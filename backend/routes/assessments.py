import os
import shutil
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

logger = logging.getLogger("assessments_route")
from backend.db import get_collection
from backend.schemas import AssessmentResponse, AssessmentCreate, DirectAssessmentCreate, ClinicalScores, MovementFeatures
from backend.auth import require_therapist_or_doctor, get_current_user
from backend.config import UPLOAD_DIR
from backend.mp_engine import analyze_video
from backend.ml_engine import predict_impairment

router = APIRouter(prefix="/assessments", tags=["Assessments & Processing"])

def generate_recommendations(features: dict) -> List[str]:
    """Generate professional physiotherapeutic recommendations based on objective metrics."""
    recs = []
    
    # 1. Joint angles
    knee = features["angles"]["knee_angle_deg"]
    hip = features["angles"]["hip_angle_deg"]
    elbow = features["angles"]["elbow_angle_deg"]
    shoulder = features["angles"]["shoulder_angle_deg"]
    
    if knee < 45:
        recs.append("Reduced Knee Flexion: Consider knee mobility exercises (heel slides, seated active extensions) to improve swing-phase clearance.")
    if hip < 28:
        recs.append("Reduced Hip Extension/Flexion: Focus on hip flexor strengthening and standing marching exercises to increase step length.")
    if elbow < 130:
        recs.append("Flexor Spasticity Pattern (Elbow Flexed): Focus on bicep stretching, active elbow extensions, and reach-and-grasp exercises.")
    if shoulder < 32:
        recs.append("Reduced Shoulder Range of Motion: Integrate active-assisted arm elevations, pulley exercises, and wall-climbing exercises.")

    # 2. Gait parameters
    speed = features["gait"]["walking_speed_ms"]
    symmetry = features["gait"]["step_symmetry_ratio"]
    balance = features["balance_stability_score"]
    arm_swing = features["arm_swing_deg"]
    
    if speed < 0.6:
        recs.append("Low Walking Speed: Recommend body-weight supported treadmill training (BWSTT) and cadence-paced walking trials.")
    if symmetry < 0.8:
        recs.append("Gait Asymmetry: Utilize metronome-guided step timing (rhythmic auditory stimulation) and weight-shifting practice on the affected leg.")
    if balance < 65:
        recs.append("Reduced Balance Stability: Prescribe standing balance trials (single-leg stand, tandem gait, weight transfer) with safety railings.")
    if arm_swing < 15:
        recs.append("Reduced Upper Limb Swing: Encourage bilateral arm swing during walking using walking poles or visual feedback.")

    if not recs:
        recs.append("Maintain current activity: General endurance and strength maintenance exercises recommended.")

    # Always append clinician disclaimer
    recs.append("Final treatment decisions should be made by qualified healthcare professionals.")
    return recs

