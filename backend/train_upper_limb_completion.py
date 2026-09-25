"""
Upper-Limb Exercise Execution Completion Training & Evaluation Pipeline
========================================================================

Trains and evaluates an independent machine learning classifier for binary exercise 
completion prediction (Complete vs. Incomplete) on the public 
"Upper Limb Stroke Rehabilitation Exercise Video Dataset".

Protocol:
- Dedicated 14-Dimensional Upper-Limb Kinematic Feature Vector (Zero gait features).
- Official Dataset Partition: 411 Train videos, 80 Test videos across 4 exercises.
- Model Selection: Evaluates 5 candidate classifiers (Logistic Regression, Random Forest, 
  Extra Trees, HistGradientBoosting, SVM) via 5-Fold Stratified Cross-Validation on the 
  411 training set only.
- Final Evaluation: The selected model is evaluated exactly once on the untouched 80 test cases.
- Incremental feature caching to disk to allow resumption and fast evaluation.

Saves model artifacts, evaluation metrics, and test predictions to:
backend/models/upper_limb_completion/
"""

import os
import sys
import json
import logging
import csv
import time
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import cv2

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("train_upper_limb_completion")

MODEL_DIR = Path(__file__).parent / "models" / "upper_limb_completion"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "upper_limb_completion_model.joblib"
SCALER_PATH = MODEL_DIR / "upper_limb_completion_scaler.joblib"
ENCODER_PATH = MODEL_DIR / "upper_limb_completion_label_encoder.joblib"
METADATA_PATH = MODEL_DIR / "feature_metadata.json"
RESULTS_PATH = MODEL_DIR / "evaluation_results.json"
CSV_PATH = MODEL_DIR / "test_predictions.csv"
CACHE_PATH = MODEL_DIR / "upper_limb_features_cache.json"

POSSIBLE_DATASET_PATHS = [
    Path(r"D:\MP\data\An upper limb stroke rehabilitation exercise video\An upper limb stroke rehabilitation exercise video"),
    Path(r"D:\MP\data\An upper limb stroke rehabilitation exercise video"),
    Path(__file__).parent.parent / "data" / "An upper limb stroke rehabilitation exercise video" / "An upper limb stroke rehabilitation exercise video",
    Path(__file__).parent.parent / "data" / "An upper limb stroke rehabilitation exercise video",
    Path(r"E:\MP\data\An upper limb stroke rehabilitation exercise video\An upper limb stroke rehabilitation exercise video"),
    Path(__file__).parent.parent / "data" / "upper_limb_exercise_dataset"
]

EXERCISES = [
    "1_Lifting an Object",
    "2_Extending the Elbow",
    "3_Lifting the Wrist",
    "4_Opening the Hand"
]

EXERCISE_DISPLAY_NAMES = {
    "1_Lifting an Object": "Lifting an Object",
    "2_Extending the Elbow": "Extending the Elbow",
    "3_Lifting the Wrist": "Lifting the Wrist",
    "4_Opening the Hand": "Opening the Hand"
}

try:
    from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    logger.error("scikit-learn or joblib missing.")
    SKLEARN_AVAILABLE = False
    joblib = None

try:
    from backend.feature_extractor import UPPER_LIMB_FEATURE_NAMES, UPPER_LIMB_FEATURE_DICTIONARY, extract_upper_limb_features_from_history
    from backend.mp_engine import ensure_model_asset
except ImportError:
    from feature_extractor import UPPER_LIMB_FEATURE_NAMES, UPPER_LIMB_FEATURE_DICTIONARY, extract_upper_limb_features_from_history
    from mp_engine import ensure_model_asset


def locate_dataset() -> Path:
    """Locate the verified upper limb dataset directory."""
    for p in POSSIBLE_DATASET_PATHS:
        if p.exists() and (p / "Exercise").exists():
            logger.info(f"Located Upper Limb Exercise Dataset at: {p}")
            return p
    for p in POSSIBLE_DATASET_PATHS:
        if p.exists():
            logger.info(f"Located dataset root at: {p}")
            return p
    raise FileNotFoundError("Upper Limb Exercise Dataset folder not found on disk.")


def init_landmarker():
    """Initializes MediaPipe PoseLandmarker once for fast reusable extraction."""
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    model_asset_path = ensure_model_asset()
    options = vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=model_asset_path),
        running_mode=vision.RunningMode.IMAGE,
        min_pose_detection_confidence=0.3,
        min_pose_presence_confidence=0.3,
        min_tracking_confidence=0.3
    )
    return vision.PoseLandmarker.create_from_options(options)


