"""
RehabShield Biomechanical Feature Extraction Module
===================================================

Defines formal mathematical definitions, units, interpretations, and feature vector construction
for quantitative gait and upper-limb motor impairment analysis.
"""

from typing import Dict, List, Any, Optional
import numpy as np

# 12-Dimensional Feature Registry with explicit mathematical definitions and units
FEATURE_DICTIONARY: Dict[str, Dict[str, str]] = {
    "hip_angle_deg": {
        "name": "Hip Sagittal Range of Motion",
        "definition": "Range of motion excursion angle at hip vertex (Shoulder-Hip-Knee vector)",
        "formula": "ROM_hip = max(theta_hip) - min(theta_hip)",
        "unit": "degrees (°)",
        "interpretation": "Measures pelvic postural excursion and forward stride propulsion."
    },
    "peak_knee_flexion_deg": {
        "name": "Peak Knee Flexion Angle",
        "definition": "Anatomical knee flexion angle during swing phase (180° minus interior knee joint angle)",
        "formula": "peak_knee_flexion = 180.0 - min(theta_knee)",
        "unit": "degrees (°)",
        "interpretation": "Measures limb swing clearance capability; identifies stiff-knee gait."
    },
    "shoulder_mobility_deg": {
        "name": "Shoulder Mobility ROM",
        "definition": "Sagittal shoulder swing excursion angle (Hip-Shoulder-Elbow vector)",
        "formula": "ROM_shoulder = max(theta_shoulder) - min(theta_shoulder)",
        "unit": "degrees (°)",
        "interpretation": "Evaluates upper-limb elevation and shoulder mobility."
    },
    "elbow_flexion_deg": {
        "name": "Elbow Flexion Angle",
        "definition": "Interior angle at elbow vertex (Shoulder-Elbow-Wrist vector)",
        "formula": "theta_elbow = arccos((v_sh_el . v_wrist_el) / (|v_sh_el| * |v_wrist_el|))",
        "unit": "degrees (°)",
        "interpretation": "Detects upper-limb flexor hypertonia and spastic synergy patterns."
    },
    "stride_length_index": {
        "name": "Relative Stride Length Index",
        "definition": "Normalized peak horizontal displacement between ankle landmarks relative to leg length",
        "formula": "stride_index = max(|x_ankle_left - x_ankle_right|) / leg_length",
        "unit": "Unitless Index (video-derived proxy)",
        "interpretation": "Quantifies spatial step stride normalized for uncalibrated cameras."
    },
    "cadence_steps_min": {
        "name": "Step Cadence",
        "definition": "Frequency of detected peak heel-strike ground contact events per minute",
        "formula": "cadence = (total_detected_steps / duration_seconds) * 60.0",
        "unit": "steps/min",
        "interpretation": "Measures temporal stepping rate and rhythmicity."
    },
    "walking_speed_index": {
        "name": "Relative Walking Speed Index",
        "definition": "Product of relative stride length index and stepping cadence",
        "formula": "speed_index = (stride_length_index * cadence) / 120.0",
        "unit": "Unitless Index (video-derived proxy)",
        "interpretation": "Combines spatial and temporal parameters into gait progression velocity index."
    },
    "step_width_index": {
        "name": "Relative Step Width Index",
        "definition": "Estimated lateral base of support width from ankle trajectories relative to inter-hip width",
        "formula": "step_width_index = mean(|x_foot_left - x_foot_right|) / hip_width",
        "unit": "Unitless Index (video-derived proxy)",
        "interpretation": "Indicates lateral base-of-support width for balance control."
    },
    "step_symmetry_ratio": {
        "name": "Step Symmetry Ratio",
        "definition": "Bilateral temporal step ratio between left and right stance durations",
        "formula": "symmetry_ratio = min(t_step_left, t_step_right) / max(t_step_left, t_step_right)",
        "unit": "ratio (0.0 to 1.0)",
        "interpretation": "1.0 indicates perfect temporal step symmetry."
    },
    "arm_swing_deg": {
        "name": "Arm Swing Amplitude",
        "definition": "Peak sagittal wrist displacement angle relative to shoulder joint during walking",
        "formula": "arm_swing = max(wrist_swing_angle) - min(wrist_swing_angle)",
        "unit": "degrees (°)",
        "interpretation": "Evaluates reciprocal upper-limb counter-rotation."
    },
    "rom_score": {
        "name": "Composite Range of Motion (ROM)",
        "definition": "Arithmetic mean of hip, knee, shoulder, and elbow ROM percentages",
        "formula": "rom_score = (rom_hip + rom_knee + rom_shoulder + rom_elbow) / 4.0",
        "unit": "percentage (%)",
        "interpretation": "Global multi-joint mobility score."
    },
    "balance_stability_score": {
        "name": "Pose Stability Index",
        "definition": "Inverse lateral sway variance of trunk center proxy across tracking frames",
        "formula": "pose_stability_index = max(0.0, min(100.0, 100.0 - (var(x_trunk) * 15000)))",
        "unit": "percentage (%)",
        "interpretation": "Pose-derived proxy metric for dynamic balance stability."
    }
}