def generate_prescribed_exercises(features: dict, affected_side: str = "Right") -> List[dict]:
    """Generate structured, evidence-based exercise prescriptions based on measured kinematics."""
    exercises = []
    angles = features.get("angles", {})
    gait = features.get("gait", {})
    
    knee = angles.get("knee_angle_deg", 60.0)
    hip = angles.get("hip_angle_deg", 45.0)
    elbow = angles.get("elbow_angle_deg", 140.0)
    shoulder = angles.get("shoulder_angle_deg", 40.0)
    
    speed = gait.get("walking_speed_ms", 0.8)
    symmetry = gait.get("step_symmetry_ratio", 0.9)
    balance = features.get("balance_stability_score", 75.0)
    arm_swing = features.get("arm_swing_deg", 20.0)

    # 1. Lower Limb / Knee Clearance
    if knee < 45:
        exercises.append({
            "title": "Active-Assisted Heel Slides & Seated Quadriceps Sets",
            "category": "Lower Limb",
            "target_deficit": f"Reduced Knee Flexion ({knee:.1f}° vs Target >55.0°)",
            "dosage": "3 sets × 10 repetitions, 2x daily",
            "intensity": "Active-Assisted",
            "instructions": "Lie supine or sit supported. Slowly slide the heel toward the buttocks to bend the knee, hold for 3 seconds, then slide back to full extension. Use a towel or strap around the foot if assistance is needed.",
            "clinical_rationale": f"Measured knee flexion is limited to {knee:.1f}°, causing foot drag and compensatory circumduction during the swing phase. Promotes hamstring activation and knee joint mobility."
        })
    elif knee < 55:
        exercises.append({
            "title": "Seated Active Terminal Knee Extensions with TheraBand",
            "category": "Lower Limb",
            "target_deficit": f"Mild Knee Flexion Deficit ({knee:.1f}°)",
            "dosage": "3 sets × 12 repetitions, 1x daily",
            "intensity": "Active",
            "instructions": "Sit upright on a stable chair with a resistance band around the ankle. Straighten the affected leg fully against resistance, hold for 2 seconds at peak extension, and lower slowly.",
            "clinical_rationale": "Strengthens vastus medialis and quadriceps to stabilize the knee during initial contact and early stance."
        })

    # 2. Upper Limb / Flexor Spasticity & Contracture
    if elbow < 130:
        exercises.append({
            "title": "Sustained Biceps Lengthening & Tabletop Reach-and-Grasp",
            "category": "Upper Limb",
            "target_deficit": f"Upper-Limb Flexor Synergy / Elbow Angle ({elbow:.1f}° vs Target >145.0°)",
            "dosage": "3 sets × 8 reach trials (with 20s stretch holds)",
            "intensity": "Active-Assisted",
            "instructions": "Rest the affected arm on a smooth table. Interlock fingers with the sound hand to guide the affected arm forward into full elbow extension. Practice reaching for and grasping light foam cups.",
            "clinical_rationale": f"Significant flexor spasticity detected (elbow angle {elbow:.1f}°). Sustained stretching inhibits hypertonia while active reach promotes cortical motor neuroplasticity."
        })
    elif elbow < 145:
        exercises.append({
            "title": "Bilateral Symmetrical Arm Reach with Lightweight Ball",
            "category": "Upper Limb",
            "target_deficit": f"Submaximal Elbow Extension ({elbow:.1f}°)",
            "dosage": "3 sets × 10 repetitions, 1x daily",
            "intensity": "Active",
            "instructions": "Hold a lightweight ball with both hands in front of the chest. Push the ball forward and upward at a 45-degree angle, focusing on equal arm extension, then return slowly.",
            "clinical_rationale": "Encourages bimanual coordination and voluntary extension through bilateral movement reinforcement."
        })

    # 3. Hip Mobility & Step Length
    if hip < 28:
        exercises.append({
            "title": "Standing High-Knee Marching with Support & Gluteal Bridges",
            "category": "Core & Pelvic Control",
            "target_deficit": f"Reduced Hip Mobility ({hip:.1f}° vs Target >35.0°)",
            "dosage": "3 sets × 10 repetitions per leg",
            "intensity": "Active",
            "instructions": "Stand facing a sturdy rail or counter. Lift the affected knee upward toward hip level in a controlled march, hold for 1 second, and lower slowly. Perform bridging exercises while lying supine.",
            "clinical_rationale": f"Hip range of motion was measured at {hip:.1f}°. Strengthening iliopsoas and gluteal muscles directly increases forward step stride and pelvic stability."
        })

    # 4. Balance Stability & Trunk Sway
    if balance < 65:
        exercises.append({
            "title": "Tandem Stance & Weight-Shifting Protocol with Safety Railings",
            "category": "Balance & Stability",
            "target_deficit": f"Elevated Lateral Trunk Sway / Balance Score ({balance:.1f}%)",
            "dosage": "3 sets × 30-second holds",
            "intensity": "Active-Assisted",
            "instructions": "Stand with one foot directly in front of the other (heel-to-toe) near a counter. Maintain balance for 30 seconds without leaning. Practice slow side-to-side weight shifting.",
            "clinical_rationale": f"Trunk balance stability is {balance:.1f}%, indicating elevated fall risk. Static and dynamic balance retraining improves vestibular-somatosensory integration."
        })
    elif balance < 80:
        exercises.append({
            "title": "Single-Leg Stance & Foam Pad Balance Trials",
            "category": "Balance & Stability",
            "target_deficit": f"Mild Dynamic Balance Asymmetry ({balance:.1f}%)",
            "dosage": "3 sets × 20 seconds per side",
            "intensity": "Active",
            "instructions": "Stand on a firm surface or balance pad. Lift the healthy foot slightly off the ground, balancing on the affected limb while lightly touching a rail for safety.",
            "clinical_rationale": "Enhances proprioceptive feedback and ankle stabilizer muscle activation."
        })

    # 5. Gait Symmetry & Cadence
    if symmetry < 0.80:
        exercises.append({
            "title": "Rhythmic Auditory Cued Step Synchronization (Metronome Walk)",
            "category": "Gait & Symmetry",
            "target_deficit": f"Marked Step Asymmetry Ratio ({symmetry:.2f} vs Ideal 1.0)",
            "dosage": "10-15 minutes continuous paced walk",
            "intensity": "Progressive Resistance",
            "instructions": "Walk along a designated straight corridor while synchronizing foot strikes to an auditory metronome set at patient's baseline cadence (e.g. 60-70 bpm). Ensure equal stance time on both legs.",
            "clinical_rationale": f"Step symmetry ratio of {symmetry:.2f} reflects prolonged stance on the healthy limb. Rhythmic auditory stimulation restores bilateral temporal symmetry."
        })

    # 6. Walking Speed & Aerobic Ambulation
    if speed < 0.60:
        exercises.append({
            "title": "Body-Weight Supported Paced Interval Walking",
            "category": "Gait & Symmetry",
            "target_deficit": f"Reduced Walking Speed ({speed:.2f} m/s vs Community Target >0.8 m/s)",
            "dosage": "2 intervals of 10 minutes (rest as needed)",
            "intensity": "Active",
            "instructions": "Perform structured walking intervals in a quiet, well-lit hallway with assistive device. Focus on pushing off with the toes and lifting the affected foot cleanly.",
            "clinical_rationale": f"Walking velocity is {speed:.2f} m/s (household ambulator range). Progressive velocity training increases cardiovascular endurance and functional independence."
        })

    # 7. Shoulder Range & Arm Swing
    if shoulder < 32 or arm_swing < 15:
        exercises.append({
            "title": "Active-Assisted Shoulder Pulley & Reciprocal Arm Swing",
            "category": "Upper Limb",
            "target_deficit": f"Reduced Shoulder Swing ({shoulder:.1f}°) & Gait Arm Swing ({arm_swing:.1f}°)",
            "dosage": "3 sets × 12 elevations",
            "intensity": "Active-Assisted",
            "instructions": "Use an overhead door pulley or cane. Use the sound hand to pull downward, gently elevating the affected arm upward into flexion without causing pain. Practice swinging arms while marching.",
            "clinical_rationale": "Prevents glenohumeral capsular stiffness (frozen shoulder) and restores natural trunk-pelvic counter-rotation during walking."
        })

    if not exercises:
        exercises.append({
            "title": "General Functional Maintenance & Endurance Program",
            "category": "General Mobility",
            "target_deficit": "Maintenance of Functional Status",
            "dosage": "20-30 minutes daily",
            "intensity": "Active",
            "instructions": "Maintain regular daily walking, gentle full-body range of motion stretches, and light resistance band exercises.",
            "clinical_rationale": "Patient exhibits near-normal biomechanical parameters. Maintenance prevents secondary deconditioning."
        })

    return exercises

