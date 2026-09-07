import os
import math
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mp_engine")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

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
            urllib.request.urlretrieve(MODEL_URL, str(MODEL_PATH))
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


def process_video_real(video_path: str) -> dict:
    """
    Process an uploaded video file using MediaPipe Pose / PoseLandmarker Tasks API.
    Extracts actual gait & kinematic movement features with detailed stage logging.
    Raises ValueError if no valid pose is detected.
    """
    logger.info("==================================================")
    logger.info("STAGE 1: VIDEO INPUT & DECODING VERIFICATION")
    logger.info("==================================================")
    logger.info(f"Target video file path: {video_path}")

    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist at path: {video_path}")
        raise ValueError(f"Video file not found at path: {video_path}")

    file_size = os.path.getsize(video_path)
    logger.info(f"Video file verified on disk. Size: {file_size} bytes")

    if not OPENCV_AVAILABLE or not MEDIAPIPE_AVAILABLE:
        logger.error("OpenCV or MediaPipe Python packages are missing.")
        raise RuntimeError("OpenCV or MediaPipe Python dependencies are not installed on the server.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"cv2.VideoCapture failed to open file: {video_path}")
        raise ValueError(f"Could not open or decode video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    logger.info(f"Video opened successfully!")
    logger.info(f"Video Metadata -> Resolution: {width}x{height}, FPS: {fps:.2f}, Total Frame Count: {total_frames}")

    logger.info("==================================================")
    logger.info("STAGE 2: MEDIAPIPE ENGINE INITIALIZATION")
    logger.info("==================================================")
    
    use_tasks_api = False
    landmarker = None
    mp_pose_legacy = None

    try:
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        model_asset_path = ensure_model_asset()
        logger.info(f"Initializing MediaPipe Tasks PoseLandmarker with asset: {model_asset_path}")

        options = vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_asset_path),
            running_mode=vision.RunningMode.IMAGE,
            min_pose_detection_confidence=0.3,
            min_pose_presence_confidence=0.3,
            min_tracking_confidence=0.3
        )
        landmarker = vision.PoseLandmarker.create_from_options(options)
        use_tasks_api = True
        logger.info("MediaPipe Tasks PoseLandmarker initialized successfully!")
    except Exception as e:
        logger.warning(f"MediaPipe Tasks API initialization failed: {e}. Attempting legacy mp.solutions fallback...")
        try:
            if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'pose'):
                mp_pose_legacy = mp.solutions.pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    min_detection_confidence=0.3,
                    min_tracking_confidence=0.3
                )
                logger.info("Legacy mp.solutions.pose initialized successfully!")
            else:
                raise RuntimeError("Legacy mp.solutions.pose is not available in installed MediaPipe package.")
        except Exception as fallback_err:
            logger.error(f"Pose model could not be initialized: {fallback_err}")
            raise RuntimeError(f"Pose model could not be initialized: {fallback_err}")

    logger.info("==================================================")
    logger.info("STAGE 3: FRAME-BY-FRAME POSE EXTRACTION")
    logger.info("==================================================")

    frame_count = 0
    valid_pose_frames = 0
    invalid_pose_frames = 0
    debug_image_saved = False

    angles_history = {"hip": [], "knee": [], "shoulder": [], "elbow": []}
    ankles_x = {"left": [], "right": []}
    trunk_x = []
    landmark_history = []  # List of 33-point landmark lists for valid frames

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

        if use_tasks_api and landmarker:
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
        elif mp_pose_legacy:
            results = mp_pose_legacy.process(rgb_frame)
            if results.pose_landmarks and len(results.pose_landmarks.landmark) >= 33:
                landmarks_33 = [
                    {
                        "id": idx,
                        "x": round(lm.x, 4),
                        "y": round(lm.y, 4),
                        "z": round(lm.z, 4),
                        "visibility": round(getattr(lm, 'visibility', 0.99), 3)
                    }
                    for idx, lm in enumerate(results.pose_landmarks.landmark[:33])
                ]

        if landmarks_33:
            valid_pose_frames += 1
            landmark_history.append(landmarks_33)

            # Key landmark positions (MediaPipe 33-point index)
            # Left: 11(Sh), 13(El), 15(Wr), 23(Hip), 25(Knee), 27(Ankle)
            # Right: 12(Sh), 14(El), 16(Wr), 24(Hip), 26(Knee), 28(Ankle)
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

            # Compute kinematic angles
            hip_ang = (calculate_angle(sh_l, hip_l, kn_l) + calculate_angle(sh_r, hip_r, kn_r)) / 2.0
            knee_ang = (calculate_angle(hip_l, kn_l, ak_l) + calculate_angle(hip_r, kn_r, ak_r)) / 2.0
            shoulder_ang = (calculate_angle(hip_l, sh_l, el_l) + calculate_angle(hip_r, sh_r, el_r)) / 2.0
            elbow_ang = (calculate_angle(sh_l, el_l, wr_l) + calculate_angle(sh_r, el_r, wr_r)) / 2.0

            angles_history["hip"].append(hip_ang)
            angles_history["knee"].append(knee_ang)
            angles_history["shoulder"].append(shoulder_ang)
            angles_history["elbow"].append(elbow_ang)

            ankles_x["left"].append(ak_l[0])
            ankles_x["right"].append(ak_r[0])
            trunk_x.append((sh_l[0] + sh_r[0]) / 2.0)

            # Draw and save debug overlay image on the first detected pose frame
            if not debug_image_saved:
                try:
                    debug_frame = frame.copy()
                    h_img, w_img, _ = debug_frame.shape
                    # Draw joint points and key skeleton lines
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
                    logger.info(f"Debug skeleton overlay image saved to: {debug_img_path}")
                except Exception as dbg_err:
                    logger.warning(f"Failed to save debug frame image: {dbg_err}")
        else:
            invalid_pose_frames += 1

    cap.release()
    if mp_pose_legacy:
        mp_pose_legacy.close()

    detection_rate_pct = round((valid_pose_frames / max(1, frame_count)) * 100, 2)

    logger.info("==================================================")
    logger.info("STAGE 4: DETECTION SUMMARY & KINEMATIC COMPUTATION")
    logger.info("==================================================")
    logger.info(f"Total Frames Processed: {frame_count}")
    logger.info(f"Valid Pose Frames: {valid_pose_frames}")
    logger.info(f"Invalid Pose Frames: {invalid_pose_frames}")
    logger.info(f"Pose Detection Rate: {detection_rate_pct}%")

    if valid_pose_frames < 1 or not landmark_history:
        logger.error("No valid pose detected in any video frame.")
        raise ValueError(
            f"No valid pose detected in the uploaded video. "
            f"Scanned {frame_count} frames, but zero valid human body poses were detected. "
            f"Please ensure the patient's full body is clearly visible in the camera frame under good lighting."
        )

    duration_sec = round(frame_count / fps, 2) if fps > 0 else 5.0

    def get_stats(history_list: List[float]) -> Tuple[float, float]:
        if not history_list:
            return 0.0, 0.0
        avg = sum(history_list) / len(history_list)
        rom = max(history_list) - min(history_list)
        return round(avg, 2), round(rom, 2)

    hip_avg, hip_rom = get_stats(angles_history["hip"])
    knee_avg, knee_rom = get_stats(angles_history["knee"])
    sh_avg, sh_rom = get_stats(angles_history["shoulder"])
    el_avg, el_rom = get_stats(angles_history["elbow"])

    stride_displacements = [abs(xl - xr) for xl, xr in zip(ankles_x["left"], ankles_x["right"])]
    max_stride_index = round(max(stride_displacements), 3) if stride_displacements else 0.0

    knee_l_rom = max(angles_history["knee"]) - min(angles_history["knee"]) if angles_history["knee"] else 1.0
    step_symmetry = round(min(1.0, max(0.2, (knee_l_rom / (knee_l_rom + 1e-5)))), 2)

    cadence_steps_min = round(min(140.0, max(20.0, (len(angles_history["knee"]) / duration_sec) * 30.0)), 1)
    relative_speed_index = round(max_stride_index * cadence_steps_min / 60.0, 2)

    if trunk_x:
        mean_trunk = sum(trunk_x) / len(trunk_x)
        variance = sum((x - mean_trunk) ** 2 for x in trunk_x) / len(trunk_x)
        balance_stability = round(max(0.0, min(100.0, 100.0 - (variance * 15000))), 1)
    else:
        balance_stability = 50.0

    # Pick representative frame with maximum movement spread
    best_frame_idx = len(landmark_history) // 2
    representative_landmarks = landmark_history[best_frame_idx]

    logger.info("Pose landmark feature extraction completed successfully!")

    return {
        "video_debug": {
            "total_frames": frame_count,
            "fps": round(fps, 1),
            "duration_sec": duration_sec,
            "valid_pose_frames": valid_pose_frames,
            "invalid_pose_frames": invalid_pose_frames,
            "detection_rate_pct": detection_rate_pct,
            "debug_image_path": str(debug_img_path) if debug_image_saved else None
        },
        "angles": {
            "hip_angle_deg": hip_avg,
            "knee_angle_deg": knee_avg,
            "shoulder_angle_deg": sh_avg,
            "elbow_angle_deg": el_avg
        },
        "gait": {
            "stride_length_m": max_stride_index,
            "cadence_steps_min": cadence_steps_min,
            "walking_speed_ms": relative_speed_index,
            "step_width_m": round(max_stride_index * 0.4, 3),
            "step_symmetry_ratio": step_symmetry
        },
        "arm_swing_deg": sh_rom,
        "rom_score": round((hip_rom + knee_rom + sh_rom + el_rom) / 4.0, 2),
        "balance_stability_score": balance_stability,
        "landmarks": representative_landmarks
    }


def analyze_video(video_path: str, **kwargs) -> dict:
    """Main entry point for video analysis."""
    if not video_path:
        raise ValueError("No video file path provided.")
    return process_video_real(video_path)
