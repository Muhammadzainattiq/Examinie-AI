from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.schemas.student import StudentProfileCreate, StudentProfileResponse
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.db import get_session
from app.handlers.student import (
    handle_create_student_profile,
    handle_delete_student_profile,
    handle_get_all_student_profiles,
    handle_get_student_profile,
    handle_update_student_profile,
)

student_router = APIRouter(prefix="/student")


@student_router.post("/create_profile/", response_model=StudentProfileResponse)
def create_student_profile(
    profile_data: StudentProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return handle_create_student_profile(profile_data, session, current_user)


@student_router.get("/get_student_profile", response_model=StudentProfileResponse)
def get_student_profile(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return handle_get_student_profile(session, current_user)


@student_router.put("/update_profile", response_model=StudentProfileResponse)
def update_student_profile(
    profile_data: StudentProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return handle_update_student_profile(profile_data, session, current_user)


@student_router.delete("/delete_profile", response_model=dict)
def delete_student_profile(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return handle_delete_student_profile(session, current_user)


@student_router.get("/get_all_profiles", response_model=List[StudentProfileResponse])
def get_all_student_profiles(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return handle_get_all_student_profiles(session, current_user)
