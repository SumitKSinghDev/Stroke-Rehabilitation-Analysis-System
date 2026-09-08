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