@router.post("", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    patient_id: str = Form(...),
    session_number: int = Form(...),
    fma_score: int = Form(0),
    bbs_score: int = Form(0),
    fac_score: int = Form(0),
    tug_score: float = Form(0.0),
    model_used: str = Form("Random Forest"),
    therapist_notes: str = Form(""),
    video: Optional[UploadFile] = File(None),
    current_user: dict = Depends(require_therapist_or_doctor)
) -> Any:
    patients_coll = get_collection("patients")
    assessments_coll = get_collection("assessments")
    
    # 1. Verify patient exists
    patient = patients_coll.find_one({"patient_id": patient_id})
    if not patient:
        patient = patients_coll.find_one({"_id": patient_id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        patient_id = patient["patient_id"] # normalize

    # 2. Save video if uploaded
    if not video or not video.filename:
        raise HTTPException(
            status_code=400, 
            detail="No video file uploaded. Please select a walking video file to perform movement analysis."
        )

    filename = f"{patient_id}_session_{session_number}_{uuid.uuid4().hex[:6]}_{video.filename}"
    save_path = UPLOAD_DIR / filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    video_path = f"uploads/{filename}"

    # 3. Process video using MediaPipe Engine
    actual_path = str(UPLOAD_DIR.parent / video_path)
    
    try:
        features = analyze_video(actual_path)
    except ValueError as ve:
        logger.warning(f"Video analysis validation error for {actual_path}: {ve}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except RuntimeError as re:
        logger.error(f"Pose model initialization error for {actual_path}: {re}")
        raise HTTPException(
            status_code=500,
            detail=f"Pose model could not be initialized: {str(re)}"
        )
    except Exception as e:
        logger.exception(f"Video processing failed for video at {actual_path}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Video processing failed: {str(e)}"
        )

    # 4. Predict Impairment using ML
    prediction = predict_impairment(features, model_name=model_used)

    # 5. Compile Clinical scores and calculate average overall clinical percentage
    # Normalized score: FMA (max 226), BBS (max 56), FAC (max 5), TUG (lower is better, norm to 10s)
    # Convert each to a 0-100 scale
    fma_norm = (fma_score / 226.0) * 100
    bbs_norm = (bbs_score / 56.0) * 100
    fac_norm = (fac_score / 5.0) * 100
    tug_norm = max(0.0, min(100.0, (20.0 - tug_score) / 15.0 * 100)) if tug_score > 0 else 0
    
    active_norms = [fma_norm, bbs_norm, fac_norm]
    if tug_score > 0:
        active_norms.append(tug_norm)
    overall_clinical = round(sum(active_norms) / len(active_norms), 1) if active_norms else 0.0

    clinical_scores_data = {
        "fma_score": fma_score,
        "bbs_score": bbs_score,
        "fac_score": fac_score,
        "tug_score": tug_score,
        "overall_clinical_score": overall_clinical
    }

    # 6. Build Assessment Dict
    assessment_doc = {
        "patient_id": patient_id,
        "session_number": session_number,
        "assessment_date": datetime.now().isoformat(),
        "video_path": video_path,
        "clinical_scores": clinical_scores_data,
        "extracted_features": features,
        "predictions": prediction,
        "recommendations": generate_recommendations(features),
        "prescribed_exercises": generate_prescribed_exercises(features, patient.get("affected_side", "Right")),
        "therapist_notes": therapist_notes
    }

    # 7. Insert to database
    result = assessments_coll.insert_one(assessment_doc)
    
    # 8. Update patient status based on this latest assessment
    # Map impairment levels to status indicators
    patient_status = "Stable"
    if prediction["impairment_level"] in ["Normal", "Mild"]:
        patient_status = "Improving"
    elif prediction["impairment_level"] in ["Severe", "Very Severe"]:
        # If this is not first session, compare with previous to set status
        prev_sessions = assessments_coll.find({"patient_id": patient_id})
        if len(prev_sessions) > 1:
            # Sort sessions
            sorted_prev = sorted(prev_sessions, key=lambda x: x["session_number"])
            latest = sorted_prev[-1]
            penultimate = sorted_prev[-2]
            
            latest_speed = latest["extracted_features"]["gait"]["walking_speed_ms"]
            prev_speed = penultimate["extracted_features"]["gait"]["walking_speed_ms"]
            if latest_speed < prev_speed - 0.05:
                patient_status = "Deteriorating"
            elif latest_speed > prev_speed + 0.05:
                patient_status = "Improving"
                
    patients_coll.update_one(
        {"patient_id": patient_id},
        {"$set": {"current_status": patient_status}}
    )

    new_assessment = assessments_coll.find_one({"_id": result.inserted_id})
    return new_assessment

@router.get("", response_model=List[AssessmentResponse])
def list_assessments(patient_id: Optional[str] = None, current_user: dict = Depends(get_current_user)) -> Any:
    assessments_coll = get_collection("assessments")
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    
    results = assessments_coll.find(query)
    # Sort by session number
    return sorted(results, key=lambda x: x.get("session_number", 0))

@router.get("/{id}", response_model=AssessmentResponse)
def get_assessment(id: str, current_user: dict = Depends(get_current_user)) -> Any:
    assessments_coll = get_collection("assessments")
    assessment = assessments_coll.find_one({"_id": id})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment record not found")
    return assessment

@router.get("/compare/{patient_id}")
def compare_ai_vs_clinical(patient_id: str, current_user: dict = Depends(get_current_user)) -> Any:
    """Return data to build a visual comparison chart of AI Impairment Rating vs Clinical Assessment Scores."""
    assessments_coll = get_collection("assessments")
    sessions = assessments_coll.find({"patient_id": patient_id})
    
    comparison = []
    
    # Map AI impairment level to a numeric score from 0 to 100 for visual comparison
    level_weights = {
        "Very Severe": 15.0,
        "Severe": 35.0,
        "Moderate": 60.0,
        "Mild": 85.0,
        "Normal": 98.0
    }

    for s in sorted(sessions, key=lambda x: x.get("session_number", 0)):
        imp_level = s["predictions"]["impairment_level"]
        ai_score = level_weights.get(imp_level, 50.0)
        clinical = s["clinical_scores"].get("overall_clinical_score", 0.0)
        
        comparison.append({
            "session_number": s["session_number"],
            "assessment_date": s["assessment_date"][:10],
            "ai_predicted_score": ai_score,
            "clinical_assessment_score": clinical,
            "impairment_level": imp_level,
            "fma": s["clinical_scores"].get("fma_score"),
            "bbs": s["clinical_scores"].get("bbs_score")
        })
        
    return comparison

@router.post("/direct", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_direct_assessment(
    assessment_in: DirectAssessmentCreate,
    current_user: dict = Depends(require_therapist_or_doctor)
) -> Any:
    patients_coll = get_collection("patients")
    assessments_coll = get_collection("assessments")

    # 1. Verify patient exists
    patient = patients_coll.find_one({"patient_id": assessment_in.patient_id})
    if not patient:
        patient = patients_coll.find_one({"_id": assessment_in.patient_id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        p_id = patient["patient_id"]
    else:
        p_id = assessment_in.patient_id

    # 2. Extract features from JSON payload
    features = assessment_in.extracted_features.model_dump()
    
    # 3. Predict Impairment using ML
    prediction = predict_impairment(features, model_name=assessment_in.model_used)

    # 4. Compile Clinical scores and calculate average overall clinical percentage
    scores = assessment_in.clinical_scores
    fma_norm = (scores.fma_score / 226.0) * 100
    bbs_norm = (scores.bbs_score / 56.0) * 100
    fac_norm = (scores.fac_score / 5.0) * 100
    tug_norm = max(0.0, min(100.0, (20.0 - scores.tug_score) / 15.0 * 100)) if scores.tug_score > 0 else 0
    
    active_norms = [fma_norm, bbs_norm, fac_norm]
    if scores.tug_score > 0:
        active_norms.append(tug_norm)
    overall_clinical = round(sum(active_norms) / len(active_norms), 1) if active_norms else 0.0

    clinical_scores_data = {
        "fma_score": scores.fma_score,
        "bbs_score": scores.bbs_score,
        "fac_score": scores.fac_score,
        "tug_score": scores.tug_score,
        "overall_clinical_score": overall_clinical
    }

    # 5. Build Assessment Dict
    assessment_doc = {
        "patient_id": p_id,
        "session_number": assessment_in.session_number,
        "assessment_date": datetime.now().isoformat(),
        "video_path": None,
        "clinical_scores": clinical_scores_data,
        "extracted_features": features,
        "predictions": prediction,
        "recommendations": generate_recommendations(features),
        "prescribed_exercises": generate_prescribed_exercises(features, patient.get("affected_side", "Right")),
        "therapist_notes": assessment_in.therapist_notes
    }

    # 6. Insert to database
    result = assessments_coll.insert_one(assessment_doc)
    
    # 7. Update patient status
    patient_status = "Stable"
    if prediction["impairment_level"] in ["Normal", "Mild"]:
        patient_status = "Improving"
    elif prediction["impairment_level"] in ["Severe", "Very Severe"]:
        prev_sessions = list(assessments_coll.find({"patient_id": p_id}))
        if len(prev_sessions) > 1:
            sorted_prev = sorted(prev_sessions, key=lambda x: x["session_number"])
            latest = sorted_prev[-1]
            penultimate = sorted_prev[-2]
            latest_speed = latest["extracted_features"]["gait"]["walking_speed_ms"]
            prev_speed = penultimate["extracted_features"]["gait"]["walking_speed_ms"]
            if latest_speed < prev_speed - 0.05:
                patient_status = "Deteriorating"
            elif latest_speed > prev_speed + 0.05:
                patient_status = "Improving"
                
    patients_coll.update_one(
        {"patient_id": p_id},
        {"$set": {"current_status": patient_status}}
    )

    new_assessment = assessments_coll.find_one({"_id": result.inserted_id})
    return new_assessment
