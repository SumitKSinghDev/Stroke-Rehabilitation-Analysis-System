from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from backend.db import get_collection
from backend.schemas import AdminStats, UserResponse, SystemLog
from backend.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Administrative Portal"])

# Simulated System Log Entries for presentation audit trail
SYSTEM_LOGS = [
    {"timestamp": "2026-07-31T09:12:00", "level": "INFO", "user": "admin", "action": "User Seeding", "details": "Default system admin, doctor, and therapist accounts initialized."},
    {"timestamp": "2026-07-31T10:15:30", "level": "INFO", "user": "therapist", "action": "Add Patient", "details": "Created patient record for PT-2026-0001 (Aarav Mehta)."},
    {"timestamp": "2026-07-31T10:30:12", "level": "INFO", "user": "therapist", "action": "Upload Video", "details": "Uploaded gait assessment video for patient PT-2026-0001."},
    {"timestamp": "2026-07-31T10:31:05", "level": "INFO", "user": "therapist", "action": "Run Pose Analysis", "details": "MediaPipe Pose processing finished successfully for session 1."},
    {"timestamp": "2026-07-31T10:31:07", "level": "INFO", "user": "system", "action": "ML Impairment Prediction", "details": "Random Forest classifier predicted level: Moderate (Confidence: 84%)."},
    {"timestamp": "2026-07-31T11:42:15", "level": "INFO", "user": "doctor", "action": "Review Assessment", "details": "Reviewed gait metrics and appended clinical notes for patient PT-2026-0001."},
    {"timestamp": "2026-07-31T12:01:40", "level": "WARNING", "user": "admin", "action": "Settings Update", "details": "Database fallback mode toggled due to connection alert."},
]

@router.get("/stats", response_model=AdminStats)
def get_system_stats(current_user: dict = Depends(require_admin)) -> Any:
    users_coll = get_collection("users")
    patients_coll = get_collection("patients")
    assessments_coll = get_collection("assessments")

    total_users = users_coll.count_documents()
    total_patients = patients_coll.count_documents()
    total_assessments = assessments_coll.count_documents()

    # Role breakdown counts
    roles = ["Admin", "Physiotherapist", "Doctor", "Patient"]
    role_counts = {}
    for r in roles:
        role_counts[r] = users_coll.count_documents({"role": r})

    return {
        "total_users": total_users,
        "total_patients": total_patients,
        "total_assessments": total_assessments,
        "role_counts": role_counts,
        "recent_logs": SYSTEM_LOGS[-10:] # Return last 10 entries
    }

@router.get("/users", response_model=List[UserResponse])
def list_system_users(current_user: dict = Depends(require_admin)) -> Any:
    users_coll = get_collection("users")
    return users_coll.find()

@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(user_id: str, new_role: str, current_user: dict = Depends(require_admin)) -> Any:
    users_coll = get_collection("users")
    user = users_coll.find_one({"_id": user_id})
    if not user:
        user = users_coll.find_one({"username": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User account not found")
            
    if new_role not in ["Admin", "Physiotherapist", "Doctor", "Patient"]:
        raise HTTPException(status_code=400, detail="Invalid system role specified")
        
    users_coll.update_one({"_id": user["_id"]}, {"$set": {"role": new_role}})
    
    # Append log entry
    SYSTEM_LOGS.append({
        "timestamp": datetime.now().isoformat(),
        "level": "WARNING",
        "user": current_user["username"],
        "action": "User Role Update",
        "details": f"Role for user {user['username']} updated to {new_role}."
    })
    
    return users_coll.find_one({"_id": user["_id"]})

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_account(user_id: str, current_user: dict = Depends(require_admin)) -> Any:
    users_coll = get_collection("users")
    user = users_coll.find_one({"_id": user_id})
    if not user:
        user = users_coll.find_one({"username": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User account not found")

    if user["username"] == current_user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own administrator account.")

    users_coll.delete_one({"_id": user["_id"]})
    
    # Append log entry
    SYSTEM_LOGS.append({
        "timestamp": datetime.now().isoformat(),
        "level": "WARNING",
        "user": current_user["username"],
        "action": "Delete User Account",
        "details": f"Deleted user account for username: {user['username']}."
    })

    return {"message": f"User account '{user['username']}' has been deleted."}
