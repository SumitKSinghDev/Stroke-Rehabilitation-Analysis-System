# System Documentation: RehabShield AI Decision Support

This documentation covers the biomechanical calculations, machine learning models, database structures, and setup procedures for the B.Tech Major Project: **ML-Based Gait & Upper Limb Motor Impairment Analysis for Stroke Rehabilitation**.

---

## 1. Biomechanical Kinematics & Math Formulas

The system processes video clips frame-by-frame using MediaPipe Pose (33 3D body keypoints). Joint angles and spatial gait parameters are calculated as follows:

### Joint Angle Calculation
For any joint vertex $B$ connected to nodes $A$ and $C$ (e.g., Elbow $B$ connected to Shoulder $A$ and Wrist $C$), the interior joint angle $\theta$ is computed using the coordinates $(x,y)$ of each landmark:

$$\theta = \left| \text{atan2}(y_C - y_B, x_C - x_B) - \text{atan2}(y_A - y_B, x_A - x_B) \right| \times \frac{180}{\pi}$$

If $\theta > 180^\circ$, we normalize the acute/obtuse range:

$$\theta = 360^\circ - \theta$$

- **Elbow Angle**: Joint vertex: Left/Right Elbow. Joint endpoints: Shoulder & Wrist.
- **Shoulder Angle**: Joint vertex: Left/Right Shoulder. Joint endpoints: Hip & Elbow.
- **Hip Angle**: Joint vertex: Left/Right Hip. Joint endpoints: Shoulder & Knee.
- **Knee Angle**: Joint vertex: Left/Right Knee. Joint endpoints: Hip & Ankle.

### Spatial Gait Diagnostics
- **Walking Speed ($v$)**: Distance travelled by the hip midpoint center ($d$) divided by session duration ($t$).
- **Step Symmetry Ratio ($S$)**: Ratio of step length on the hemiparetic affected side ($L_a$) compared to the healthy side ($L_h$):
  $$S = \frac{\min(L_a, L_h)}{\max(L_a, L_h)}$$
  A value of $1.0$ represents perfect symmetry. Stroke patients typically exhibit ratios between $0.45$ and $0.80$.
- **Balance Stability Score**: Calculated as the lateral variance of the trunk center (midpoint of shoulders) across frames. A higher variance represents instability and balance sway.

---

## 2. Machine Learning Classifiers

Extracted gait features are mapped into a 12-dimensional vector:

$$\mathbf{x} = [ \theta_{hip}, \theta_{knee}, \theta_{shoulder}, \theta_{elbow}, L_{stride}, \text{Cadence}, v, w_{step}, S, \theta_{arm\_swing}, \text{ROM}, \text{Stability} ]$$

These vectors are classified into 5 motor impairment levels:
1. **Normal**
2. **Mild**
3. **Moderate**
4. **Severe**
5. **Very Severe**

The backend supports:
- **Random Forest**: Best overall accuracy; handles non-linear gait parameters well.
- **Support Vector Machine (SVM)**: Effective in high-dimensional feature bounds.
- **XGBoost**: Extreme Gradient Boosting for low-latency decision support.

---

## 3. Database Collections (MongoDB)

### `users`
Tracks clinician and administrative credentials.
- `username`: String (Unique login credential)
- `email`: String (HIPAA contact)
- `password_hash`: String (Bcrypt hashed)
- `role`: String (Admin, Physiotherapist, Doctor, Patient)

### `patients`
Stores patient clinical history.
- `patient_id`: String (Unique clinic ID, e.g. `PT-2026-9812`)
- `name`: String
- `age`: Integer
- `stroke_type`: String (Ischemic, Hemorrhagic, TIA)
- `affected_side`: String (Left, Right, Bilateral)
- `stroke_date`: Date String (Onset timeline)
- `current_status`: String (Improving, Stable, Deteriorating)

### `assessments`
Stores video landmarks, calculated angles, and classifier predictions.
- `patient_id`: String
- `session_number`: Integer
- `assessment_date`: DateTime
- `extracted_features`: Joint angles history and gait metrics
- `predictions`: Predicted impairment level and confidence
- `recommendations`: AI Decision Support physical therapy advice
- `therapist_notes`: Manual text entry by physical therapist

---

## 4. Run & Startup Instructions

### Prerequisites
- Node.js (v20+)
- Python (3.10+)

### Quick Launch
1. Open terminal in the project directory.
2. Run the concurrent service script:
   ```bash
   python run_app.py
   ```
3. Open http://localhost:5173 in the browser.
4. Log in using the quick-login shortcuts on the screen.
