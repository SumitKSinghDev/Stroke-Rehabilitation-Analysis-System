from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from datetime import datetime
from backend.db import get_collection
from backend.schemas import PatientCreate, PatientResponse, PatientUpdate
from backend.auth import get_current_user, require_therapist_or_doctor

router = APIRouter(prefix="/patients", tags=["Patient Management"])

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient_in: PatientCreate, current_user: dict = Depends(require_therapist_or_doctor)) -> Any:
    patients_coll = get_collection("patients")
    
    # Check duplicate patient_id
    if patients_coll.find_one({"patient_id": patient_in.patient_id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patient ID {patient_in.patient_id} already exists."
        )
        
    patient_dict = patient_in.model_dump()
    patient_dict["therapist_id"] = str(current_user["_id"])
    patient_dict["created_at"] = datetime.now().isoformat()
    
    result = patients_coll.insert_one(patient_dict)
    new_patient = patients_coll.find_one({"_id": result.inserted_id})
    return new_patient

@router.get("", response_model=List[PatientResponse])
def list_patients(current_user: dict = Depends(get_current_user)) -> Any:
    patients_coll = get_collection("patients")
    assessments_coll = get_collection("assessments")
    
    patients = patients_coll.find()
    
    # Enrich patients with session count
    enriched_patients = []
    for p in patients:
        p_id = p["patient_id"]
        session_count = assessments_coll.count_documents({"patient_id": p_id})
        p["session_count"] = session_count
        enriched_patients.append(p)
        
    return enriched_patients

@router.get("/{id}", response_model=PatientResponse)
def get_patient(id: str, current_user: dict = Depends(get_current_user)) -> Any:
    patients_coll = get_collection("patients")
    assessments_coll = get_collection("assessments")
    
    patient = patients_coll.find_one({"_id": id})
    if not patient:
        # Check by patient_id string as well
        patient = patients_coll.find_one({"patient_id": id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
    p_id = patient["patient_id"]
    patient["session_count"] = assessments_coll.count_documents({"patient_id": p_id})
    return patient

@router.put("/{id}", response_model=PatientResponse)
def update_patient(
    id: str, 
    patient_in: PatientUpdate, 
    current_user: dict = Depends(require_therapist_or_doctor)
) -> Any:
    patients_coll = get_collection("patients")
    patient = patients_coll.find_one({"_id": id})
    if not patient:
        patient = patients_coll.find_one({"patient_id": id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
    update_data = {k: v for k, v in patient_in.model_dump().items() if v is not None}
    if update_data:
        patients_coll.update_one({"_id": patient["_id"]}, {"$set": update_data})
        
    updated_patient = patients_coll.find_one({"_id": patient["_id"]})
    
    assessments_coll = get_collection("assessments")
    updated_patient["session_count"] = assessments_coll.count_documents({"patient_id": updated_patient["patient_id"]})
    return updated_patient

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_patient(id: str, current_user: dict = Depends(require_therapist_or_doctor)) -> Any:
    patients_coll = get_collection("patients")
    assessments_coll = get_collection("assessments")
    
    patient = patients_coll.find_one({"_id": id})
    if not patient:
        patient = patients_coll.find_one({"patient_id": id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
    # Delete patient and their assessments
    patients_coll.delete_one({"_id": patient["_id"]})
    
    # Optional: Delete associated assessments
    assessments = assessments_coll.find({"patient_id": patient["patient_id"]})
    for a in assessments:
        assessments_coll.delete_one({"_id": a["_id"]})
        
    return {"message": f"Patient {patient['name']} and all associated session assessments deleted successfully."}
