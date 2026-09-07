from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

# ----------------- AUTH & USER SCHEMAS -----------------

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str
    role: str = Field("Physiotherapist", description="Admin, Physiotherapist, Doctor, Patient")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: str = Field(..., alias="_id")
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    full_name: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

# ----------------- PATIENT SCHEMAS -----------------

class PatientBase(BaseModel):
    patient_id: str = Field(..., description="Unique ID like PT-2026-0001")
    name: str
    age: int
    gender: str
    stroke_type: str = Field(..., description="Ischemic, Hemorrhagic, TIA")
    affected_side: str = Field(..., description="Left, Right, Bilateral")
    stroke_date: str = Field(..., description="YYYY-MM-DD")
    current_status: str = Field("Stable", description="Improving, Stable, Deteriorating")
    medical_notes: Optional[str] = ""
    photo_url: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    stroke_type: Optional[str] = None
    affected_side: Optional[str] = None
    stroke_date: Optional[str] = None
    current_status: Optional[str] = None
    medical_notes: Optional[str] = None
    photo_url: Optional[str] = None

class PatientResponse(PatientBase):
    id: str = Field(..., alias="_id")
    created_at: Optional[str] = None
    therapist_id: Optional[str] = None
    session_count: int = 0

    class Config:
        populate_by_name = True

# ----------------- ASSESSMENT SCHEMAS -----------------

class ClinicalScores(BaseModel):
    fma_score: int = Field(0, ge=0, le=226, description="Fugl-Meyer Assessment (0-226)")
    bbs_score: int = Field(0, ge=0, le=56, description="Berg Balance Scale (0-56)")
    fac_score: int = Field(0, ge=0, le=5, description="Functional Ambulation Categories (0-5)")
    tug_score: float = Field(0.0, ge=0.0, description="Timed Up and Go (seconds)")
    overall_clinical_score: Optional[float] = 0.0

class JointAngles(BaseModel):
    hip_angle_deg: float
    knee_angle_deg: float
    shoulder_angle_deg: float
    elbow_angle_deg: float

class GaitParameters(BaseModel):
    stride_length_m: float
    cadence_steps_min: float
    walking_speed_ms: float
    step_width_m: float
    step_symmetry_ratio: float

class Landmark(BaseModel):
    id: int
    x: float
    y: float
    z: float
    visibility: float

class MovementFeatures(BaseModel):
    angles: JointAngles
    gait: GaitParameters
    arm_swing_deg: float
    rom_score: float
    balance_stability_score: float
    landmarks: Optional[List[Landmark]] = []

class MLPrediction(BaseModel):
    impairment_level: str = Field(..., description="Normal, Mild, Moderate, Severe, Very Severe")
    model_used: str = Field("Random Forest", description="Random Forest, SVM, XGBoost")
    confidence: float = Field(..., ge=0.0, le=1.0)
    feature_importances: Dict[str, float]

class AssessmentCreate(BaseModel):
    patient_id: str
    session_number: int
    clinical_scores: ClinicalScores
    video_filename: Optional[str] = None
    therapist_notes: Optional[str] = ""

class DirectAssessmentCreate(BaseModel):
    patient_id: str
    session_number: int
    clinical_scores: ClinicalScores
    extracted_features: MovementFeatures
    model_used: str = "Random Forest"
    therapist_notes: Optional[str] = ""

class PrescribedExercise(BaseModel):
    title: str
    category: str
    target_deficit: str
    dosage: str
    intensity: str
    instructions: str
    clinical_rationale: str

class AssessmentResponse(BaseModel):
    id: str = Field(..., alias="_id")
    patient_id: str
    session_number: int
    assessment_date: str
    video_path: Optional[str] = None
    clinical_scores: ClinicalScores
    extracted_features: Optional[MovementFeatures] = None
    predictions: Optional[MLPrediction] = None
    recommendations: List[str] = []
    prescribed_exercises: Optional[List[PrescribedExercise]] = []
    therapist_notes: Optional[str] = ""

    class Config:
        populate_by_name = True

# ----------------- PROGRESS & ANALYTICS SCHEMAS -----------------

class ProgressTrendPoint(BaseModel):
    session_number: int
    assessment_date: str
    walking_speed: float
    balance_score: float
    rom_score: float
    overall_score: float
    impairment_level: str

class ProgressSummary(BaseModel):
    improvement_pct: float
    recovery_status: str
    trends: List[ProgressTrendPoint]

# ----------------- ADMIN & LOGS SCHEMAS -----------------

class SystemLog(BaseModel):
    timestamp: str
    level: str
    user: str
    action: str
    details: str

class AdminStats(BaseModel):
    total_users: int
    total_patients: int
    total_assessments: int
    role_counts: Dict[str, int]
    recent_logs: List[SystemLog]
