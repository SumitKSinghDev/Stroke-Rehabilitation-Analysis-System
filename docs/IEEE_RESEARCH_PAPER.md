# Machine Learning-Based Gait and Upper Limb Motor Impairment Analysis for Stroke Rehabilitation

**IEEE Style Research Draft Paper**

---

## Abstract
Stroke remains a leading cause of long-term adult disability globally. Objective, quantitative assessment of motor impairment is critical for monitoring rehabilitation progress and tailoring physical therapy interventions. Traditional clinical validation scales, such as the Fugl-Meyer Assessment (FMA) and Berg Balance Scale (BBS), rely on manual scoring by trained clinicians, which introduces inter-rater variability and periodic sampling constraints. This paper presents a markerless, monocular computer vision and subject-independent machine learning framework for quantitative movement analysis. Trained on the open-access **StrokeRehab Dataset** (71 participants: 51 stroke-impaired, 20 healthy control; 355 total ADL trials) with gait parameter reference validation from the **PhysioNet Multi-Gait Dataset**, the system utilizes MediaPipe 33-landmark pose tracking, peak-based heel strike detection, and a 12-dimensional biomechanical feature representation to classify stroke movement impairment patterns into ground-truth categories (*Healthy Control Gait & Movement*, *Stroke Motor Impairment: Restricted Upper-Limb & Asymmetric*, *Stroke Motor Impairment: Unstable Gait & Stance*). Evaluated via 5-Fold StratifiedGroupKFold cross-validation across 71 unique subjects to prevent intra-subject data leakage, Logistic Regression achieved 99.43% accuracy (Macro F1 = 0.9946), SVM achieved 99.14% accuracy (Macro F1 = 0.9918), and Random Forest achieved 98.57% accuracy (Macro F1 = 0.9864). The application incorporates automated Video Quality Control (QC) filtering, relative spatial index normalization, and analysis-based exercise considerations while maintaining strict adherence to decision-support guidelines without fabricating medical diagnoses.

---

## I. Introduction
Post-stroke motor impairment manifests in diverse kinematic deviations, including hemiparetic circumduction, stiff-knee gait, flexor spasticity in the upper limbs, and trunk sway instability. Quantitative gait analysis traditionally requires expensive optical motion capture systems (e.g., Vicon, Qualisys) or body-worn inertial measurement units (IMUs), limiting their adoption in home-based or low-resource clinical settings.

Recent advances in deep-learning-based pose estimation enable markerless kinematic estimation directly from standard RGB video sequences. However, existing applications frequently suffer from methodological flaws:
1. **Intra-Subject Data Leakage**: Standard random splits leak frames from the same subject into train/test sets, inflating cross-validation performance.
2. **Uncalibrated Metric Errors**: Reporting absolute metric distances (e.g., meters or m/s) from monocular camera clips without camera calibration introduces distance-dependent distortion.
3. **Fabricated Skeletons & Metrics**: Systems displaying static default skeletons when pose detection fails mask tracking errors.

To address these challenges, we introduce an integrated, end-to-end quantitative movement analysis system designed for stroke rehabilitation.

---

## II. Methodology

### A. Video Quality Control (QC) Pre-Filtering
Before feature extraction, incoming RGB video files undergo automated pre-filtering evaluating:
- **Resolution & Aspect Ratio**: Verifies minimum vertical resolution ($>360\text{p}$).
- **Pose Detection Fidelity**: Requires $>40\%$ valid 33-landmark detections across total video frames.
- **Lighting & Boundary Quality**: Flags low-contrast or truncated lower-body clips.

Videos failing QC return explicit status warnings (`Poor / Insufficient`) rather than fallback defaults.

### B. Markerless Pose Tracking & Peak Step Detection
MediaPipe Pose Landmarker extracts 33 body coordinate keypoints $P_i = (x_i, y_i, z_i, v_i)$ per frame $t$. Step segmentation is performed by detecting local minima in vertical ankle displacement $y_{\text{ankle}}(t)$ corresponding to heel strike ground contact events.

### C. 12-Dimensional Biomechanical Feature Representation
To normalize spatial measurements across uncalibrated cameras, spatial parameters are computed as relative indices scaled against anatomical segment lengths (e.g., total leg length or inter-hip distance):

1. **Hip Sagittal ROM ($f_1$)**: Excursion angle between shoulder, hip, and knee vectors.
2. **Peak Knee Flexion ($f_2$)**: Anatomical swing-phase knee flexion ($180^\circ - \text{joint angle}$).
3. **Shoulder Mobility ($f_3$)**: Sagittal shoulder swing range.
4. **Elbow Flexion ($f_4$)**: Interior elbow angle indicating upper-limb flexor hypertonia.
5. **Relative Stride Length Index ($f_5$)**: Mean peak-to-peak ankle stride normalized by leg length.
6. **Cadence ($f_6$)**: Step frequency (steps/min).
7. **Relative Walking Speed Index ($f_7$)**: Normalized velocity index $\frac{f_5 \times f_6}{120}$.
8. **Relative Step Width Index ($f_8$)**: Lateral foot displacement normalized by hip width.
9. **Step Symmetry Ratio ($f_9$)**: Bilateral stance timing ratio $\frac{\min(t_L, t_R)}{\max(t_L, t_R)}$.
10. **Arm Swing Amplitude ($f_{10}$)**: Maximum wrist displacement range during walk cycles.
11. **Composite ROM Score ($f_{11}$)**: Normalized weighted average of lower and upper limb ROM.
12. **Balance Stability Score ($f_{12}$)**: Postural stability index based on lateral trunk sway deviation.

---

## III. Experiments & Validation Results

### A. Subject-Independent StratifiedGroupKFold Validation
The dataset comprises 355 trials across 71 distinct subjects (51 stroke-impaired, 20 healthy control) grouped strictly by `subject_id`. Evaluation was executed via 5-Fold `StratifiedGroupKFold` cross-validation:

| Model Classifier | GroupKFold Accuracy | Macro F1 Score | Weighted Precision | Weighted Recall | Weighted F1 Score |
|---|---|---|---|---|---|
| **Logistic Regression (L2)** | **99.43%** | **0.9946** | **0.9946** | **0.9943** | **0.9944** |
| **SVM (RBF Kernel)** | **99.14%** | **0.9918** | **0.9918** | **0.9914** | **0.9916** |
| **Random Forest (100 Trees)** | **98.57%** | **0.9864** | **0.9860** | **0.9857** | **0.9859** |
| **XGBoost Classifier** | **96.34%** | **0.9644** | **0.9634** | **0.9634** | **0.9633** |

---

## IV. Discussion & Clinical Implementation

The application connects the entire video analysis pipeline directly to a responsive web dashboard (React + FastAPI + MongoDB). When keypoint tracking is incomplete, the system explicitly outputs `"Not reliably measurable"`, maintaining scientific integrity.

### Decision-Support & Ethical Guardrails
All UI components and generated PDF reports prominently feature research disclaimers:
> *"This system provides quantitative movement analysis for decision-support purposes only. It does not provide automated medical diagnoses."*

---

## V. Conclusion
We have demonstrated a markerless, subject-independent movement analysis system for stroke rehabilitation. By eliminating legacy dataset dependencies, implementing robust GroupKFold validation, and enforcing explicit Video QC filtering, the system provides a transparent, scientifically defensible platform for clinical movement evaluation.
