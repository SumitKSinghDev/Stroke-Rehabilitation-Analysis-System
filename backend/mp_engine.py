import os
import math
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mp_engine")

OPENCV_ERR = ""
MEDIAPIPE_ERR = ""

try:
    import cv2
    OPENCV_AVAILABLE = True
except Exception as _e:
    cv2 = None
    OPENCV_AVAILABLE = False
    OPENCV_ERR = str(_e)

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except Exception as _e:
    mp = None
    MEDIAPIPE_AVAILABLE = False
    MEDIAPIPE_ERR = str(_e)

# Path to local MediaPipe Tasks model asset
MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "pose_landmarker_full.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"

def ensure_model_asset() -> str:
    """Ensure the MediaPipe PoseLandmarker model file exists, downloading if necessary."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if not MODEL_PATH.exists() or MODEL_PATH.stat().st_size < 1000000:
        logger.info(f"Downloading MediaPipe PoseLandmarker model asset from {MODEL_URL}...")
        try:
            req = urllib.request.Request(
                MODEL_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            import ssl
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(req, context=context) as response, open(MODEL_PATH, "wb") as out_file:
                out_file.write(response.read())
            logger.info(f"Model asset downloaded successfully to {MODEL_PATH} ({MODEL_PATH.stat().st_size} bytes)")
        except Exception as e:
            logger.error(f"Failed to download MediaPipe model asset: {e}")
            raise RuntimeError(f"Pose model asset could not be downloaded/initialized: {e}")
    return str(MODEL_PATH)


def calculate_angle(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """Calculate 2D angle (in degrees) between three points (a, b, c) with b as vertex."""
    try:
        ang = math.degrees(
            math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
        )
        ang = abs(ang)
        if ang > 180:
            ang = 360 - ang
        return round(ang, 2)
    except Exception:
        return 0.0


def process_video_real(video_path: str, movement_type: str = "general") -> dict:
    """
    Process an uploaded video file using MediaPipe Pose / PoseLandmarker Tasks API.
    Separates general/gait processing from upper-limb processing to prevent misapplying step-detection algorithms.
    Raises ValueError if no valid pose is detected.
    """
    logger.info("==================================================")
    logger.info(f"STAGE 1: VIDEO INPUT VERIFICATION (Movement Type: {movement_type})")
    logger.info("==================================================")
    logger.info(f"Target video file path: {video_path}")

    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist at path: {video_path}")
        raise ValueError(f"Video file not found at path: {video_path}")

    file_size = os.path.getsize(video_path)
    if file_size == 0:
        logger.error(f"Uploaded video file is empty (0 bytes): {video_path}")
        raise ValueError("Unable to open the uploaded video. File size is 0 bytes.")

    logger.info(f"Video file verified on disk. Size: {file_size} bytes")

    if not OPENCV_AVAILABLE or cv2 is None:
        logger.error(f"OpenCV Python dependency is missing: {OPENCV_ERR}")
        raise RuntimeError(f"OpenCV Python package is not installed on the server: {OPENCV_ERR}")

    if not MEDIAPIPE_AVAILABLE or mp is None:
        logger.error(f"MediaPipe Python dependency is missing: {MEDIAPIPE_ERR}")
        raise RuntimeError(f"MediaPipe Python package is not installed on the server: {MEDIAPIPE_ERR}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"cv2.VideoCapture failed to open file: {video_path}")
        raise ValueError("Unable to open the uploaded video.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    logger.info(f"Video opened successfully! Resolution: {width}x{height}, FPS: {fps:.2f}, Frames: {total_frames}")

    landmarker = None
    try:
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        model_asset_path = ensure_model_asset()
        options = vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_asset_path),
            running_mode=vision.RunningMode.IMAGE,
            min_pose_detection_confidence=0.3,
            min_pose_presence_confidence=0.3,
            min_tracking_confidence=0.3
        )
        landmarker = vision.PoseLandmarker.create_from_options(options)
    except Exception as e:
        logger.error(f"MediaPipe Tasks API initialization failed: {e}")
        raise RuntimeError(f"Pose model could not be initialized: {e}")

    frame_count = 0
    valid_pose_frames = 0
    invalid_pose_frames = 0
    debug_image_saved = False

    angles_history = {"hip": [], "knee": [], "shoulder": [], "elbow": []}
    ankles_x = {"left": [], "right": []}
    ankles_y = {"left": [], "right": []}
    wrists_x = {"left": [], "right": []}
    wrists_y = {"left": [], "right": []}
    trunk_x = []
    landmark_history = []

    uploads_dir = Path(__file__).parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    debug_img_path = uploads_dir / "debug_pose.jpg"

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        landmarks_33 = []

        if landmarker:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = landmarker.detect(mp_image)
            if detection_result.pose_landmarks and len(detection_result.pose_landmarks) > 0:
                raw_lms = detection_result.pose_landmarks[0]
                if len(raw_lms) >= 33:
                    landmarks_33 = [
                        {
                            "id": idx,
                            "x": round(lm.x, 4),
                            "y": round(lm.y, 4),
                            "z": round(lm.z, 4),
                            "visibility": round(getattr(lm, 'visibility', 0.99), 3)
                        }
                        for idx, lm in enumerate(raw_lms[:33])
                    ]

        if landmarks_33:
            valid_pose_frames += 1
            landmark_history.append(landmarks_33)

            sh_l = (landmarks_33[11]["x"], landmarks_33[11]["y"])
            sh_r = (landmarks_33[12]["x"], landmarks_33[12]["y"])
            el_l = (landmarks_33[13]["x"], landmarks_33[13]["y"])
            el_r = (landmarks_33[14]["x"], landmarks_33[14]["y"])
            wr_l = (landmarks_33[15]["x"], landmarks_33[15]["y"])
            wr_r = (landmarks_33[16]["x"], landmarks_33[16]["y"])
            hip_l = (landmarks_33[23]["x"], landmarks_33[23]["y"])
            hip_r = (landmarks_33[24]["x"], landmarks_33[24]["y"])
            kn_l = (landmarks_33[25]["x"], landmarks_33[25]["y"])
            kn_r = (landmarks_33[26]["x"], landmarks_33[26]["y"])
            ak_l = (landmarks_33[27]["x"], landmarks_33[27]["y"])
            ak_r = (landmarks_33[28]["x"], landmarks_33[28]["y"])

            hip_ang_l = calculate_angle(sh_l, hip_l, kn_l)
            hip_ang_r = calculate_angle(sh_r, hip_r, kn_r)
            knee_ang_l = calculate_angle(hip_l, kn_l, ak_l)
            knee_ang_r = calculate_angle(hip_r, kn_r, ak_r)
            sh_ang_l = calculate_angle(hip_l, sh_l, el_l)
            sh_ang_r = calculate_angle(hip_r, sh_r, el_r)
            el_ang_l = calculate_angle(sh_l, el_l, wr_l)
            el_ang_r = calculate_angle(sh_r, el_r, wr_r)

            angles_history["hip"].append((hip_ang_l + hip_ang_r) / 2.0)
            angles_history["knee"].append((knee_ang_l + knee_ang_r) / 2.0)
            angles_history["shoulder"].append((sh_ang_l + sh_ang_r) / 2.0)
            angles_history["elbow"].append((el_ang_l + el_ang_r) / 2.0)

            ankles_x["left"].append(ak_l[0])
            ankles_x["right"].append(ak_r[0])
            ankles_y["left"].append(ak_l[1])
            ankles_y["right"].append(ak_r[1])
            wrists_x["left"].append(wr_l[0])
            wrists_x["right"].append(wr_r[0])
            wrists_y["left"].append(wr_l[1])
            wrists_y["right"].append(wr_r[1])
            trunk_x.append((sh_l[0] + sh_r[0]) / 2.0)

            if not debug_image_saved:
                try:
                    debug_frame = frame.copy()
                    h_img, w_img, _ = debug_frame.shape
                    connections = [
                        (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
                        (11, 23), (12, 24), (23, 24), (23, 25), (25, 27),
                        (24, 26), (26, 28)
                    ]
                    for idx_a, idx_b in connections:
                        pt_a = (int(landmarks_33[idx_a]["x"] * w_img), int(landmarks_33[idx_a]["y"] * h_img))
                        pt_b = (int(landmarks_33[idx_b]["x"] * w_img), int(landmarks_33[idx_b]["y"] * h_img))
                        cv2.line(debug_frame, pt_a, pt_b, (0, 255, 0), 2)

                    for lm in landmarks_33:
                        cx, cy = int(lm["x"] * w_img), int(lm["y"] * h_img)
                        cv2.circle(debug_frame, (cx, cy), 4, (0, 0, 255), -1)

                    cv2.imwrite(str(debug_img_path), debug_frame)
                    debug_image_saved = True
                except Exception as dbg_err:
                    logger.warning(f"Failed to save debug frame image: {dbg_err}")
        else:
            invalid_pose_frames += 1

    cap.release()
    if hasattr(landmarker, "close"):
        try:
            landmarker.close()
        except Exception:
            pass

    detection_rate_pct = round((valid_pose_frames / max(1, frame_count)) * 100, 2)
    duration_sec = round(frame_count / fps, 2) if fps > 0 else 5.0

    if detection_rate_pct >= 90.0 and fps >= 24.0 and duration_sec >= 2.0:
        quality_status = "Excellent"
        quality_warning = None
    elif detection_rate_pct >= 75.0 and fps >= 15.0:
        quality_status = "Good"
        quality_warning = None
    elif detection_rate_pct >= 50.0:
        quality_status = "Fair"
        quality_warning = "Moderate tracking gaps detected. Interpret metrics with caution."
    else:
        quality_status = "Poor / Insufficient"
        quality_warning = "Low pose detection quality (<50% valid frames). Check lighting or camera angle."

    if valid_pose_frames < 1 or not landmark_history:
        raise ValueError("No valid pose detected in any video frame.")

    # Lower-Limb Step Processing (Only run for gait / general modes)
    total_detected_steps = 0
    left_steps = []
    right_steps = []
    cadence_steps_min = None
    step_symmetry = None

    if movement_type in ["gait", "general"]:
        def detect_heel_strikes(y_coords: List[float], fps_val: float) -> List[int]:
            if len(y_coords) < 10:
                return []
            smoothed = [(y_coords[i-1] + y_coords[i] + y_coords[i+1]) / 3.0 for i in range(1, len(y_coords) - 1)]
            min_dist = max(4, int(fps_val * 0.35))
            peaks = []
            last_peak = -min_dist
            mean_y = sum(smoothed) / len(smoothed)
            for idx in range(1, len(smoothed) - 1):
                if smoothed[idx] > smoothed[idx-1] and smoothed[idx] > smoothed[idx+1]:
                    if smoothed[idx] >= mean_y * 0.95:
                        if (idx - last_peak) >= min_dist:
                            peaks.append(idx + 1)
                            last_peak = idx
            return peaks

        left_steps = detect_heel_strikes(ankles_y["left"], fps)
        right_steps = detect_heel_strikes(ankles_y["right"], fps)
        total_detected_steps = len(left_steps) + len(right_steps)

        if total_detected_steps >= 2 and duration_sec > 0:
            cadence_steps_min = round((total_detected_steps / duration_sec) * 60.0, 1)

        if len(left_steps) > 0 and len(right_steps) > 0:
            step_symmetry = round(min(len(left_steps), len(right_steps)) / max(len(left_steps), len(right_steps)), 2)

    # Anatomical Kinematics
    raw_knee_history = angles_history["knee"]
    flexion_knee_history = [round(180.0 - k, 2) for k in raw_knee_history]
    knee_rom = round(max(raw_knee_history) - min(raw_knee_history), 2) if raw_knee_history else 0.0
    peak_knee_flexion = round(max(flexion_knee_history), 2) if flexion_knee_history else 0.0

    hip_avg = round(sum(angles_history["hip"]) / len(angles_history["hip"]), 2) if angles_history["hip"] else 0.0
    hip_rom = round(max(angles_history["hip"]) - min(angles_history["hip"]), 2) if angles_history["hip"] else 0.0

    sh_avg = round(sum(angles_history["shoulder"]) / len(angles_history["shoulder"]), 2) if angles_history["shoulder"] else 0.0
    sh_rom = round(max(angles_history["shoulder"]) - min(angles_history["shoulder"]), 2) if angles_history["shoulder"] else 0.0

    el_avg = round(sum(angles_history["elbow"]) / len(angles_history["elbow"]), 2) if angles_history["elbow"] else 0.0
    el_rom = round(max(angles_history["elbow"]) - min(angles_history["elbow"]), 2) if angles_history["elbow"] else 0.0

    stride_displacements = [abs(xl - xr) for xl, xr in zip(ankles_x["left"], ankles_x["right"])]
    max_stride_index = round(max(stride_displacements), 3) if stride_displacements else None

    relative_speed_index = round(max_stride_index * cadence_steps_min / 60.0, 2) if (max_stride_index is not None and cadence_steps_min is not None) else None

    if trunk_x:
        mean_trunk = sum(trunk_x) / len(trunk_x)
        variance = sum((x - mean_trunk) ** 2 for x in trunk_x) / len(trunk_x)
        balance_stability = round(max(0.0, min(100.0, 100.0 - (variance * 15000))), 1)
    else:
        balance_stability = None

    best_frame_idx = len(landmark_history) // 2
    representative_landmarks = landmark_history[best_frame_idx]

    video_debug_object = {
        "video_filename": os.path.basename(video_path),
        "movement_type": movement_type,
        "frame_count": frame_count,
        "fps": round(fps, 1),
        "duration_seconds": duration_sec,
        "valid_pose_frames": valid_pose_frames,
        "invalid_pose_frames": invalid_pose_frames,
        "pose_detection_rate": detection_rate_pct,
        "video_quality_status": quality_status,
        "video_quality_warning": quality_warning,
        "detected_steps": total_detected_steps,
        "left_step_events": left_steps,
        "right_step_events": right_steps,
        "knee_flexion_peak_deg": peak_knee_flexion,
        "shoulder_rom_deg": sh_rom,
        "elbow_rom_deg": el_rom,
        "debug_image_path": str(debug_img_path) if debug_image_saved else None
    }

    video_quality_object = {
        "category": quality_status,
        "score": round(detection_rate_pct, 1),
        "fps": round(fps, 1),
        "total_frames": frame_count,
        "tracked_frames": valid_pose_frames,
        "resolution": f"{width}x{height}",
        "reasons": [quality_warning] if quality_warning else []
    }

    return {
        "movement_type": movement_type,
        "video_debug": video_debug_object,
        "video_quality": video_quality_object,
        "angles": {
            "hip_angle_deg": hip_avg,
            "knee_angle_deg": peak_knee_flexion,
            "shoulder_angle_deg": sh_avg,
            "elbow_angle_deg": el_avg
        },
        "upper_limb_metrics": {
            "shoulder_rom_deg": sh_rom,
            "elbow_rom_deg": el_rom,
            "elbow_avg_deg": el_avg,
            "shoulder_avg_deg": sh_avg
        },
        "gait": {
            "stride_length_m": max_stride_index,
            "stride_length_index": max_stride_index,
            "cadence_steps_min": cadence_steps_min,
            "walking_speed_ms": relative_speed_index,
            "walking_speed_index": relative_speed_index,
            "step_width_m": round(max_stride_index * 0.4, 3) if max_stride_index is not None else None,
            "step_width_index": round(max_stride_index * 0.4, 3) if max_stride_index is not None else None,
            "step_symmetry_ratio": step_symmetry
        },
        "arm_swing_deg": sh_rom,
        "rom_score": round((hip_rom + knee_rom + sh_rom + el_rom) / 4.0, 2),
        "balance_stability_score": balance_stability,
        "landmarks": representative_landmarks
    }


def analyze_video(video_path: str, movement_type: str = "general", **kwargs) -> dict:
    """Main entry point for video analysis."""
    if not video_path:
        raise ValueError("No video file path provided.")
    return process_video_real(video_path, movement_type=movement_type)
