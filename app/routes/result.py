from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.exam import Exam, ExamAttempt, Result
from app.schemas.result import ResultCreate, ResultResponse
from app.utils.db import get_session
from app.utils.auth import get_current_user
from app.models.user import StudentProfile, StudentProgress, User
from app.models.enum import LatestGrade
from app.utils.student_progress import calculate_grade

result_router = APIRouter(prefix="/results")

@result_router.post("/create_result/{exam_attempt_id}", response_model=ResultResponse)
async def create_result(
    exam_attempt_id: UUID,
    result_data: ResultCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    # Retrieve the student's profile
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    # Retrieve the exam attempt based on the exam attempt ID
    exam_attempt = session.get(ExamAttempt, exam_attempt_id)
    if not exam_attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam attempt not found.")

    exam = session.get(Exam, exam_attempt.exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

    # Retrieve the latest StudentProgress record for the student
    latest_progress = session.exec(
        select(StudentProgress)
        .where(StudentProgress.profile_id == profile.id)
        .order_by(StudentProgress.date_recorded.desc())
    ).first()

    # Initialize fields for the new StudentProgress record based on the latest progress
    total_exams_taken = (latest_progress.total_exams_taken if latest_progress else 0) + 1

    # Calculate the grade and percentage
    if result_data.total_marks:
        percentage = (result_data.obtained_marks / result_data.total_marks) * 100
    else:
        percentage = 0.0  # Handle case where total_marks is None

    grade = calculate_grade(percentage)

    # Calculate exams passed/failed based on grade
    exams_passed = (latest_progress.exams_passed if latest_progress else 0) + (1 if grade not in [LatestGrade.F, LatestGrade.INCOMPLETE, LatestGrade.FAIL] else 0)
    exams_failed = (latest_progress.exams_failed if latest_progress else 0) + (1 if grade in [LatestGrade.F, LatestGrade.INCOMPLETE, LatestGrade.FAIL] else 0)

    # Calculate total points and time spent
    total_points = (latest_progress.total_points if latest_progress else 0) + (result_data.obtained_marks or 0)

    # Create a new StudentProgress record
    progress_record = StudentProgress(
        profile_id=profile.id,
        date_recorded=datetime.utcnow(),
        last_exam_score=result_data.obtained_marks or 0,
        total_exams_taken=total_exams_taken,
        exams_passed=exams_passed,
        exams_failed=exams_failed,
        total_points=total_points,
        overall_grade=None,  # Placeholder for calculation below
        overall_percentage=0.0,  # Placeholder for calculation below
    )

    # Add the new progress record to the session
    session.add(progress_record)
    session.commit()
    session.refresh(progress_record)

    # Create the result entry and link it to the new progress record
    new_result = Result(
        exam_attempt_id=exam_attempt.id,
        student_progress_id=progress_record.id,
        exam_title=exam.title,
        total_marks=result_data.total_marks,
        obtained_marks=result_data.obtained_marks,
        grade=str(grade),
        percentage=percentage,
        feedback=result_data.feedback
    )
    session.add(new_result)
    session.commit()
    session.refresh(new_result)

    # Calculate overall grade and percentage based on all results for the student
    all_results = session.exec(select(Result).where(Result.student_progress_id == progress_record.id)).all()
    if all_results:
        total_obtained = sum(result.obtained_marks for result in all_results)
        total_max = sum(result.total_marks for result in all_results if result.total_marks)

        if total_max > 0:
            overall_percentage = (total_obtained / total_max) * 100
            progress_record.overall_percentage = overall_percentage
            progress_record.overall_grade = calculate_grade(overall_percentage)

    # Update and save the new progress record with the calculated grade and percentage
    session.add(progress_record)
    session.commit()
    session.refresh(progress_record)

    return new_result


@result_router.get("/get_result/{result_id}/", response_model=ResultResponse)
async def get_result(
    result_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve result details by result_id
    result = session.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    return result


@result_router.get("/get_all_student_results/", response_model=List[ResultResponse])
async def get_student_results(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Get the student's profile
    student_profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    # Get all results associated with the student's profile through StudentProgress
    results = session.exec(
        select(Result)
        .join(StudentProgress, StudentProgress.id == Result.student_progress_id)
        .where(StudentProgress.profile_id == student_profile.id)
    ).all()

    return results