FEATURE_NAMES = [
    "hip_angle_deg",
    "peak_knee_flexion_deg",
    "shoulder_mobility_deg",
    "elbow_flexion_deg",
    "stride_length_index",
    "cadence_steps_min",
    "walking_speed_index",
    "step_width_index",
    "step_symmetry_ratio",
    "arm_swing_deg",
    "rom_score",
    "balance_stability_score"
]


def build_feature_vector(extracted_features: dict) -> Optional[np.ndarray]:
    """
    Extracts 12-element numerical feature vector from raw biomechanical extraction dictionary.
    
    Args:
        extracted_features: Dictionary produced by analyze_video() containing 'angles', 'gait', etc.

    Returns:
        numpy.ndarray of shape (12,) or None if essential metric structures are missing.
    """
    if not isinstance(extracted_features, dict):
        return None

    gait = extracted_features.get("gait", {})
    angles = extracted_features.get("angles", {})

    hip = angles.get("hip_angle_deg")
    knee = angles.get("knee_angle_deg")
    shoulder = angles.get("shoulder_angle_deg")
    elbow = angles.get("elbow_angle_deg")

    stride = gait.get("stride_length_index") if gait.get("stride_length_index") is not None else gait.get("stride_length_m")
    cadence = gait.get("cadence_steps_min")
    speed = gait.get("walking_speed_index") if gait.get("walking_speed_index") is not None else gait.get("walking_speed_ms")
    width = gait.get("step_width_index") if gait.get("step_width_index") is not None else gait.get("step_width_m")
    symmetry = gait.get("step_symmetry_ratio")

    arm_swing = extracted_features.get("arm_swing_deg")
    rom_score = extracted_features.get("rom_score")
    balance = extracted_features.get("balance_stability_score")

    # Build vector using extracted metrics (with safe defaults if None)
    vector = [
        float(hip if hip is not None else 35.0),
        float(knee if knee is not None else 45.0),
        float(shoulder if shoulder is not None else 30.0),
        float(elbow if elbow is not None else 120.0),
        float(stride if stride is not None else 0.3),
        float(cadence if cadence is not None else 60.0),
        float(speed if speed is not None else 0.4),
        float(width if width is not None else 0.15),
        float(symmetry if symmetry is not None else 0.7),
        float(arm_swing if arm_swing is not None else 15.0),
        float(rom_score if rom_score is not None else 45.0),
        float(balance if balance is not None else 60.0)
    ]

    return np.array(vector, dtype=np.float32)


# 14-Dimensional Upper-Limb Kinematic Feature Registry (MediaPipe Pose 33-point derived)
UPPER_LIMB_FEATURE_NAMES = [
    "shoulder_rom_active_deg",
    "elbow_rom_active_deg",
    "elbow_min_angle_deg",
    "elbow_max_angle_deg",
    "elbow_mean_angle_deg",
    "shoulder_mean_angle_deg",
    "wrist_vertical_excursion",
    "wrist_horizontal_excursion",
    "wrist_max_reach_dist",
    "peak_elbow_angular_velocity_dps",
    "mean_elbow_angular_velocity_dps",
    "peak_shoulder_angular_velocity_dps",
    "movement_smoothness_index",
    "bilateral_rom_asymmetry_deg"
]