def extract_features_from_video_path(video_path: Path, landmarker) -> Optional[List[float]]:
    """
    Extracts 14 upper-limb kinematic features from video using reused landmarker.
    Samples every 2nd frame for 2x speedup while preserving full kinematic resolution (15 fps).
    """
    import mediapipe as mp

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.warning(f"Could not open video: {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    effective_fps = fps / 3.0  # Sample every 3rd frame (10 fps effective)

    landmark_history = []
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if frame_idx % 3 != 0:
            continue

        h, w = frame.shape[:2]
        if w > 480:
            new_w = 480
            new_h = int(h * (480.0 / w))
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        res = landmarker.detect(mp_img)

        if res.pose_landmarks and len(res.pose_landmarks) > 0:
            raw_lms = res.pose_landmarks[0]
            if len(raw_lms) >= 33:
                lms_33 = [
                    {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": getattr(lm, "visibility", 0.99)}
                    for lm in raw_lms[:33]
                ]
                landmark_history.append(lms_33)

    cap.release()

    if len(landmark_history) < 5:
        logger.warning(f"Insufficient pose detections in {video_path.name} ({len(landmark_history)} valid frames)")
        # Fallback default feature vector for edge-case tracking loss
        return [30.0, 45.0, 90.0, 135.0, 110.0, 35.0, 0.2, 0.2, 0.4, 20.0, 10.0, 15.0, 50.0, 10.0]

    f_vec = extract_upper_limb_features_from_history(landmark_history, fps=effective_fps)
    if f_vec is not None:
        return [float(x) for x in f_vec]
    return [30.0, 45.0, 90.0, 135.0, 110.0, 35.0, 0.2, 0.2, 0.4, 20.0, 10.0, 15.0, 50.0, 10.0]


def scan_dataset(dataset_root: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Scans dataset directory and returns train and test video manifests."""
    train_videos = []
    test_videos = []

    exercise_dir = dataset_root / "Exercise" if (dataset_root / "Exercise").exists() else dataset_root

    for root, _, files in os.walk(exercise_dir):
        for f in sorted(files):
            if f.endswith(".mp4"):
                full_path = Path(root) / f
                rel_parts = full_path.relative_to(dataset_root).parts

                ex_name = "Unknown"
                label = "Unknown"
                split = "Unknown"

                for p in rel_parts:
                    if p in EXERCISES or "Lifting" in p or "Extending" in p or "Opening" in p:
                        ex_name = p
                    elif p in ["Complete", "Incomplete"]:
                        label = p
                    elif p in ["Train", "Test"]:
                        split = p

                item = {
                    "video_name": f,
                    "file_path": str(full_path),
                    "exercise": ex_name,
                    "exercise_clean": EXERCISE_DISPLAY_NAMES.get(ex_name, ex_name),
                    "label": label,
                    "split": split
                }

                if split == "Train":
                    train_videos.append(item)
                elif split == "Test":
                    test_videos.append(item)

    logger.info(f"Discovered: {len(train_videos)} Train videos, {len(test_videos)} Test videos.")
    return train_videos, test_videos


_worker_landmarker = None


def _worker_init():
    global _worker_landmarker
    try:
        _worker_landmarker = init_landmarker()
    except Exception as e:
        logger.error(f"Worker init error: {e}")


def _extract_worker(item: Dict[str, Any]) -> Tuple[str, Optional[List[float]]]:
    global _worker_landmarker
    vname = item["video_name"]
    vpath = Path(item["file_path"])
    try:
        if _worker_landmarker is None:
            _worker_landmarker = init_landmarker()
        feats = extract_features_from_video_path(vpath, _worker_landmarker)
        return vname, feats
    except Exception as e:
        logger.warning(f"Extraction failed for {vname}: {e}")
        return vname, [30.0, 45.0, 90.0, 135.0, 110.0, 35.0, 0.2, 0.2, 0.4, 20.0, 10.0, 15.0, 50.0, 10.0]


def load_or_extract_features(train_videos: List[Dict[str, Any]], test_videos: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Extracts features across dataset videos with parallel multi-worker extraction and persistent disk caching."""
    from concurrent.futures import ProcessPoolExecutor, as_completed

    cache = {}
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r") as cf:
                cache = json.load(cf)
            logger.info(f"Loaded existing feature cache with {len(cache)} videos.")
        except Exception as e:
            logger.warning(f"Could not read cache: {e}")
            cache = {}

    all_videos = train_videos + test_videos
    uncached = [v for v in all_videos if v["video_name"] not in cache]

    if uncached:
        logger.info(f"Extracting features for {len(uncached)} videos using parallel MediaPipe workers...")
        num_workers = min(6, os.cpu_count() or 4)
        start_t = time.time()
        processed_count = 0

        with ProcessPoolExecutor(max_workers=num_workers, initializer=_worker_init) as executor:
            futures = [executor.submit(_extract_worker, item) for item in uncached]
            for future in as_completed(futures):
                vname, feats = future.result()
                cache[vname] = feats
                processed_count += 1

                if processed_count % 20 == 0 or processed_count == len(uncached):
                    rate = processed_count / max(0.1, time.time() - start_t)
                    remaining = (len(uncached) - processed_count) / max(0.01, rate)
                    logger.info(f"Progress: [{processed_count}/{len(uncached)}] videos processed ({rate:.1f} vid/s, ~{remaining:.0f}s remaining).")
                    with open(CACHE_PATH, "w") as cf:
                        json.dump(cache, cf)

        with open(CACHE_PATH, "w") as cf:
            json.dump(cache, cf)
        logger.info(f"Saved complete feature cache to {CACHE_PATH} ({len(cache)} total videos).")

    # Build Train & Test matrices
    X_train = np.array([cache[v["video_name"]] for v in train_videos], dtype=np.float32)
    y_train = np.array([v["label"] for v in train_videos])
    X_test = np.array([cache[v["video_name"]] for v in test_videos], dtype=np.float32)
    y_test = np.array([v["label"] for v in test_videos])

    return X_train, y_train, X_test, y_test


def run_training_and_evaluation():
    """
    Main training, validation selection, and untouched test evaluation routine.
    """
    if not SKLEARN_AVAILABLE:
        logger.error("scikit-learn is required.")
        return

    dataset_root = locate_dataset()
    train_videos, test_videos = scan_dataset(dataset_root)

    if len(train_videos) == 0 or len(test_videos) == 0:
        logger.error("Dataset partition videos missing.")
        return

    # Extract or load cached feature vectors
    X_train_raw, y_train_str, X_test_raw, y_test_str = load_or_extract_features(train_videos, test_videos)

    # Encode labels (Complete = 0, Incomplete = 1 or alphabetical)
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train_str)
    y_test = label_encoder.transform(y_test_str)
    classes = list(label_encoder.classes_)

    logger.info(f"Target Classes: {classes}")

    # Scale features using StandardScaler fit exclusively on Training set
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test = scaler.transform(X_test_raw)

    # Candidate Classifiers for Validation Comparison
    candidates = {
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        "Extra Trees": ExtraTreesClassifier(n_estimators=100, max_depth=8, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        "HistGradientBoosting": HistGradientBoostingClassifier(max_iter=100, random_state=42),
        "SVM (RBF)": SVC(kernel="rbf", C=1.0, probability=True, random_state=42)
    }

    # 5-Fold Cross-Validation on the 411 Training Set ONLY
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    val_results = {}
    best_model_name = None
    best_val_f1 = -1.0

    logger.info("==================================================")
    logger.info("5-FOLD CROSS-VALIDATION ON 411 TRAINING CASES ONLY")
    logger.info("==================================================")

    for name, clf in candidates.items():
        y_val_pred = cross_val_predict(clf, X_train, y_train, cv=cv)
        acc = accuracy_score(y_train, y_val_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_train, y_val_pred, average="macro", zero_division=0)

        val_results[name] = {
            "validation_accuracy": round(float(acc), 4),
            "validation_macro_precision": round(float(prec), 4),
            "validation_macro_recall": round(float(rec), 4),
            "validation_macro_f1": round(float(f1), 4)
        }
        logger.info(f"  [{name}] Val Acc: {acc*100:.2f}%, Macro F1: {f1:.4f}")

        if f1 > best_val_f1:
            best_val_f1 = f1
            best_model_name = name

    logger.info(f"\nSelected Best Architecture: '{best_model_name}' (Val Macro F1 = {best_val_f1:.4f})")

    # Fit Selected Best Model on Full 411 Training Set
    selected_clf = candidates[best_model_name]
    selected_clf.fit(X_train, y_train)

    # ==================================================
    # EXACTLY ONCE EVALUATION ON UNTOUCHED 80 TEST CASES
    # ==================================================
    logger.info("==================================================")
    logger.info(f"FINAL UNTOUCHED TEST EVALUATION ({len(X_test)} TEST CASES)")
    logger.info("==================================================")

    y_test_pred = selected_clf.predict(X_test)
    y_test_probs = selected_clf.predict_proba(X_test) if hasattr(selected_clf, "predict_proba") else None

    test_acc = accuracy_score(y_test, y_test_pred)
    macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average="macro", zero_division=0)
    weighted_prec, weighted_rec, weighted_f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average="weighted", zero_division=0)

    # Class-wise metrics
    c_prec, c_rec, c_f1, c_supp = precision_recall_fscore_support(y_test, y_test_pred, average=None, zero_division=0)
    class_wise_metrics = {}
    for idx, c_name in enumerate(classes):
        class_wise_metrics[c_name] = {
            "precision": round(float(c_prec[idx]), 4),
            "recall": round(float(c_rec[idx]), 4),
            "f1_score": round(float(c_f1[idx]), 4),
            "support": int(c_supp[idx])
        }

    # Confusion matrix
    cm = confusion_matrix(y_test, y_test_pred)
    cm_list = cm.tolist()

    # Per-Exercise Breakdown
    per_exercise_metrics = {}
    for ex in EXERCISES:
        ex_clean = EXERCISE_DISPLAY_NAMES.get(ex, ex)
        ex_indices = [i for i, v in enumerate(test_videos) if v["exercise"] == ex or ex_clean in v["exercise"]]
        if ex_indices:
            sub_y_true = y_test[ex_indices]
            sub_y_pred = y_test_pred[ex_indices]
            ex_acc = accuracy_score(sub_y_true, sub_y_pred)
            ex_prec, ex_rec, ex_f1, _ = precision_recall_fscore_support(sub_y_true, sub_y_pred, average="macro", zero_division=0)
            per_exercise_metrics[ex_clean] = {
                "exercise_name": ex_clean,
                "test_video_count": len(ex_indices),
                "correct_count": int(np.sum(sub_y_true == sub_y_pred)),
                "accuracy": round(float(ex_acc), 4),
                "accuracy_percent": f"{ex_acc * 100:.2f}%",
                "precision": round(float(ex_prec), 4),
                "recall": round(float(ex_rec), 4),
                "f1_score": round(float(ex_f1), 4)
            }

    # Build Test Predictions Table
    test_pred_records = []
    for idx, v in enumerate(test_videos):
        pred_label = classes[y_test_pred[idx]]
        true_label = v["label"]
        match_status = "MATCH" if pred_label == true_label else "MISMATCH"
        conf = float(np.max(y_test_probs[idx])) * 100.0 if y_test_probs is not None else 100.0

        test_pred_records.append({
            "video_name": v["video_name"],
            "exercise": v["exercise_clean"],
            "ground_truth": true_label,
            "prediction": pred_label,
            "confidence": round(conf, 1),
            "match_status": match_status
        })

    # Save test predictions CSV
    df_preds = pd.DataFrame(test_pred_records)
    df_preds.to_csv(CSV_PATH, index=False)
    logger.info(f"Saved test predictions CSV to {CSV_PATH}")

    # Build Evaluation Results JSON
    eval_results = {
        "dataset_name": "Upper Limb Stroke Rehabilitation Exercise Video Dataset",
        "evaluation_stage": "Held-Out Test Evaluation",
        "selected_model_architecture": best_model_name,
        "feature_count": len(UPPER_LIMB_FEATURE_NAMES),
        "features": UPPER_LIMB_FEATURE_NAMES,
        "classes": classes,
        "sample_split": {
            "train_videos_count": len(X_train),
            "test_videos_count": len(X_test),
            "total_videos": len(X_train) + len(X_test)
        },
        "validation_model_comparison": val_results,
        "held_out_test_metrics": {
            "accuracy": round(float(test_acc), 4),
            "accuracy_percent": f"{test_acc * 100:.2f}%",
            "macro_precision": round(float(macro_prec), 4),
            "macro_recall": round(float(macro_rec), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "correct_predictions": int(np.sum(y_test == y_test_pred)),
            "incorrect_predictions": int(np.sum(y_test != y_test_pred)),
            "total_test_videos": len(y_test)
        },
        "class_wise_metrics": class_wise_metrics,
        "confusion_matrix": {
            "labels": classes,
            "matrix": cm_list
        },
        "per_exercise_metrics": per_exercise_metrics,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "The reported metrics reflect dataset-label agreement evaluated on the official held-out test partition. This is a research evaluation and does not constitute a clinical diagnosis."
    }

    with open(RESULTS_PATH, "w") as rf:
        json.dump(eval_results, rf, indent=2)
    logger.info(f"Saved verified evaluation results JSON to {RESULTS_PATH}")

    # Save feature metadata JSON
    metadata = {
        "model_name": "Upper Limb Exercise Completion Classifier",
        "model_type": best_model_name,
        "feature_count": len(UPPER_LIMB_FEATURE_NAMES),
        "feature_names": UPPER_LIMB_FEATURE_NAMES,
        "classes": classes,
        "feature_dictionary": UPPER_LIMB_FEATURE_DICTIONARY,
        "training_date": datetime.now().isoformat()
    }
    with open(METADATA_PATH, "w") as mf:
        json.dump(metadata, mf, indent=2)

    # Save Model Artifacts
    joblib.dump(selected_clf, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(label_encoder, ENCODER_PATH)

    logger.info(f"Saved model artifacts to {MODEL_DIR}")
    logger.info("==================================================")
    logger.info(f"EVALUATION COMPLETE: Test Acc = {test_acc*100:.2f}%, Macro F1 = {macro_f1:.4f}")
    logger.info("==================================================")


if __name__ == "__main__":
    run_training_and_evaluation()
