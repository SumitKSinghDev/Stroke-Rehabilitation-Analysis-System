"""
StrokeRehab Research Model Loader & Inference Module
=====================================================

Loads the Random Forest research model trained on released StrokeRehab 431-dimensional video features.
Provides safe loading, feature dimension checks, non-constant feature masking, and temporal majority-vote smoothing.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger("stroke_rehab_research")

MODEL_DIR = Path(__file__).parent
RF_MODEL_PATH = MODEL_DIR / "rf_stroke_rehab_model.joblib"
MASK_PATH = MODEL_DIR / "non_constant_mask.npy"

FUNCTIONAL_PRIMITIVES = ["rest", "reach", "transport", "stabilize", "reposition"]

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None


class StrokeRehabResearchEngine:
    def __init__(self):
        self.model = None
        self.non_constant_mask = None
        self.is_loaded = False
        self._try_load_model()

    def _try_load_model(self):
        """Attempts to load rf_stroke_rehab_model.joblib and non_constant_mask.npy safely."""
        if not JOBLIB_AVAILABLE:
            logger.warning("joblib is not installed. StrokeRehab research model cannot be loaded.")
            return

        try:
            if MASK_PATH.exists():
                self.non_constant_mask = np.load(MASK_PATH)
                logger.info(f"Loaded non-constant feature mask from {MASK_PATH}")

            if RF_MODEL_PATH.exists():
                self.model = joblib.load(RF_MODEL_PATH)
                self.is_loaded = True
                logger.info(f"Successfully loaded StrokeRehab research model from {RF_MODEL_PATH}")
            else:
                logger.info(f"StrokeRehab model file not yet present at {RF_MODEL_PATH}. Standalone research results endpoint will serve verified benchmark metrics.")
        except Exception as err:
            logger.error(f"Error loading StrokeRehab research model: {err}")
            self.is_loaded = False

    def predict_primitives(self, feature_matrix: np.ndarray, apply_smoothing: bool = True, window_size: int = 9) -> Dict[str, Any]:
        """
        Runs primitive classification on 431 or 432-dimensional StrokeRehab released features.
        Applies majority-vote temporal smoothing with window size 9 if requested.
        """
        if not self.is_loaded or self.model is None:
            return {
                "status": "model_not_loaded",
                "message": "StrokeRehab research model is not loaded on disk.",
                "predictions": None
            }

        arr = np.asarray(feature_matrix, dtype=np.float32)

        # Feature masking: if 432 features are provided, remove constant feature #83 or apply mask
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        n_features = arr.shape[1]
        if n_features == 432:
            if self.non_constant_mask is not None:
                arr = arr[:, self.non_constant_mask]
            else:
                # Remove constant feature index 83
                arr = np.delete(arr, 83, axis=1)
        elif n_features != 431:
            return {
                "status": "invalid_feature_dimension",
                "message": f"Expected 431 or 432 features for StrokeRehab research model, got {n_features}.",
                "predictions": None
            }

        try:
            raw_preds = self.model.predict(arr)
            probs = self.model.predict_proba(arr)

            final_preds = raw_preds
            if apply_smoothing and len(raw_preds) >= window_size:
                final_preds = self._apply_majority_vote_smoothing(raw_preds, window_size)

            pred_labels = [FUNCTIONAL_PRIMITIVES[int(idx)] if int(idx) < len(FUNCTIONAL_PRIMITIVES) else f"Primitive_{idx}" for idx in final_preds]

            return {
                "status": "success",
                "predictions": pred_labels,
                "raw_predictions": [FUNCTIONAL_PRIMITIVES[int(idx)] for idx in raw_preds],
                "temporal_smoothing_applied": apply_smoothing,
                "window_size": window_size,
                "probabilities": probs.tolist()
            }
        except Exception as e:
            logger.error(f"Inference error in StrokeRehab model: {e}")
            return {
                "status": "error",
                "message": str(e),
                "predictions": None
            }

    def _apply_majority_vote_smoothing(self, predictions: np.ndarray, window_size: int = 9) -> np.ndarray:
        """Applies majority vote window smoothing to sequence predictions."""
        half_w = window_size // 2
        smoothed = np.copy(predictions)
        n = len(predictions)

        for i in range(n):
            start_i = max(0, i - half_w)
            end_i = min(n, i + half_w + 1)
            window = predictions[start_i:end_i]
            counts = np.bincount(window)
            smoothed[i] = np.argmax(counts)

        return smoothed


# Global instance
stroke_rehab_engine = StrokeRehabResearchEngine()
