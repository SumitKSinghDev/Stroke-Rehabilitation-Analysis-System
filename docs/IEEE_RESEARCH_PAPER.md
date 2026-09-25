# Machine Learning-Based Gait and Upper Limb Motor Impairment Analysis for Stroke Rehabilitation

**IEEE Style Research Draft Paper**

---

## Abstract
Stroke remains a leading cause of long-term adult disability globally. Objective, quantitative assessment of motor impairment is critical for monitoring rehabilitation progress and tailoring physical therapy interventions. Traditional clinical validation scales rely on manual scoring by trained clinicians, which introduces inter-rater variability. This paper presents a markerless monocular computer vision and machine learning framework for quantitative movement analysis. The system combines MediaPipe 33-landmark pose tracking, movement-specific kinematic feature extraction, and multi-session patient progress monitoring. In parallel, a separate research evaluation module benchmarked on the open-access **StrokeRehab Dataset** (Kaku et al., NeurIPS 2022; 431 released video feature dimensions; 5 functional primitives: *Rest, Reach, Transport, Stabilize, Reposition*) achieved 69.24% validation accuracy (Macro F1 = 0.6593) and 63.92% held-out test accuracy (Macro F1 = 0.6233) using Random Forest classification with majority-vote temporal smoothing (window = 9). The application incorporates automated video quality control filtering and relative spatial index normalization while maintaining strict adherence to decision-support guidelines without fabricating medical diagnoses.

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

### A. Subject-Independent Research ML Benchmark
The research machine learning evaluation module was benchmarked on the open-access **StrokeRehab Dataset** (Kaku et al., NeurIPS 2022; 431 released video feature dimensions; 5 functional primitives: *Rest, Reach, Transport, Stabilize, Reposition*) using a strict **subject-independent split** (33 training, 8 validation, and 8 held-out test subjects):

| Evaluation Mode | Model Architecture | Accuracy | Macro F1 Score | Protocol Description |
|---|---|---|---|---|
| **Validation Set (Fold Evaluation)** | Random Forest + Temporal Smoothing (Window=9) | **69.24%** | **0.6593** | Validation set performance across 8 subject-independent folds |
| **Final Held-Out Test Set** | Random Forest + Temporal Smoothing (Window=9) | **63.92%** | **0.6233** | Held-out test performance across 8 unseen test subjects |
| **Raw Test Set (No Smoothing)** | Random Forest Classifier (Raw Sequence) | **59.07%** | **0.5748** | Baseline performance prior to majority-vote temporal smoothing |

---

## IV. Discussion & Clinical Implementation

The application connects the entire video analysis pipeline directly to a responsive web dashboard (React + FastAPI + MongoDB). When keypoint tracking is incomplete, the system explicitly outputs `"Not reliably measurable"`, maintaining scientific integrity.

### Decision-Support & Ethical Guardrails
All UI components and generated PDF reports prominently feature research disclaimers:
> *"This system provides quantitative movement analysis for decision-support purposes only. It does not provide automated medical diagnoses."*

---

## V. Conclusion
We have demonstrated a markerless, subject-independent movement analysis system for stroke rehabilitation. By eliminating legacy dataset dependencies, implementing robust GroupKFold validation, and enforcing explicit Video QC filtering, the system provides a transparent, scientifically defensible platform for clinical movement evaluation.
