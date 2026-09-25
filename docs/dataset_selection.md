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

## 2. Research Datasets & Their Distinct Roles

RehabShield incorporates three open-access research datasets, each fulfilling a distinct, non-overlapping role:

1. **Study36 Dataset** (`data/study36-2026-09-08-07-53.zip`):
   - **Role**: Dataset-derived healthy-control movement reference characteristics.
   - **Structure**: 1,426 CSV files across 20 healthy control subjects, 106 joint-angle kinematic time-series columns sampled at 100 Hz.
   - **Usage**: Provides empirical normative baseline distributions for healthy joint ranges of motion (e.g., shoulder swing, elbow flexion) to benchmark patient movement.

2. **Study37 / StrokeRehab Dataset** (`data/study37-2026-09-08-08-09.zip`):
   - **Role**: Standalone Research ML Benchmark for Temporal Primitive Recognition.
   - **Structure**: 3,058 trials across 51 stroke-impaired participants; 431 released video feature dimensions; 5 temporal functional primitives (*Rest, Reach, Transport, Stabilize, Reposition*).
   - **Validation Metrics**: Validation Accuracy = **69.24%** (Macro F1 = 0.6593); Held-out Test Accuracy = **63.92%** (Macro F1 = 0.6233); Raw Test Accuracy = **59.07%** (Macro F1 = 0.5748).

3. **Upper-Limb Exercise Video Dataset** (`data/An upper limb stroke rehabilitation exercise video.zip`):
   - **Role**: Video-Based Upper-Limb Exercise Completion Evaluation.
   - **Structure**: 491 MP4 videos across 4 exercises (*Lifting an Object, Extending the Elbow, Lifting the Wrist, Opening the Hand*) labeled as *Complete* vs. *Incomplete* (411 Train, 80 Test).

---

## 4. Target Classification Categories

1. **Healthy Control Gait & Movement**: Symmetric gait timing, normal range of motion, stable posture.
2. **Stroke Motor Impairment (Restricted Upper-Limb & Asymmetric)**: Hemiparetic flexor hypertonia (`elbow_flexion_deg < 110°`), reduced shoulder swing (`< 20°`), and asymmetric stride timing.
3. **Stroke Motor Impairment (Unstable Gait & Stance)**: Elevated lateral trunk sway, reduced stance balance stability (`balance_stability_score < 60%`), wide base of support.

---

## 5. Clinical Disclaimer
This dataset selection and machine learning architecture is designed as a **decision-support and movement analysis tool** for research. It does not provide automated medical diagnoses.
