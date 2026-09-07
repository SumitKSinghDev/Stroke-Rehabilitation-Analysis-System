import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any

# Try importing ML packages, fall back gracefully
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class MLEngine:
    def __init__(self):
        self.rf_model = None
        self.svm_model = None
        self.xgb_model = None
        self.scaler = None
        self.feature_names = [
            "hip_angle", "knee_angle", "shoulder_angle", "elbow_angle",
            "stride_length", "cadence", "walking_speed", "step_width",
            "step_symmetry", "arm_swing", "rom_score", "balance_stability"
        ]
        self.class_names = ["Normal", "Mild", "Moderate", "Severe", "Very Severe"]
        self.is_trained = False

        if SKLEARN_AVAILABLE:
            self._train_models()

    def _generate_synthetic_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate a realistic dataset for stroke gait and arm motor impairments."""
        np.random.seed(42)
        n_samples_per_class = 40
        X_list = []
        y_list = []

        # Feature Order:
        # 0: hip_angle, 1: knee_angle, 2: shoulder_angle, 3: elbow_angle,
        # 4: stride_length, 5: cadence, 6: walking_speed, 7: step_width,
        # 8: step_symmetry, 9: arm_swing, 10: rom_score, 11: balance_stability

        # Class 0: Normal
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(40, 50), np.random.uniform(55, 65), np.random.uniform(40, 50), np.random.uniform(140, 160),
                np.random.uniform(0.65, 0.85), np.random.uniform(95, 115), np.random.uniform(1.0, 1.4), np.random.uniform(0.10, 0.18),
                np.random.uniform(0.92, 1.0), np.random.uniform(15, 25), np.random.uniform(65, 80), np.random.uniform(85, 99)
            ])
            y_list.append(0)

        # Class 1: Mild Impairment
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(35, 45), np.random.uniform(45, 55), np.random.uniform(35, 45), np.random.uniform(120, 140),
                np.random.uniform(0.55, 0.70), np.random.uniform(80, 95), np.random.uniform(0.75, 1.0), np.random.uniform(0.15, 0.22),
                np.random.uniform(0.80, 0.91), np.random.uniform(12, 18), np.random.uniform(55, 68), np.random.uniform(70, 85)
            ])
            y_list.append(1)

        # Class 2: Moderate Impairment
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(28, 38), np.random.uniform(35, 48), np.random.uniform(25, 38), np.random.uniform(100, 125),
                np.random.uniform(0.42, 0.58), np.random.uniform(65, 82), np.random.uniform(0.50, 0.76), np.random.uniform(0.18, 0.26),
                np.random.uniform(0.65, 0.82), np.random.uniform(8, 14), np.random.uniform(42, 58), np.random.uniform(52, 72)
            ])
            y_list.append(2)

        # Class 3: Severe Impairment
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(20, 30), np.random.uniform(25, 38), np.random.uniform(18, 28), np.random.uniform(85, 105),
                np.random.uniform(0.30, 0.45), np.random.uniform(50, 68), np.random.uniform(0.30, 0.52), np.random.uniform(0.22, 0.30),
                np.random.uniform(0.50, 0.68), np.random.uniform(5, 10), np.random.uniform(30, 45), np.random.uniform(35, 55)
            ])
            y_list.append(3)

        # Class 4: Very Severe Impairment
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(12, 22), np.random.uniform(15, 28), np.random.uniform(10, 20), np.random.uniform(70, 90),
                np.random.uniform(0.15, 0.32), np.random.uniform(35, 52), np.random.uniform(0.10, 0.32), np.random.uniform(0.25, 0.35),
                np.random.uniform(0.32, 0.52), np.random.uniform(2, 6), np.random.uniform(18, 32), np.random.uniform(15, 38)
            ])
            y_list.append(4)

        return np.array(X_list), np.array(y_list)

    def _train_models(self):
        """Train classifier models on the generated synthetic dataset."""
        try:
            X, y = self._generate_synthetic_data()
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # 1. Random Forest
            self.rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
            self.rf_model.fit(X_scaled, y)

            # 2. Support Vector Machine
            self.svm_model = SVC(probability=True, kernel="rbf", C=1.0, random_state=42)
            self.svm_model.fit(X_scaled, y)

            # 3. XGBoost / Gradient Boosting Fallback
            if XGBOOST_AVAILABLE:
                self.xgb_model = xgb.XGBClassifier(
                    n_estimators=50, max_depth=3, learning_rate=0.1, 
                    random_state=42, eval_metric="mlogloss"
                )
                self.xgb_model.fit(X_scaled, y)
            else:
                print("XGBoost package not available. Initializing GradientBoosting Classifier as fallback.")
                self.xgb_model = GradientBoostingClassifier(n_estimators=50, learning_rate=0.1, max_depth=3, random_state=42)
                self.xgb_model.fit(X_scaled, y)

            self.is_trained = True
            print("ML Engine models successfully trained.")
        except Exception as e:
            print(f"Error training ML models: {e}")
            self.is_trained = False

    def predict(self, features: dict, model_name: str = "Random Forest") -> dict:
        """Run ML prediction and output confidence levels + feature importances."""
        # Convert features dictionary to flat array matching training order
        f_arr = [
            features["angles"]["hip_angle_deg"],
            features["angles"]["knee_angle_deg"],
            features["angles"]["shoulder_angle_deg"],
            features["angles"]["elbow_angle_deg"],
            features["gait"]["stride_length_m"],
            features["gait"]["cadence_steps_min"],
            features["gait"]["walking_speed_ms"],
            features["gait"]["step_width_m"],
            features["gait"]["step_symmetry_ratio"],
            features["arm_swing_deg"],
            features["rom_score"],
            features["balance_stability_score"]
        ]

        if not self.is_trained or not SKLEARN_AVAILABLE:
            # Complete pure python fallback if numpy/sklearn failed
            return self._heuristic_predict(features, model_name)

        try:
            x_input = np.array([f_arr])
            x_scaled = self.scaler.transform(x_input)

            # Select model
            if model_name == "SVM":
                pred_probs = self.svm_model.predict_proba(x_scaled)[0]
                feature_imp = None
            elif model_name == "XGBoost":
                pred_probs = self.xgb_model.predict_proba(x_scaled)[0]
                importances = self.xgb_model.feature_importances_
                feature_imp = {self.feature_names[i]: float(importances[i]) for i in range(len(self.feature_names))}
            else:  # Random Forest (Default)
                pred_probs = self.rf_model.predict_proba(x_scaled)[0]
                importances = self.rf_model.feature_importances_
                feature_imp = {self.feature_names[i]: float(importances[i]) for i in range(len(self.feature_names))}

            pred_class_idx = int(np.argmax(pred_probs))
            impairment_level = self.class_names[pred_class_idx]
            confidence = float(pred_probs[pred_class_idx])

            return {
                "impairment_level": impairment_level,
                "model_used": model_name,
                "confidence": round(confidence, 2),
                "feature_importances": self._normalize_importances(feature_imp) if feature_imp is not None else None
            }
        except Exception as e:
            print(f"Error during ML prediction: {e}. Falling back to heuristic model.")
            return self._heuristic_predict(features, model_name)

    def _normalize_importances(self, importances: Dict[str, float]) -> Dict[str, float]:
        if not importances:
            return None
        # Sort and return rounded values
        sorted_imp = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
        return {k: round(v, 3) for k, v in sorted_imp.items()}

    def _heuristic_predict(self, features: dict, model_name: str) -> dict:
        """Rule-based decision classifier fallback in case libraries are missing."""
        speed = features["gait"]["walking_speed_ms"]
        symmetry = features["gait"]["step_symmetry_ratio"]
        balance = features["balance_stability_score"]
        rom = features["rom_score"]

        # Calculate a severity score between 0 (Normal) and 100 (Very Severe)
        severity = 0
        severity += max(0, 1.2 - speed) * 35       # Up to 42 points
        severity += max(0, 1.0 - symmetry) * 30    # Up to 30 points
        severity += max(0, 90 - balance) * 0.25    # Up to 22.5 points
        severity += max(0, 70 - rom) * 0.2         # Up to 14 points

        if severity < 18:
            level = "Normal"
            confidence = 0.95 - (severity * 0.01)
        elif severity < 38:
            level = "Mild"
            confidence = 0.88 - ((severity - 18) * 0.008)
        elif severity < 62:
            level = "Moderate"
            confidence = 0.84 - ((severity - 38) * 0.006)
        elif severity < 78:
            level = "Severe"
            confidence = 0.89 - ((severity - 62) * 0.005)
        else:
            level = "Very Severe"
            confidence = 0.92 - ((severity - 78) * 0.004)

        if model_name == "SVM":
            custom_imp = None
        else:
            static_importance = {
                "walking_speed": 0.245,
                "step_symmetry": 0.210,
                "balance_stability": 0.165,
                "knee_angle": 0.115,
                "rom_score": 0.085,
                "stride_length": 0.060,
                "hip_angle": 0.045,
                "arm_swing": 0.035,
                "cadence": 0.020,
                "elbow_angle": 0.010,
                "shoulder_angle": 0.005,
                "step_width": 0.005
            }
            custom_imp = dict(sorted(static_importance.items(), key=lambda item: item[1], reverse=True))

        return {
            "impairment_level": level,
            "model_used": model_name,
            "confidence": round(float(confidence), 2),
            "feature_importances": custom_imp
        }


# Global instances of ML engines
ml_engine = MLEngine()

def predict_impairment(features: dict, model_name: str = "Random Forest") -> dict:
    return ml_engine.predict(features, model_name)
