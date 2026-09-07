from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any
from backend.db import get_collection
from backend.schemas import UserCreate, UserResponse, Token, UserLogin, ProfileUpdate, PasswordUpdate
from backend.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate) -> Any:
    users_coll = get_collection("users")
    
    # Check if username or email exists
    if users_coll.find_one({"username": user_in.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if users_coll.find_one({"email": user_in.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    user_dict = user_in.model_dump()
    hashed_password = get_password_hash(user_dict.pop("password"))
    user_dict["password_hash"] = hashed_password
    user_dict["created_at"] = None  # Will be set as string in db.py

    result = users_coll.insert_one(user_dict)
    
    # Retrieve inserted user
    new_user = users_coll.find_one({"_id": result.inserted_id})
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    users_coll = get_collection("users")
    user = users_coll.find_one({"username": form_data.username})
    
    if not user or not verify_password(form_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"],
        "full_name": user["full_name"]
    }

@router.post("/login-json", response_model=Token)
def login_json(credentials: UserLogin) -> Any:
    """Alternative login endpoint supporting raw JSON payload."""
    users_coll = get_collection("users")
    user = users_coll.find_one({"username": credentials.username})
    
    if not user or not verify_password(credentials.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"],
        "full_name": user["full_name"]
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: dict = Depends(get_current_user)) -> Any:
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(profile_in: ProfileUpdate, current_user: dict = Depends(get_current_user)) -> Any:
    users_coll = get_collection("users")
    update_data = {k: v for k, v in profile_in.model_dump().items() if v is not None}
    
    if "email" in update_data:
        existing_email = users_coll.find_one({"email": update_data["email"]})
        if existing_email and str(existing_email["_id"]) != str(current_user["_id"]):
            raise HTTPException(status_code=400, detail="Email already in use")
            
    if update_data:
        users_coll.update_one({"_id": current_user["_id"]}, {"$set": update_data})
        
    return users_coll.find_one({"_id": current_user["_id"]})

@router.put("/me/password", status_code=status.HTTP_200_OK)
def update_password(pw_in: PasswordUpdate, current_user: dict = Depends(get_current_user)) -> Any:
    users_coll = get_collection("users")
    if not verify_password(pw_in.old_password, current_user.get("password_hash", "")):
        raise HTTPException(status_code=400, detail="Incorrect old password")
        
    hashed_pw = get_password_hash(pw_in.new_password)
    users_coll.update_one({"_id": current_user["_id"]}, {"$set": {"password_hash": hashed_pw}})
    return {"message": "Password updated successfully"}
