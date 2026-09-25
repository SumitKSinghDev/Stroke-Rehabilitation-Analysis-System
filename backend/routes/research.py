"""
Research ML Evaluation API Routes
=================================

Provides API endpoints for the separate StrokeRehab Research ML Evaluation component.
Exposes verified benchmark results on the StrokeRehab Dataset (Kaku et al., NeurIPS 2022)
and provides safe inference endpoint for compatible 431-dimensional feature inputs.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

try:
    from backend.models.stroke_rehab.research_loader import stroke_rehab_engine, FUNCTIONAL_PRIMITIVES
except ImportError:
    from models.stroke_rehab.research_loader import stroke_rehab_engine, FUNCTIONAL_PRIMITIVES

router = APIRouter(
    prefix="/research",
    tags=["Research ML Evaluation"]
)


class ResearchMLResultsResponse(BaseModel):
    dataset_name: str
    dataset_citation: str
    task_name: str
    model_architecture: str
    feature_count: int
    constant_features_removed: int
    classes: List[str]
    subject_split: Dict[str, int]
    validation_metrics: Dict[str, Any]
    final_test_metrics: Dict[str, Any]
    raw_test_metrics: Dict[str, Any]
    temporal_smoothing: Dict[str, Any]
    evaluation_stage: str
    is_clinical_diagnosis: bool
    limitations_note: str


VERIFIED_RESEARCH_RESULTS = {
    "dataset_name": "StrokeRehab Dataset",
    "dataset_citation": "Kaku et al., NeurIPS 2022",
    "task_name": "Five-Class Functional Primitive Recognition",
    "model_architecture": "Random Forest Classifier + Majority-Vote Temporal Smoothing",
    "feature_count": 431,
    "constant_features_removed": 1,
    "classes": ["Rest", "Reach", "Transport", "Stabilize", "Reposition"],
    "subject_split": {
        "train_subjects": 33,
        "validation_subjects": 8,
        "test_subjects": 8,
        "total_subjects": 49
    },
    "validation_metrics": {
        "accuracy": 0.6924,
        "accuracy_percent": "69.24%",
        "macro_f1": 0.6593,
        "description": "Validation set metrics across 8 subject-independent folds"
    },
    "final_test_metrics": {
        "label": "Final held-out test result",
        "accuracy": 0.6392,
        "accuracy_percent": "63.92%",
        "macro_f1": 0.6233,
        "temporal_smoothing": "Majority vote (window = 9)",
        "description": "Held-out test performance across 8 unseen subjects after temporal smoothing"
    },
    "raw_test_metrics": {
        "label": "Raw Test Result (No Smoothing)",
        "accuracy": 0.5907,
        "accuracy_percent": "59.07%",
        "macro_f1": 0.5748,
        "description": "Held-out test performance without temporal window smoothing"
    },
    "temporal_smoothing": {
        "method": "Majority Vote Window",
        "window_size": 9
    },
    "evaluation_stage": "Research-stage evaluation",
    "is_clinical_diagnosis": False,
    "limitations_note": (
        "These results are based on the released StrokeRehab video-feature representation and a subject-independent "
        "research evaluation. The released dataset does not provide raw patient video for direct reproduction of the "
        "feature extraction from arbitrary uploaded videos. Therefore, these research results are presented separately "
        "from the application's MediaPipe-based video analysis and should not be interpreted as clinical diagnostic performance."
    )
}


@router.get("/ml-results", response_model=ResearchMLResultsResponse)
async def get_research_ml_results():
    """
    Returns the verified benchmark metrics for the StrokeRehab Research ML Evaluation component.
    """
    return VERIFIED_RESEARCH_RESULTS


class CustomInferencePayload(BaseModel):
    features: List[List[float]]
    apply_smoothing: Optional[bool] = True
    window_size: Optional[int] = 9


@router.post("/predict-primitives")
async def predict_primitives(payload: CustomInferencePayload):
    """
    Inference endpoint for compatible 431/432-dimensional StrokeRehab released video features.
    Returns clear warning if input features are incompatible with the StrokeRehab model schema.
    """
    if not stroke_rehab_engine.is_loaded:
        return {
            "status": "model_unavailable",
            "message": "The StrokeRehab 431-feature model file is not available on disk. Serving verified benchmark metrics.",
            "benchmark_results": VERIFIED_RESEARCH_RESULTS
        }

    res = stroke_rehab_engine.predict_primitives(
        feature_matrix=payload.features,
        apply_smoothing=payload.apply_smoothing if payload.apply_smoothing is not None else True,
        window_size=payload.window_size or 9
    )
    return res


@router.get("/study36-reference")
async def get_study36_reference():
    """
    Returns dataset-derived healthy-control movement reference characteristics from Study36.
    """
    try:
        from backend.study36_reference import compute_study36_reference_summary
    except ImportError:
        from study36_reference import compute_study36_reference_summary

    return compute_study36_reference_summary()

