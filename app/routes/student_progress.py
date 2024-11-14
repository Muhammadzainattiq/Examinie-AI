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


@progress_router.post("/create_progress_record", response_model=StudentProgress)
def create_progress_record(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if the student profile exists
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    # Create an initial progress record
    new_progress = StudentProgress(
        profile_id=profile.id,
        date_recorded=date.today(),
        last_exam_score=0.0,
        total_exams_taken=0,
        exams_passed=0,
        exams_failed=0,
        total_points=0,
        overall_grade=None,
        overall_percentage=0.0,
        time_spent=0
    )

    session.add(new_progress)
    session.commit()
    session.refresh(new_progress)

    return new_progress


# routes/student.py

@progress_router.put("/update_progress", response_model=StudentProgressResponse)
def update_progress(
    last_exam_score: float,
    passed: bool,
<<<<<<< HEAD
=======
    time_spent: int,
>>>>>>> b630a287bf5ddd336d87b341e0671ec1b0b45e5c
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    # Retrieve the student's profile
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    # Retrieve the latest progress record
    last_progress_record = session.exec(
<<<<<<< HEAD
        select(StudentProgress).where(StudentProgress.profile_id == profile.id).order_by(StudentProgress.created_at.desc())
=======
        select(StudentProgress).where(StudentProgress.profile_id == profile.id).order_by(StudentProgress.date_recorded.desc())
>>>>>>> b630a287bf5ddd336d87b341e0671ec1b0b45e5c
    ).first()
    if not last_progress_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress record not found.")

    # Create a new progress record, initializing it with values from the latest record
    new_progress_record = StudentProgress(
        profile_id=profile.id,
        date_recorded=date.today(),
        last_exam_score=last_exam_score,
        total_exams_taken=last_progress_record.total_exams_taken + 1,
        exams_passed=last_progress_record.exams_passed + (1 if passed else 0),
        exams_failed=last_progress_record.exams_failed + (0 if passed else 1),
        total_points=last_progress_record.total_points + int(last_exam_score),
        overall_grade=last_progress_record.overall_grade,  # Initial value, will update below
        overall_percentage=last_progress_record.overall_percentage,  # Initial value, will update below
<<<<<<< HEAD
=======
        time_spent=last_progress_record.time_spent + time_spent
>>>>>>> b630a287bf5ddd336d87b341e0671ec1b0b45e5c
    )

    # Calculate the overall grade and percentage based on all results linked to this progress record
    results = session.exec(select(Result).where(Result.student_progress_id == last_progress_record.id)).all()

    if results:
        total_obtained = sum(result.obtained_marks for result in results)
        total_max = sum(result.total_marks for result in results if result.total_marks)
        
        if total_max > 0:
            overall_percentage = (total_obtained / total_max) * 100
            new_progress_record.overall_percentage = overall_percentage
            new_progress_record.overall_grade = calculate_grade(overall_percentage)  # Use the LatestGrade enum

    # Add the new record to the session and commit
    session.add(new_progress_record)
    session.commit()
    session.refresh(new_progress_record)

    return new_progress_record



@progress_router.get("/progress_history", response_model=List[StudentProgress])
def get_progress_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Fetch all progress records for the user
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    progress_records = session.exec(select(StudentProgress).where(StudentProgress.profile_id == profile.id)).all()
    
    if not progress_records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No progress records found.")

    return progress_records




