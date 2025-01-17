# app/routes/student_progress.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import date
from app.models.exam import Result
from app.models.user import StudentProfile, StudentProgress
from app.models.user import User
from app.schemas.student import StudentProgressResponse
from app.utils.auth import get_current_user
from app.utils.db import get_session
from app.utils.student_progress import calculate_grade
progress_router = APIRouter(prefix="/student_progress")


def handle_get_progress_history(
    session: Session,
    current_user: User
):
    # Fetch all progress records for the user
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    progress_records = session.exec(select(StudentProgress).where(StudentProgress.profile_id == profile.id)).all()
    
    if not progress_records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No progress records found.")

    return progress_records

def handle_get_latest_progress(
    session: Session,
    current_user: User
):
    # Fetch the student's profile
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    # Fetch the latest progress record
    latest_progress = session.exec(
        select(StudentProgress)
        .where(StudentProgress.profile_id == profile.id)
        .order_by(StudentProgress.created_at.desc())
    ).first()

    if not latest_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress record found for the student."
        )

    return latest_progress