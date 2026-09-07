from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any, Dict
from backend.db import get_collection
from backend.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["Progress & Recovery Analytics"])

@router.get("/{patient_id}")
def get_patient_progress(patient_id: str, current_user: dict = Depends(get_current_user)) -> Any:
    assessments_coll = get_collection("assessments")
    patients_coll = get_collection("patients")
    
    # 1. Verify patient exists
    patient = patients_coll.find_one({"patient_id": patient_id})
    if not patient:
        patient = patients_coll.find_one({"_id": patient_id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        patient_id = patient["patient_id"]

    # 2. Retrieve all assessments for patient sorted by session number
    sessions = list(assessments_coll.find({"patient_id": patient_id}))
    sessions = sorted(sessions, key=lambda x: x.get("session_number", 0))

    if not sessions:
        return {
            "session_count": 0,
            "improvement_pct": 0.0,
            "overall_status": "No sessions logged",
            "recovery_timeline": [],
            "recent_comparison": {}
        }

    # 3. Calculate recovery timeline points
    recovery_timeline = []
    
    # Map impairment levels to a general numeric score for simple charts
    impairment_to_score = {
        "Very Severe": 20,
        "Severe": 40,
        "Moderate": 65,
        "Mild": 85,
        "Normal": 98
    }

    for idx, s in enumerate(sessions):
        feats = s.get("extracted_features", {})
        gait = feats.get("gait", {})
        angles = feats.get("angles", {})
        
        # Calculate a normalized upper limb mobility score (shoulder ROM + elbow angle normalized)
        # Shoulder range of motion can go from 10 to 60 deg
        sh_rom = feats.get("arm_swing_deg", 20.0)
        sh_mobility_score = min(100.0, (sh_rom / 50.0) * 100)
        
        # Elbow angle (closer to 150-180 is better, stroke elbow spastic flexion is around 90-110)
        el_ang = angles.get("elbow_angle_deg", 120.0)
        el_flexion_deficit_score = min(100.0, (el_ang / 160.0) * 100)
        
        upper_limb_score = round((sh_mobility_score + el_flexion_deficit_score) / 2.0, 1)

        # Calculate a generalized Motor Score out of 100 based on joint rom and walking parameters
        motor_score = round(
            (gait.get("walking_speed_ms", 0.5) / 1.3 * 30) + 
            (feats.get("balance_stability_score", 50.0) / 100 * 30) + 
            (feats.get("rom_score", 40.0) / 75 * 20) + 
            (upper_limb_score / 100 * 20),
            1
        )
        motor_score = min(100.0, max(0.0, motor_score))

        recovery_timeline.append({
            "session_number": s["session_number"],
            "assessment_date": s["assessment_date"][:10],
            "walking_speed": round(gait.get("walking_speed_ms", 0.0), 2),
            "balance": round(feats.get("balance_stability_score", 0.0), 1),
            "hip_angle": round(angles.get("hip_angle_deg", 0.0), 1),
            "knee_angle": round(angles.get("knee_angle_deg", 0.0), 1),
            "shoulder_mobility": round(sh_rom, 1),
            "upper_limb_movement": upper_limb_score,
            "overall_motor_score": motor_score,
            "impairment_level": s["predictions"]["impairment_level"]
        })

    # 4. Compare first vs last session to calculate improvement %
    improvement_pct = 0.0
    recent_comparison = {}
    
    if len(sessions) >= 1:
        first = recovery_timeline[0]
        last = recovery_timeline[-1]
        
        # Overall motor score improvement
        first_score = first["overall_motor_score"]
        last_score = last["overall_motor_score"]
        
        if first_score > 0:
            improvement_pct = round(((last_score - first_score) / first_score) * 100, 1)
        else:
            improvement_pct = 0.0
            
        recent_comparison = {
            "walking_speed": {
                "initial": first["walking_speed"],
                "current": last["walking_speed"],
                "diff": round(last["walking_speed"] - first["walking_speed"], 2),
                "improvement_pct": round(((last["walking_speed"] - first["walking_speed"]) / first["walking_speed"] * 100), 1) if first["walking_speed"] > 0 else 0.0
            },
            "balance": {
                "initial": first["balance"],
                "current": last["balance"],
                "diff": round(last["balance"] - first["balance"], 1),
                "improvement_pct": round(((last["balance"] - first["balance"]) / first["balance"] * 100), 1) if first["balance"] > 0 else 0.0
            },
            "knee_angle": {
                "initial": first["knee_angle"],
                "current": last["knee_angle"],
                "diff": round(last["knee_angle"] - first["knee_angle"], 1),
                "improvement_pct": round(((last["knee_angle"] - first["knee_angle"]) / first["knee_angle"] * 100), 1) if first["knee_angle"] > 0 else 0.0
            },
            "upper_limb_movement": {
                "initial": first["upper_limb_movement"],
                "current": last["upper_limb_movement"],
                "diff": round(last["upper_limb_movement"] - first["upper_limb_movement"], 1),
                "improvement_pct": round(((last["upper_limb_movement"] - first["upper_limb_movement"]) / first["upper_limb_movement"] * 100), 1) if first["upper_limb_movement"] > 0 else 0.0
            },
            "overall_motor_score": {
                "initial": first_score,
                "current": last_score,
                "diff": round(last_score - first_score, 1),
                "improvement_pct": improvement_pct
            }
        }

    # Recovery status assessment
    if len(sessions) < 2:
        status_text = "Baseline session logged. Awaiting subsequent assessments."
    elif improvement_pct > 15:
        status_text = "Significant functional recovery demonstrated."
    elif improvement_pct > 3:
        status_text = "Gradual motor improvement observed."
    elif improvement_pct >= -3:
        status_text = "Condition stable. Check range of motion fluctuations."
    else:
        status_text = "Motor regression detected. Review physical therapy plan."

    return {
        "patient_id": patient_id,
        "name": patient["name"],
        "session_count": len(sessions),
        "improvement_pct": improvement_pct,
        "overall_status": status_text,
        "recovery_timeline": recovery_timeline,
        "recent_comparison": recent_comparison
    }
