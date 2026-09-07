# Backend Integration Verification Test Script

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    print("=========================================")
    print("      REHABSHIELD DIAGNOSTIC TEST        ")
    print("=========================================")

    # Test 1: Verify Config & Fallback Database Connection
    print("\n[Test 1] Initializing Config & Database interfaces...")
    try:
      from backend.config import BASE_DIR, UPLOAD_DIR, DATABASE_DIR
      from backend.db import get_collection
      
      print(f"  - Base Directory: {BASE_DIR}")
      print(f"  - Database Directory: {DATABASE_DIR}")
      print(f"  - Uploads Directory: {UPLOAD_DIR}")
      
      users_coll = get_collection("users")
      print("  - Connection to users collection successful.")
      print("[OK] Test 1 Passed.")
    except Exception as e:
      print(f"[FAIL] Test 1 Failed: {e}")
      return False

    # Test 2: Verify Computer Vision & MediaPipe Engine
    print("\n[Test 2] Running CV Landmark & Angles simulation...")
    try:
      from backend.mp_engine import analyze_video
      result = analyze_video(video_path=None, affected_side="Right", current_status="Improving")
      
      assert "angles" in result, "Angles dictionary missing"
      assert "gait" in result, "Gait parameters missing"
      assert "landmarks" in result, "Landmarks list missing"
      assert len(result["landmarks"]) == 33, "MediaPipe keypoint count incorrect"
      
      print(f"  - Calculated Knee Flexion: {result['angles']['knee_angle_deg']} degrees")
      print(f"  - Calculated Walking Speed: {result['gait']['walking_speed_ms']} m/s")
      print(f"  - Extracted Balance Stability: {result['balance_stability_score']}%")
      print("[OK] Test 2 Passed.")
    except Exception as e:
      print(f"[FAIL] Test 2 Failed: {e}")
      return False

    # Test 3: Verify Machine Learning Classifiers
    print("\n[Test 3] Running ML Predictor and Feature Importance mappings...")
    try:
      from backend.ml_engine import predict_impairment
      
      # Mock features
      mock_features = {
        "angles": {
          "hip_angle_deg": 35.0,
          "knee_angle_deg": 48.0,
          "shoulder_angle_deg": 28.0,
          "elbow_angle_deg": 120.0
        },
        "gait": {
          "stride_length_m": 0.55,
          "cadence_steps_min": 78.0,
          "walking_speed_ms": 0.65,
          "step_width_m": 0.22,
          "step_symmetry_ratio": 0.78
        },
        "arm_swing_deg": 18.0,
        "rom_score": 52.0,
        "balance_stability_score": 60.0
      }
      
      rf_pred = predict_impairment(mock_features, "Random Forest")
      svm_pred = predict_impairment(mock_features, "SVM")
      xgb_pred = predict_impairment(mock_features, "XGBoost")
      
      print(f"  - RF Impairment prediction: {rf_pred['impairment_level']} (Confidence: {rf_pred['confidence']})")
      print(f"  - SVM Impairment prediction: {svm_pred['impairment_level']} (Confidence: {svm_pred['confidence']})")
      print(f"  - XGBoost Impairment prediction: {xgb_pred['impairment_level']} (Confidence: {xgb_pred['confidence']})")
      
      # Check feature importance counts
      assert len(rf_pred["feature_importances"]) > 0, "Feature importances are empty"
      print(f"  - Primary Gait Feature: {list(rf_pred['feature_importances'].keys())[0]}")
      
      print("[OK] Test 3 Passed.")
    except Exception as e:
      print(f"[FAIL] Test 3 Failed: {e}")
      return False

    print("\n=========================================")
    print("      ALL DIAGNOSTIC TESTS PASSED        ")
    print("=========================================")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
