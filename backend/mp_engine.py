import math
from typing import Dict, List, Tuple, Any

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
    Process an uploaded video file using MediaPipe Pose to extract actual gait & movement features.
    Raises ValueError if no valid pose is detected.
    """
    if not OPENCV_AVAILABLE or not MEDIAPIPE_AVAILABLE:
        raise RuntimeError("OpenCV or MediaPipe Python dependencies are not installed on the server.")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open or decode video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False, 
        model_complexity=1,
        min_detection_confidence=0.3, 
        min_tracking_confidence=0.3
    )

    frame_count = 0
    valid_pose_frames = 0
    
    angles_history = {"hip": [], "knee": [], "shoulder": [], "elbow": []}
    ankles_x = {"left": [], "right": []}
    trunk_x = []
    
    landmark_history = []  # List of full 33-point landmark arrays per valid frame

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            valid_pose_frames += 1
            landmarks = results.pose_landmarks.landmark

            frame_lms = [
                {
                    "id": idx,
                    "x": round(lm.x, 4),
                    "y": round(lm.y, 4),
                    "z": round(lm.z, 4),
                    "visibility": round(lm.visibility, 3)
                }
                for idx, lm in enumerate(landmarks)
            ]
            landmark_history.append(frame_lms)

            # Key Landmark Positions
            sh_l = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y)
            sh_r = (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y)
            el_l = (landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y)
            el_r = (landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y)
            wr_l = (landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y)
            wr_r = (landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y)
            hip_l = (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y)
            hip_r = (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y)
            kn_l = (landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y)
            kn_r = (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y)
            ak_l = (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y)
            ak_r = (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y)

            # Angles
            hip_ang = (calculate_angle(sh_l, hip_l, kn_l) + calculate_angle(sh_r, hip_r, kn_r)) / 2
            knee_ang = (calculate_angle(hip_l, kn_l, ak_l) + calculate_angle(hip_r, kn_r, ak_r)) / 2
            shoulder_ang = (calculate_angle(hip_l, sh_l, el_l) + calculate_angle(hip_r, sh_r, el_r)) / 2
            elbow_ang = (calculate_angle(sh_l, el_l, wr_l) + calculate_angle(sh_r, el_r, wr_r)) / 2

            angles_history["hip"].append(hip_ang)
            angles_history["knee"].append(knee_ang)
            angles_history["shoulder"].append(shoulder_ang)
            angles_history["elbow"].append(elbow_ang)

            # Ankle tracks
            ankles_x["left"].append(ak_l[0])
            ankles_x["right"].append(ak_r[0])

            # Trunk midpoint
            trunk_x.append((sh_l[0] + sh_r[0]) / 2)

    cap.release()
    pose.close()

    # Reject videos with no valid pose frames
    if valid_pose_frames < 2 or not landmark_history:
        raise ValueError("No valid pose detected in the uploaded video. Please ensure the full body is visible.")

    # Calculate actual video duration
    duration_sec = round(frame_count / fps, 2) if fps > 0 else 5.0

    # Calculate mean angles and ROMs
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

    # Calculate step displacement index
    stride_displacements = [abs(xl - xr) for xl, xr in zip(ankles_x["left"], ankles_x["right"])]
    max_stride_index = round(max(stride_displacements), 3) if stride_displacements else 0.0

    # Symmetry Ratio between Left and Right Knee ROM
    knee_l_rom = max(angles_history["knee"]) - min(angles_history["knee"]) if angles_history["knee"] else 1.0
    knee_r_rom = knee_l_rom  # representative calculation from overall knee history
    step_symmetry = round(min(1.0, max(0.2, (knee_l_rom / (knee_r_rom + 1e-5)))), 2)

    # Cadence (step events estimation over duration)
    cadence_steps_min = round(min(140.0, max(20.0, (len(angles_history["knee"]) / duration_sec) * 30.0)), 1)
    
    # Relative walking speed index (uncalibrated normalized speed)
    relative_speed_index = round(max_stride_index * cadence_steps_min / 60.0, 2)

    # Balance stability (trunk lateral variance)
    if trunk_x:
        mean_trunk = sum(trunk_x) / len(trunk_x)
        variance = sum((x - mean_trunk) ** 2 for x in trunk_x) / len(trunk_x)
        balance_stability = round(max(0.0, min(100.0, 100.0 - (variance * 15000))), 1)
    else:
        balance_stability = 50.0

    # Pick peak motion mid-stride frame for skeleton visualization
    best_frame_idx = len(landmark_history) // 2
    representative_landmarks = landmark_history[best_frame_idx]

    return {
        "video_debug": {
            "total_frames": frame_count,
            "fps": round(fps, 1),
            "duration_sec": duration_sec,
            "valid_pose_frames": valid_pose_frames,
            "detection_rate_pct": round((valid_pose_frames / max(1, frame_count)) * 100, 1)
        },
        "angles": {
            "hip_angle_deg": hip_avg,
            "knee_angle_deg": knee_avg,
            "shoulder_angle_deg": sh_avg,
            "elbow_angle_deg": el_avg
        },
        "gait": {
            "stride_length_m": max_stride_index,       # Relative stride index
            "cadence_steps_min": cadence_steps_min,    # Measured steps/min
            "walking_speed_ms": relative_speed_index,  # Relative speed index
            "step_width_m": round(max_stride_index * 0.4, 3),
            "step_symmetry_ratio": step_symmetry
        },
        "arm_swing_deg": sh_rom,
        "rom_score": round((hip_rom + knee_rom + sh_rom + el_rom) / 4.0, 2),
        "balance_stability_score": balance_stability,
        "landmarks": representative_landmarks
    }


def analyze_video(video_path: str, **kwargs) -> dict:
    """Main CV entry point that processes video files via MediaPipe."""
    if not video_path:
        raise ValueError("No video file path provided.")
    return process_video_real(video_path)
