import os
import logging
from pathlib import Path
from typing import Dict, Tuple, Any, Optional
import numpy as np

logger = logging.getLogger("ml_engine")

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "gait_classifier.joblib"
SCALER_PATH = MODEL_DIR / "gait_scaler.joblib"

# Try importing ML packages
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    joblib = None

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
            self._load_or_train_models()

    def _generate_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate training dataset based on biomechanical range distributions."""
        np.random.seed(42)
        n_samples_per_class = 50
        X_list = []
        y_list = []

        # Class 0: Normal
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(40, 50), np.random.uniform(55, 65), np.random.uniform(40, 50), np.random.uniform(140, 160),
                np.random.uniform(0.65, 0.85), np.random.uniform(95, 115), np.random.uniform(1.0, 1.4), np.random.uniform(0.10, 0.18),
                np.random.uniform(0.92, 1.0), np.random.uniform(15, 25), np.random.uniform(65, 80), np.random.uniform(85, 99)
            ])
            y_list.append(0)

        # Class 1: Mild
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(35, 45), np.random.uniform(45, 55), np.random.uniform(35, 45), np.random.uniform(120, 140),
                np.random.uniform(0.55, 0.70), np.random.uniform(80, 95), np.random.uniform(0.75, 1.0), np.random.uniform(0.15, 0.22),
                np.random.uniform(0.80, 0.91), np.random.uniform(12, 18), np.random.uniform(55, 68), np.random.uniform(70, 85)
            ])
            y_list.append(1)

        # Class 2: Moderate
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(28, 38), np.random.uniform(35, 48), np.random.uniform(25, 38), np.random.uniform(100, 125),
                np.random.uniform(0.42, 0.58), np.random.uniform(65, 82), np.random.uniform(0.50, 0.76), np.random.uniform(0.18, 0.26),
                np.random.uniform(0.65, 0.82), np.random.uniform(8, 14), np.random.uniform(42, 58), np.random.uniform(52, 72)
            ])
            y_list.append(2)

        # Class 3: Severe
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(20, 30), np.random.uniform(25, 38), np.random.uniform(18, 28), np.random.uniform(85, 105),
                np.random.uniform(0.30, 0.45), np.random.uniform(50, 68), np.random.uniform(0.30, 0.52), np.random.uniform(0.22, 0.30),
                np.random.uniform(0.50, 0.68), np.random.uniform(5, 10), np.random.uniform(30, 45), np.random.uniform(35, 55)
            ])
            y_list.append(3)

        # Class 4: Very Severe
        for _ in range(n_samples_per_class):
            X_list.append([
                np.random.uniform(12, 22), np.random.uniform(15, 28), np.random.uniform(10, 20), np.random.uniform(70, 90),
                np.random.uniform(0.15, 0.32), np.random.uniform(35, 52), np.random.uniform(0.10, 0.32), np.random.uniform(0.25, 0.35),
                np.random.uniform(0.32, 0.52), np.random.uniform(2, 6), np.random.uniform(18, 32), np.random.uniform(15, 38)
            ])
            y_list.append(4)

        return np.array(X_list), np.array(y_list)

    def _load_or_train_models(self):
        """Load trained models from disk, or train and persist them if missing."""
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        try:
            if MODEL_PATH.exists() and SCALER_PATH.exists() and joblib is not None:
                logger.info(f"Loading trained ML model and scaler from disk ({MODEL_PATH})...")
                models_dict = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.rf_model = models_dict.get("rf")
                self.svm_model = models_dict.get("svm")
                self.xgb_model = models_dict.get("xgb")
                self.is_trained = True
                logger.info("Trained ML models loaded successfully from disk!")
                return
        except Exception as err:
            logger.warning(f"Could not load ML models from disk: {err}. Re-training model...")

        try:
            X, y = self._generate_training_data()
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.rf_model.fit(X_scaled, y)

            self.svm_model = SVC(probability=True, kernel="rbf", C=1.0, random_state=42)
            self.svm_model.fit(X_scaled, y)

            if XGBOOST_AVAILABLE:
                self.xgb_model = xgb.XGBClassifier(
                    n_estimators=50, max_depth=3, learning_rate=0.1, 
                    random_state=42, eval_metric="mlogloss"
                )
                self.xgb_model.fit(X_scaled, y)
            else:
                self.xgb_model = GradientBoostingClassifier(n_estimators=50, learning_rate=0.1, max_depth=3, random_state=42)
                self.xgb_model.fit(X_scaled, y)

            self.is_trained = True

            if joblib is not None:
                joblib.dump({"rf": self.rf_model, "svm": self.svm_model, "xgb": self.xgb_model}, MODEL_PATH)
                joblib.dump(self.scaler, SCALER_PATH)
                logger.info(f"ML Engine models successfully trained and saved to disk ({MODEL_PATH}).")
        except Exception as e:
            logger.error(f"Error training/saving ML models: {e}")
            self.is_trained = False

    def predict(self, features: dict, model_name: str = "Random Forest") -> dict:
        """Run ML prediction and output confidence levels + feature importances."""
        if not self.is_trained or not SKLEARN_AVAILABLE or self.scaler is None:
            return {
                "impairment_level": "Unavailable",
                "model_used": model_name,
                "confidence": None,
                "feature_importances": None,
                "compatibility_note": "ML classification from this video is unavailable because trained model dependencies are not loaded."
            }

        try:
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
        except (KeyError, TypeError) as err:
            logger.error(f"Feature extraction dictionary incomplete: {err}")
            return {
                "impairment_level": "Unavailable",
                "model_used": model_name,
                "confidence": None,
                "feature_importances": None,
                "compatibility_note": f"Feature format incompatible: {err}"
            }

        try:
            x_input = np.array([f_arr])
            
            # Select target model
            if model_name == "SVM":
                target_model = self.svm_model
            elif model_name == "XGBoost":
                target_model = self.xgb_model
            else:
                target_model = self.rf_model

            if target_model is None:
                target_model = self.rf_model

            # Verify input dimension feature compatibility
            expected_n_features = getattr(target_model, "n_features_in_", 12)
            if x_input.shape[1] != expected_n_features:
                logger.error(f"Feature dimension mismatch: Model expects {expected_n_features} features, got {x_input.shape[1]}")
                return {
                    "impairment_level": "Unavailable",
                    "model_used": model_name,
                    "confidence": None,
                    "feature_importances": None,
                    "compatibility_note": f"ML classification from this video is unavailable because the current trained model expects a different feature representation ({expected_n_features} vs {x_input.shape[1]})."
                }

            x_scaled = self.scaler.transform(x_input)
            pred_probs = target_model.predict_proba(x_scaled)[0]

            feature_imp = None
            if hasattr(target_model, "feature_importances_"):
                importances = target_model.feature_importances_
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
            logger.error(f"Error during ML prediction: {e}")
            return {
                "impairment_level": "Unavailable",
                "model_used": model_name,
                "confidence": None,
                "feature_importances": None,
                "compatibility_note": f"ML prediction calculation error: {e}"
            }

    def _normalize_importances(self, importances: Dict[str, float]) -> Dict[str, float]:
        if not importances:
            return None
        sorted_imp = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
        return {k: round(v, 3) for k, v in sorted_imp.items()}


# Global instance of ML engine
ml_engine = MLEngine()

def predict_impairment(features: dict, model_name: str = "Random Forest") -> dict:
    return ml_engine.predict(features, model_name)

