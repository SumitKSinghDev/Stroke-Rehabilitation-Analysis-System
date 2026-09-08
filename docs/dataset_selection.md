# Dataset Selection & Methodological Justification

## Official Project Title
**"Machine Learning-Based Gait and Upper Limb Motor Impairment Analysis for Stroke Rehabilitation"**

---

## 1. Overview & Dataset Rationale

For robust, scientifically defensible machine learning models in stroke rehabilitation research, dataset selection and cross-validation strategies must adhere strictly to biomechanical standards and avoid data leakage.

In earlier development phases, proprietary or dataset-specific formats (such as raw 25-joint Kinect arrays from TRSPD) created cross-platform coupling issues and monocular video incompatibility. In this upgraded research framework:

- **Primary ML Dataset**: **StrokeRehab Dataset** (`https://strokerehabdata.github.io/`) — Comprises 71 unique participants (51 stroke-impaired patients, 20 healthy control subjects) performing activities of daily living (ADLs) and functional movement primitives (Reach, Transport, Reposition, Stabilize, Idle), yielding 355 programmatically parsed trials.
- **Secondary Gait Reference Dataset**: **PhysioNet Multi-Camera and Multimodal Dataset for Posture and Gait Analysis** (`https://physionet.org/content/multi-gait-posture/1.0.0/`) — Used strictly for relative gait parameter reference validation (14 healthy subjects).
- **TRSPD Removal**: TRSPD has been completely removed from the project with zero legacy dependencies.

---

## 2. Benchmark Feature Mapping

The system maps 33 body coordinate keypoints into a 12-dimensional biomechanical feature vector:

| Index | Feature Symbol | Description | Units / Scale |
|---|---|---|---|
| 1 | `hip_angle_deg` | Sagittal Hip Range of Motion | Degrees (°) |
| 2 | `peak_knee_flexion_deg` | Peak Swing-Phase Knee Flexion | Degrees (°) |
| 3 | `shoulder_mobility_deg` | Sagittal Shoulder Excursion | Degrees (°) |
| 4 | `elbow_flexion_deg` | Elbow Flexion Synergy Angle | Degrees (°) |
| 5 | `stride_length_index` | Relative Stride Length Index | Unitless Index |
| 6 | `cadence_steps_min` | Temporal Stepping Cadence | Steps / min |
| 7 | `walking_speed_index` | Relative Walking Speed Index | Unitless Index |
| 8 | `step_width_index` | Base of Support Width Index | Unitless Index |
| 9 | `step_symmetry_ratio` | Bilateral Temporal Step Ratio | Ratio (0.0 - 1.0) |
| 10 | `arm_swing_deg` | Bilateral Arm Swing Amplitude | Degrees (°) |
| 11 | `rom_score` | Composite Joint Mobility | Percentage (%) |
| 12 | `balance_stability_score` | Center-of-Mass Sway Control | Percentage (%) |

---

## 3. Subject-Independent StratifiedGroupKFold Validation Protocol

To prevent **intra-subject data leakage** (where frames or trials from the same patient are present in both training and testing splits), models are evaluated using `StratifiedGroupKFold` cross-validation (5 folds) grouped strictly by `subject_id` across 71 unique participants.

### Validation Results across 71 Subjects (355 Trials):
- **Logistic Regression (L2 Penalty)**: GroupKFold Accuracy = 99.43%, Macro F1 = 0.9946, Weighted F1 = 0.9944
- **Support Vector Machine (SVM)**: GroupKFold Accuracy = 99.14%, Macro F1 = 0.9918, Weighted F1 = 0.9916
- **Random Forest (100 Trees)**: GroupKFold Accuracy = 98.57%, Macro F1 = 0.9864, Weighted F1 = 0.9859
- **XGBoost (Ensemble)**: GroupKFold Accuracy = 96.34%, Macro F1 = 0.9644, Weighted F1 = 0.9633

---

## 4. Target Classification Categories

1. **Healthy Control Gait & Movement**: Symmetric gait timing, normal range of motion, stable posture.
2. **Stroke Motor Impairment (Restricted Upper-Limb & Asymmetric)**: Hemiparetic flexor hypertonia (`elbow_flexion_deg < 110°`), reduced shoulder swing (`< 20°`), and asymmetric stride timing.
3. **Stroke Motor Impairment (Unstable Gait & Stance)**: Elevated lateral trunk sway, reduced stance balance stability (`balance_stability_score < 60%`), wide base of support.

---

## 5. Clinical Disclaimer
This dataset selection and machine learning architecture is designed as a **decision-support and movement analysis tool** for research. It does not provide automated medical diagnoses.
