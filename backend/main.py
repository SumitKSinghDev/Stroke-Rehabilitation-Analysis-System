import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import UPLOAD_DIR, REPORT_DIR
from backend.db import get_collection
from backend.auth import get_password_hash
from backend.routes import auth, patients, assessments, progress, admin, reports

app = FastAPI(
    title="Stroke Rehab AI-Assisted Decision Support System",
    description="ML-Based Gait & Upper Limb Motor Impairment Analysis for Stroke Rehabilitation",
    version="1.0.0"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow development clients
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve upload videos and reports statically
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/reports", StaticFiles(directory=str(REPORT_DIR)), name="reports")

# Register routes
app.include_router(auth.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(assessments.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "title": "Stroke Rehabilitation Decision Support System API",
        "status": "Online",
        "documentation": "/docs"
    }


# ---------------- DATABASE SEEDER ----------------

@app.on_event("startup")
def seed_database():
    """Seed default clinical user accounts, patients, and multi-session assessments."""
    users_coll = get_collection("users")
    patients_coll = get_collection("patients")
    assessments_coll = get_collection("assessments")

    # 1. Seed Users if empty
    if users_coll.count_documents() == 0:
        print("Database is empty. Seeding default clinical user accounts...")
        default_users = [
            {
                "username": "admin",
                "email": "admin@rehabshield.org",
                "full_name": "System Administrator",
                "role": "Admin",
                "password_hash": get_password_hash("admin123")
            },
            {
                "username": "therapist",
                "email": "therapist@rehabshield.org",
                "full_name": "Dr. Ramesh Kumar (PT)",
                "role": "Physiotherapist",
                "password_hash": get_password_hash("therapist123")
            },
            {
                "username": "doctor",
                "email": "doctor@rehabshield.org",
                "full_name": "Dr. Ananya Iyer (MD, Neurologist)",
                "role": "Doctor",
                "password_hash": get_password_hash("doctor123")
            }
        ]
        for u in default_users:
            users_coll.insert_one(u)
        print("User accounts seeded successfully: admin, therapist, doctor (all passwords end in 123).")

    # 2. Seed Patients if empty
    if patients_coll.count_documents() == 0:
        print("Seeding initial patient cases...")
        
        # We will create a default therapist id reference
        therapist_user = users_coll.find_one({"username": "therapist"})
        therapist_id = str(therapist_user["_id"]) if therapist_user else "system"

        default_patients = [
            {
                "patient_id": "PT-2026-0001",
                "name": "Aarav Mehta",
                "age": 58,
                "gender": "Male",
                "stroke_type": "Ischemic",
                "affected_side": "Right",
                "stroke_date": "2026-02-15",
                "current_status": "Improving",
                "medical_notes": "Right hemiparetic stroke with gait drop foot. Shows strong compliance in exercise regimens.",
                "therapist_id": therapist_id,
                "created_at": "2026-03-01T10:00:00"
            },
            {
                "patient_id": "PT-2026-0002",
                "name": "Priya Sharma",
                "age": 62,
                "gender": "Female",
                "stroke_type": "Hemorrhagic",
                "affected_side": "Left",
                "stroke_date": "2026-01-10",
                "current_status": "Stable",
                "medical_notes": "Left-sided weakness affecting shoulder range of motion and overall walking balance. Uses walking frame.",
                "therapist_id": therapist_id,
                "created_at": "2026-03-05T11:30:00"
            }
        ]
        
        for p in default_patients:
            patients_coll.insert_one(p)
        print("Patients seeded successfully.")

        # 3. Seed Assessments (Sessions 1, 2, 3, 4) showing progress for Aarav Mehta
        # Session 1: Severe impairment, slow walking speed, low balance
        # Session 2: Moderate impairment, slight improvements
        # Session 3: Moderate impairment, speed improved
        # Session 4: Mild impairment, high balance and speed
        
        print("Seeding multi-session patient progress logs...")
        
        aarav_sessions = [
            # Session 1 - Baseline
            {
                "patient_id": "PT-2026-0001",
                "session_number": 1,
                "assessment_date": "2026-03-05T10:30:00",
                "video_path": None,
                "clinical_scores": {
                    "fma_score": 85,
                    "bbs_score": 24,
                    "fac_score": 1,
                    "tug_score": 28.5,
                    "overall_clinical_score": 38.6
                },
                "extracted_features": {
                    "angles": {
                        "hip_angle_deg": 22.4,
                        "knee_angle_deg": 28.1,
                        "shoulder_angle_deg": 18.5,
                        "elbow_angle_deg": 105.4
                    },
                    "gait": {
                        "stride_length_m": 0.32,
                        "cadence_steps_min": 52.0,
                        "walking_speed_ms": 0.28,
                        "step_width_m": 0.30,
                        "step_symmetry_ratio": 0.54
                    },
                    "arm_swing_deg": 8.5,
                    "rom_score": 43.6,
                    "balance_stability_score": 32.0,
                    "landmarks": []
                },
                "predictions": {
                    "impairment_level": "Severe",
                    "model_used": "Random Forest",
                    "confidence": 0.86,
                    "feature_importances": {
                        "walking_speed": 0.23, "step_symmetry": 0.19, "balance_stability": 0.16, "knee_angle": 0.12
                    }
                },
                "recommendations": [
                    "Reduced Knee Flexion: Consider knee mobility exercises (heel slides) to improve swing clearance.",
                    "Low Walking Speed: Recommend body-weight supported walk pacing.",
                    "Reduced Balance Stability: Prescribe standing balance trials with rails.",
                    "Final treatment decisions should be made by qualified healthcare professionals."
                ],
                "therapist_notes": "Baseline session. Patient requires significant support. Severe foot drop and elbow contracture pattern."
            },
            # Session 2
            {
                "patient_id": "PT-2026-0001",
                "session_number": 2,
                "assessment_date": "2026-04-05T10:15:00",
                "video_path": None,
                "clinical_scores": {
                    "fma_score": 115,
                    "bbs_score": 32,
                    "fac_score": 2,
                    "tug_score": 22.0,
                    "overall_clinical_score": 50.1
                },
                "extracted_features": {
                    "angles": {
                        "hip_angle_deg": 26.8,
                        "knee_angle_deg": 34.5,
                        "shoulder_angle_deg": 22.0,
                        "elbow_angle_deg": 112.5
                    },
                    "gait": {
                        "stride_length_m": 0.42,
                        "cadence_steps_min": 65.0,
                        "walking_speed_ms": 0.46,
                        "step_width_m": 0.27,
                        "step_symmetry_ratio": 0.65
                    },
                    "arm_swing_deg": 12.0,
                    "rom_score": 48.9,
                    "balance_stability_score": 48.0,
                    "landmarks": []
                },
                "predictions": {
                    "impairment_level": "Moderate",
                    "model_used": "Random Forest",
                    "confidence": 0.72,
                    "feature_importances": {
                        "walking_speed": 0.23, "step_symmetry": 0.19, "balance_stability": 0.16, "knee_angle": 0.12
                    }
                },
                "recommendations": [
                    "Reduced Knee Flexion: Consider knee mobility exercises.",
                    "Low Walking Speed: Recommend paced corridor walks.",
                    "Reduced Balance Stability: Prescribe standing balance trials with rails.",
                    "Final treatment decisions should be made by qualified healthcare professionals."
                ],
                "therapist_notes": "Session 2. Shows improvements in knee flexion and gait speed. Balance remains moderately impaired."
            },
            # Session 3
            {
                "patient_id": "PT-2026-0001",
                "session_number": 3,
                "assessment_date": "2026-05-05T11:00:00",
                "video_path": None,
                "clinical_scores": {
                    "fma_score": 145,
                    "bbs_score": 40,
                    "fac_score": 3,
                    "tug_score": 16.5,
                    "overall_clinical_score": 64.9
                },
                "extracted_features": {
                    "angles": {
                        "hip_angle_deg": 32.1,
                        "knee_angle_deg": 41.2,
                        "shoulder_angle_deg": 28.6,
                        "elbow_angle_deg": 125.0
                    },
                    "gait": {
                        "stride_length_m": 0.52,
                        "cadence_steps_min": 78.0,
                        "walking_speed_ms": 0.68,
                        "step_width_m": 0.23,
                        "step_symmetry_ratio": 0.78
                    },
                    "arm_swing_deg": 16.5,
                    "rom_score": 56.7,
                    "balance_stability_score": 65.0,
                    "landmarks": []
                },
                "predictions": {
                    "impairment_level": "Moderate",
                    "model_used": "Random Forest",
                    "confidence": 0.81,
                    "feature_importances": {
                        "walking_speed": 0.23, "step_symmetry": 0.19, "balance_stability": 0.16, "knee_angle": 0.12
                    }
                },
                "recommendations": [
                    "Reduced Knee Flexion: Keep up knee extensions.",
                    "Gait Asymmetry: Utilize metronome-guided step timing.",
                    "Final treatment decisions should be made by qualified healthcare professionals."
                ],
                "therapist_notes": "Session 3. Walks with minimal supervision. Step symmetry has improved from 0.54 to 0.78."
            },
            # Session 4
            {
                "patient_id": "PT-2026-0001",
                "session_number": 4,
                "assessment_date": "2026-06-05T09:45:00",
                "video_path": None,
                "clinical_scores": {
                    "fma_score": 182,
                    "bbs_score": 48,
                    "fac_score": 4,
                    "tug_score": 11.2,
                    "overall_clinical_score": 81.3
                },
                "extracted_features": {
                    "angles": {
                        "hip_angle_deg": 41.5,
                        "knee_angle_deg": 52.3,
                        "shoulder_angle_deg": 38.0,
                        "elbow_angle_deg": 142.1
                    },
                    "gait": {
                        "stride_length_m": 0.65,
                        "cadence_steps_min": 92.0,
                        "walking_speed_ms": 0.88,
                        "step_width_m": 0.18,
                        "step_symmetry_ratio": 0.88
                    },
                    "arm_swing_deg": 22.0,
                    "rom_score": 68.4,
                    "balance_stability_score": 82.0,
                    "landmarks": []
                },
                "predictions": {
                    "impairment_level": "Mild",
                    "model_used": "Random Forest",
                    "confidence": 0.89,
                    "feature_importances": {
                        "walking_speed": 0.23, "step_symmetry": 0.19, "balance_stability": 0.16, "knee_angle": 0.12
                    }
                },
                "recommendations": [
                    "Gait Asymmetry: Maintain symmetric cadence exercises.",
                    "Final treatment decisions should be made by qualified healthcare professionals."
                ],
                "therapist_notes": "Session 4. Excellent progress. Independent ambulation achieved. Slight asymmetry remains, but range of motion is near normal."
            }
        ]

        for s in aarav_sessions:
            assessments_coll.insert_one(s)
            
        # Seed session 1 baseline for Priya Sharma
        priya_sessions = [
            {
                "patient_id": "PT-2026-0002",
                "session_number": 1,
                "assessment_date": "2026-03-10T11:45:00",
                "video_path": None,
                "clinical_scores": {
                    "fma_score": 98,
                    "bbs_score": 18,
                    "fac_score": 1,
                    "tug_score": 32.0,
                    "overall_clinical_score": 34.8
                },
                "extracted_features": {
                    "angles": {
                        "hip_angle_deg": 18.2,
                        "knee_angle_deg": 24.1,
                        "shoulder_angle_deg": 12.5,
                        "elbow_angle_deg": 92.4
                    },
                    "gait": {
                        "stride_length_m": 0.25,
                        "cadence_steps_min": 42.0,
                        "walking_speed_ms": 0.18,
                        "step_width_m": 0.35,
                        "step_symmetry_ratio": 0.48
                    },
                    "arm_swing_deg": 4.5,
                    "rom_score": 32.6,
                    "balance_stability_score": 28.0,
                    "landmarks": []
                },
                "predictions": {
                    "impairment_level": "Very Severe",
                    "model_used": "Random Forest",
                    "confidence": 0.92,
                    "feature_importances": {
                        "walking_speed": 0.23, "step_symmetry": 0.19, "balance_stability": 0.16, "knee_angle": 0.12
                    }
                },
                "recommendations": [
                    "Reduced Knee Flexion: Consider knee mobility exercises.",
                    "Low Walking Speed: Speed-oriented frame pacing.",
                    "Reduced Balance Stability: Safe seated balance movements.",
                    "Final treatment decisions should be made by qualified healthcare professionals."
                ],
                "therapist_notes": "Baseline session. Patient requires physical assistance from therapist + frame. Severe hemiplegia on the left."
            }
        ]
        for s in priya_sessions:
            assessments_coll.insert_one(s)
            
        print("Completed database seeding of patients and sessions.")
