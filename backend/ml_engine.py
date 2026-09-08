"""
Machine Learning Inference Engine
=================================

Evaluates 12-dimensional biomechanical feature vectors against subject-independent ML models
(Random Forest, SVM, Logistic Regression, XGBoost) trained on the StrokeRehab Dataset.
Performs feature schema compatibility checks, strict probability normalization (summing to 100%),
and model-specific feature explanations.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, Any, Optional
import numpy as np

try:
    from backend.feature_extractor import FEATURE_NAMES, build_feature_vector
except ImportError:
    from feature_extractor import FEATURE_NAMES, build_feature_vector

logger = logging.getLogger("ml_engine")

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "gait_classifier.joblib"
SCALER_PATH = MODEL_DIR / "gait_scaler.joblib"
ENCODER_PATH = MODEL_DIR / "label_encoder.joblib"
SCHEMA_PATH = MODEL_DIR / "feature_schema.json"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler, LabelEncoder
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
        self.lr_model = None
        self.xgb_model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = FEATURE_NAMES
        self.class_names = []
        self.metadata = {}
        self.is_trained = False
        self.schema_valid = False

        if SKLEARN_AVAILABLE:
            self._load_models_and_verify_schema()

    def _load_models_and_verify_schema(self):
        """Load trained models from disk and verify feature schema compatibility."""
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        try:
            if MODEL_PATH.exists() and SCALER_PATH.exists() and ENCODER_PATH.exists() and joblib is not None:
                logger.info(f"Loading StrokeRehab ML models from {MODEL_DIR}...")
                models_dict = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.label_encoder = joblib.load(ENCODER_PATH)

                self.rf_model = models_dict.get("rf")
                self.svm_model = models_dict.get("svm")
                self.lr_model = models_dict.get("lr")
                self.xgb_model = models_dict.get("xgb")

                if hasattr(self.label_encoder, "classes_"):
                    self.class_names = [str(c) for c in self.label_encoder.classes_]

                # Verify Schema Compatibility
                if SCHEMA_PATH.exists():
                    with open(SCHEMA_PATH, "r") as f:
                        schema = json.load(f)
                    saved_names = schema.get("feature_names", [])
                    if len(saved_names) != len(self.feature_names) or saved_names != self.feature_names:
                        logger.error(f"Feature schema mismatch! Expected {len(self.feature_names)} features ({self.feature_names}), saved {len(saved_names)} ({saved_names}).")
                        self.schema_valid = False
                    else:
                        self.schema_valid = True

                if METADATA_PATH.exists():
                    with open(METADATA_PATH, "r") as f:
                        self.metadata = json.load(f)

                self.is_trained = True
                logger.info(f"Loaded trained models successfully. Target Classes ({len(self.class_names)}): {self.class_names}")
                return
        except Exception as err:
            logger.warning(f"Could not load ML models from disk: {err}. Retraining pipeline...")

        # Invoke train_models if models missing
        try:
            from train_models import train_and_evaluate_models
            train_and_evaluate_models()
            if MODEL_PATH.exists() and SCALER_PATH.exists() and ENCODER_PATH.exists() and joblib is not None:
                models_dict = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.label_encoder = joblib.load(ENCODER_PATH)
                self.rf_model = models_dict.get("rf")
                self.svm_model = models_dict.get("svm")
                self.lr_model = models_dict.get("lr")
                self.xgb_model = models_dict.get("xgb")
                if hasattr(self.label_encoder, "classes_"):
                    self.class_names = [str(c) for c in self.label_encoder.classes_]
                self.is_trained = True
                self.schema_valid = True
        except Exception as e:
            logger.error(f"Failed to train ML models: {e}")
            self.is_trained = False

    def predict(self, features: dict, model_name: str = "Random Forest") -> dict:
        """
        Run ML classification, returning strictly normalized probabilities (summing to 100%)
        and model-specific feature explanations.
        """
        if not self.is_trained or not SKLEARN_AVAILABLE or self.scaler is None:
            return {
                "impairment_level": "Not reliably measurable",
                "model_used": model_name,
                "confidence": None,
                "feature_importances": None,
                "prediction_probabilities": None,
                "compatibility_note": "ML classification unavailable: trained model dependencies not loaded."
            }

        # Extract 12-dimensional feature vector
        f_vec = features.get("feature_vector")
        if f_vec is None or len(f_vec) != len(self.feature_names) or any(v is None for v in f_vec):
            f_vec = build_feature_vector(features)

        if f_vec is None or len(f_vec) != len(self.feature_names) or any(v is None for v in f_vec):
            logger.warning("Incomplete or incompatible feature vector for ML inference.")
            return {
                "impairment_level": "Not reliably measurable",
                "model_used": model_name,
                "confidence": None,
                "feature_importances": None,
                "prediction_probabilities": None,
                "compatibility_note": "Not reliably measurable due to incomplete pose keypoints or tracking loss."
            }

        try:
            x_input = np.array([f_vec], dtype=np.float32)

            # Model Selection
            clean_name = model_name.strip().title()
            if "Svm" in clean_name or "Support Vector" in clean_name:
                target_model = self.svm_model
                actual_name = "SVM"
            elif "Xgboost" in clean_name or "Xgb" in clean_name:
                target_model = self.xgb_model
                actual_name = "XGBoost"
            elif "Logistic" in clean_name:
                target_model = self.lr_model
                actual_name = "Logistic Regression"
            else:
                target_model = self.rf_model
                actual_name = "Random Forest"

            if target_model is None:
                target_model = self.rf_model
                actual_name = "Random Forest"

            # Feature schema compatibility check against model
            expected_n_features = getattr(target_model, "n_features_in_", 12)
            if x_input.shape[1] != expected_n_features:
                logger.error(f"Feature dimension mismatch: Model expects {expected_n_features} features, got {x_input.shape[1]}.")
                return {
                    "impairment_level": "Not reliably measurable",
                    "model_used": model_name,
                    "confidence": None,
                    "feature_importances": None,
                    "prediction_probabilities": None,
                    "compatibility_note": f"Model feature schema mismatch. Expected {expected_n_features} features, got {x_input.shape[1]}."
                }

            x_scaled = self.scaler.transform(x_input)
            pred_probs_raw = target_model.predict_proba(x_scaled)[0]

            # Strict Probability Normalization (guaranteeing sum == 100.0%)
            prob_sum = float(np.sum(pred_probs_raw))
            if prob_sum > 0:
                pred_probs_norm = pred_probs_raw / prob_sum
            else:
                pred_probs_norm = np.ones_like(pred_probs_raw) / len(pred_probs_raw)

            # Round to 1 decimal place and adjust max probability by remainder
            raw_rounded = [round(float(p) * 100.0, 1) for p in pred_probs_norm]
            remainder = round(100.0 - sum(raw_rounded), 1)
            if abs(remainder) > 0 and len(raw_rounded) > 0:
                max_i = int(np.argmax(pred_probs_norm))
                raw_rounded[max_i] = round(raw_rounded[max_i] + remainder, 1)

            prob_dict = {}
            for idx, prob_val in enumerate(raw_rounded):
                c_name = str(self.class_names[idx]) if idx < len(self.class_names) else f"Class {idx}"
                prob_dict[c_name] = prob_val

            assert abs(sum(prob_dict.values()) - 100.0) < 0.1, f"Probability total must sum to 100.0%, got {sum(prob_dict.values())}"

            # Model-Specific Feature Explanations
            feature_imp = None
            if hasattr(target_model, "feature_importances_"):
                importances = target_model.feature_importances_
                feature_imp = {self.feature_names[i]: float(importances[i]) for i in range(len(self.feature_names))}
            elif hasattr(target_model, "coef_"):
                # For Logistic Regression: normalized coefficient magnitude as "Relative Feature Weight"
                coef_mag = np.mean(np.abs(target_model.coef_), axis=0)
                total_mag = float(np.sum(coef_mag))
                if total_mag > 0:
                    coef_norm = coef_mag / total_mag
                    feature_imp = {self.feature_names[i]: float(coef_norm[i]) for i in range(len(self.feature_names))}

            pred_class_idx = int(np.argmax(pred_probs_norm))
            impairment_level = str(self.class_names[pred_class_idx]) if pred_class_idx < len(self.class_names) else "Unknown"
            confidence = float(pred_probs_norm[pred_class_idx]) * 100.0

            return {
                "impairment_level": impairment_level,
                "model_used": actual_name,
                "confidence": round(confidence, 1),
                "feature_importances": self._normalize_importances(feature_imp) if feature_imp is not None else None,
                "prediction_probabilities": prob_dict
            }

        except Exception as e:
            logger.error(f"Error during ML prediction: {e}")
            return {
                "impairment_level": "Not reliably measurable",
                "model_used": model_name,
                "confidence": None,
                "feature_importances": None,
                "prediction_probabilities": None,
                "compatibility_note": f"ML classification calculation error: {e}"
            }

    def _normalize_importances(self, importances: Dict[str, float]) -> Dict[str, float]:
        if not importances:
            return None
        total = sum(importances.values())
        if total <= 0:
            return None
        sorted_imp = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
        return {k: round((v / total) * 100.0, 1) for k, v in sorted_imp.items()}


# Global instance of ML engine
ml_engine = MLEngine()


def predict_impairment(features: dict, model_name: str = "Random Forest") -> dict:
    return ml_engine.predict(features, model_name)
