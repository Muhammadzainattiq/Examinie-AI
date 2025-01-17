# app/routes/student_progress.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import date
from app.handlers.student_progress import handle_get_latest_progress, handle_get_progress_history
from app.models.exam import Result
from app.models.user import StudentProfile, StudentProgress
from app.models.user import User
from app.schemas.student import StudentProgressResponse
from app.utils.auth import get_current_user
from app.utils.db import get_session
from app.utils.student_progress import calculate_grade
progress_router = APIRouter(prefix="/student_progress")

@progress_router.get("/get_progress_history", response_model=List[StudentProgress])
def get_progress_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_get_progress_history(session, current_user)
    return response

@progress_router.get("/get_latest_progress", response_model=StudentProgressResponse)
def get_latest_progress(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
   response = handle_get_latest_progress(session, current_user)
   return response