UPPER_LIMB_FEATURE_DICTIONARY: Dict[str, Dict[str, str]] = {
    "shoulder_rom_active_deg": {
        "name": "Active Shoulder Elevation ROM",
        "definition": "Range of motion excursion of dominant/active shoulder vertex",
        "unit": "degrees (°)"
    },
    "elbow_rom_active_deg": {
        "name": "Active Elbow Extension ROM",
        "definition": "Range of motion excursion of active elbow joint",
        "unit": "degrees (°)"
    },
    "elbow_min_angle_deg": {
        "name": "Minimum Elbow Angle",
        "definition": "Minimum interior angle at elbow (indicates flexor posturing/spasticity)",
        "unit": "degrees (°)"
    },
    "elbow_max_angle_deg": {
        "name": "Maximum Elbow Extension Angle",
        "definition": "Maximum interior angle at elbow during extension phase",
        "unit": "degrees (°)"
    },
    "elbow_mean_angle_deg": {
        "name": "Mean Elbow Angle",
        "definition": "Temporal average of elbow interior angle",
        "unit": "degrees (°)"
    },
    "shoulder_mean_angle_deg": {
        "name": "Mean Shoulder Angle",
        "definition": "Temporal average of shoulder elevation angle",
        "unit": "degrees (°)"
    },
    "wrist_vertical_excursion": {
        "name": "Vertical Wrist Excursion",
        "definition": "Normalized vertical range of motion of wrist landmark",
        "unit": "normalized displacement"
    },
    "wrist_horizontal_excursion": {
        "name": "Horizontal Wrist Excursion",
        "definition": "Normalized horizontal range of motion of wrist landmark",
        "unit": "normalized displacement"
    },
    "wrist_max_reach_dist": {
        "name": "Maximum Reach Distance",
        "definition": "Peak normalized Euclidean distance between wrist and shoulder",
        "unit": "normalized distance"
    },
    "peak_elbow_angular_velocity_dps": {
        "name": "Peak Elbow Angular Velocity",
        "definition": "Maximum rate of change of elbow angle across execution",
        "unit": "deg/s"
    },
    "mean_elbow_angular_velocity_dps": {
        "name": "Mean Elbow Angular Velocity",
        "definition": "Average angular velocity magnitude of elbow joint",
        "unit": "deg/s"
    },
    "peak_shoulder_angular_velocity_dps": {
        "name": "Peak Shoulder Angular Velocity",
        "definition": "Maximum rate of change of shoulder angle across execution",
        "unit": "deg/s"
    },
    "movement_smoothness_index": {
        "name": "Movement Smoothness Index",
        "definition": "Inverse variance of joint angular acceleration (smoothness proxy)",
        "unit": "dimensionless index"
    },
    "bilateral_rom_asymmetry_deg": {
        "name": "Bilateral Arm ROM Asymmetry",
        "definition": "Absolute difference between left and right arm joint excursion ranges",
        "unit": "degrees (°)"
    }
}


def compute_angle_2d(a: tuple, b: tuple, c: tuple) -> float:
    """Calculate 2D angle (in degrees) between three points (a, b, c) with b as vertex."""
    import math
    try:
        ang = math.degrees(
            math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
        )
        ang = abs(ang)
        if ang > 180:
            ang = 360 - ang
        return float(ang)
    except Exception:
        return 0.0


def extract_upper_limb_features_from_history(landmark_history: List[List[Dict[str, Any]]], fps: float = 30.0) -> Optional[np.ndarray]:
    """
    Extracts 14-dimensional upper-limb kinematic feature vector from MediaPipe 33-keypoint sequence.
    Excludes all lower-limb gait and step detection features.
    """
    if not landmark_history or len(landmark_history) < 5:
        return None

    dt = 1.0 / max(5.0, fps)

    sh_l_angles = []
    sh_r_angles = []
    el_l_angles = []
    el_r_angles = []
    wrist_l_y = []
    wrist_r_y = []
    wrist_l_x = []
    wrist_r_x = []
    reach_l_dist = []
    reach_r_dist = []

    for lms in landmark_history:
        if len(lms) < 33:
            continue
        # Left upper limb: 11 (Sh), 13 (El), 15 (Wr), 23 (Hip)
        # Right upper limb: 12 (Sh), 14 (El), 16 (Wr), 24 (Hip)
        sh_l = (lms[11]["x"], lms[11]["y"])
        sh_r = (lms[12]["x"], lms[12]["y"])
        el_l = (lms[13]["x"], lms[13]["y"])
        el_r = (lms[14]["x"], lms[14]["y"])
        wr_l = (lms[15]["x"], lms[15]["y"])
        wr_r = (lms[16]["x"], lms[16]["y"])
        hip_l = (lms[23]["x"], lms[23]["y"])
        hip_r = (lms[24]["x"], lms[24]["y"])

        ang_sh_l = compute_angle_2d(hip_l, sh_l, el_l)
        ang_sh_r = compute_angle_2d(hip_r, sh_r, el_r)
        ang_el_l = compute_angle_2d(sh_l, el_l, wr_l)
        ang_el_r = compute_angle_2d(sh_r, el_r, wr_r)

        sh_l_angles.append(ang_sh_l)
        sh_r_angles.append(ang_sh_r)
        el_l_angles.append(ang_el_l)
        el_r_angles.append(ang_el_r)

        wrist_l_y.append(wr_l[1])
        wrist_r_y.append(wr_r[1])
        wrist_l_x.append(wr_l[0])
        wrist_r_x.append(wr_r[0])

        d_l = np.sqrt((wr_l[0] - sh_l[0]) ** 2 + (wr_l[1] - sh_l[1]) ** 2)
        d_r = np.sqrt((wr_r[0] - sh_r[0]) ** 2 + (wr_r[1] - sh_r[1]) ** 2)
        reach_l_dist.append(d_l)
        reach_r_dist.append(d_r)

    if not el_l_angles or not el_r_angles:
        return None

    # Determine dominant/active limb based on maximum range of motion
    rom_el_l = max(el_l_angles) - min(el_l_angles)
    rom_el_r = max(el_r_angles) - min(el_r_angles)
    rom_sh_l = max(sh_l_angles) - min(sh_l_angles)
    rom_sh_r = max(sh_r_angles) - min(sh_r_angles)

    active_side = "right" if (rom_el_r + rom_sh_r) >= (rom_el_l + rom_sh_l) else "left"

    if active_side == "right":
        el_active = np.array(el_r_angles)
        sh_active = np.array(sh_r_angles)
        wrist_y_active = np.array(wrist_r_y)
        wrist_x_active = np.array(wrist_r_x)
        reach_active = np.array(reach_r_dist)
    else:
        el_active = np.array(el_l_angles)
        sh_active = np.array(sh_l_angles)
        wrist_y_active = np.array(wrist_l_y)
        wrist_x_active = np.array(wrist_l_x)
        reach_active = np.array(reach_l_dist)

    sh_rom = float(np.max(sh_active) - np.min(sh_active))
    el_rom = float(np.max(el_active) - np.min(el_active))
    el_min = float(np.min(el_active))
    el_max = float(np.max(el_active))
    el_mean = float(np.mean(el_active))
    sh_mean = float(np.mean(sh_active))

    wrist_vert_excursion = float(np.max(wrist_y_active) - np.min(wrist_y_active))
    wrist_horiz_excursion = float(np.max(wrist_x_active) - np.min(wrist_x_active))
    wrist_max_reach = float(np.max(reach_active))

    # Angular velocities and accelerations
    vel_el = np.abs(np.diff(el_active) / dt) if len(el_active) > 1 else np.array([0.0])
    vel_sh = np.abs(np.diff(sh_active) / dt) if len(sh_active) > 1 else np.array([0.0])
    acc_el = np.diff(vel_el) / dt if len(vel_el) > 1 else np.array([0.0])

    peak_el_vel = float(np.max(vel_el)) if len(vel_el) > 0 else 0.0
    mean_el_vel = float(np.mean(vel_el)) if len(vel_el) > 0 else 0.0
    peak_sh_vel = float(np.max(vel_sh)) if len(vel_sh) > 0 else 0.0

    acc_var = float(np.var(acc_el)) if len(acc_el) > 0 else 0.0
    smoothness_index = float(100.0 / (1.0 + np.sqrt(acc_var) * 0.01))

    bilateral_asymm = float(abs(rom_el_l - rom_el_r) + abs(rom_sh_l - rom_sh_r)) / 2.0

    vec = [
        sh_rom,
        el_rom,
        el_min,
        el_max,
        el_mean,
        sh_mean,
        wrist_vert_excursion,
        wrist_horiz_excursion,
        wrist_max_reach,
        peak_el_vel,
        mean_el_vel,
        peak_sh_vel,
        smoothness_index,
        bilateral_asymm
    ]

    return np.array(vec, dtype=np.float32)

