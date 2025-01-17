from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.exam import Answer, Exam, ExamAttempt, Question, Result
from app.schemas.result import ResultCreate, ResultResponse
from app.utils.db import get_session
from app.utils.auth import get_current_user
from app.models.user import StudentProfile, StudentProgress, User
from app.models.enum import LatestGrade
from app.utils.exam_grading import grade_questions
from app.utils.student_progress import calculate_grade
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from uuid import UUID

result_router = APIRouter(prefix="/results")

def handle_get_result(
    result_id: UUID,
    session: Session,
    current_user: User
):
    # Retrieve result details by result_id
    result = session.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    return result


def handle_get_student_results(
    session: Session,
    current_user: User
):
    # Get all results associated with the student's profile through StudentProgress
    results = session.exec(
        select(Result)
        .where(Result.student_id == current_user.id)
    ).all()

    return results

def handle_get_last_exam_result(
    session: Session,
    current_user: User):
    # Fetch the most recent result for the current user
    last_result = session.exec(
        select(Result)
        .where(Result.student_id == current_user.id)
        .order_by(Result.created_at.desc())
    ).first()

    if not last_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No exam results found for the student."
        )

    return last_result


def handle_generate_and_update_result(
    exam_attempt_id: UUID,
    session: Session,
    current_user: User
):
    # Fetch exam attempt
    attempt = session.get(ExamAttempt, exam_attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    
    # Check if the exam attempt is completed
    if not attempt.completed:
        raise HTTPException(
            status_code=400,  # Bad Request
            detail="Result cannot be generated because the exam attempt is not completed."
        )

    # Fetch related exam and questions
    exam = session.get(Exam, attempt.exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for the attempt")

    # Get all questions associated with the exam
    questions = session.exec(
        select(Question).where(Question.exam_id == exam.id)
    ).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for the exam")

    # Fetch answers based on the exam attempt
    answers = session.exec(
        select(Answer).where(Answer.attempt_id == attempt.id)
    ).all()
    student_answers = {answer.question_id: answer.response for answer in answers}

    # Call grade_questions to grade the exam and return feedback
    graded_results = grade_questions(questions, student_answers, session)

    # Construct graded questions with additional details
    graded_questions = []
    for graded_result in graded_results:
        question = session.get(Question, graded_result["question_id"])
        student_response = student_answers.get(graded_result["question_id"], "Unattempted")
        graded_questions.append({
            "question_id": graded_result["question_id"],  # Include question ID
            "statement": question.statement,  # Include the question statement
            "response": student_response,  # Include the student's response
            "question_type": graded_result["question_type"],
            "total_marks": graded_result["total_marks"],
            "obtained_marks": graded_result["obtained_marks"],
            "feedback": graded_result["feedback"]
        })

    # Summarize the overall result
    total_marks = sum(q["total_marks"] for q in graded_results)
    obtained_marks = sum(q["obtained_marks"] for q in graded_results)
    summarized_feedback = " | ".join(q["feedback"] for q in graded_results if q["feedback"])

    # Calculate grade and percentage
    percentage = (obtained_marks / total_marks) * 100 if total_marks > 0 else 0
    grade = calculate_grade(percentage)

    # Save overall result in the database
    result = Result(
        exam_attempt_id=attempt.id,
        student_id=attempt.student_id,
        exam_title=exam.title,
        total_marks=total_marks,
        obtained_marks=obtained_marks,
        grade=grade,
        percentage=percentage
    )
    session.add(result)
    session.commit()
    session.refresh(result)

    # Retrieve student's profile and progress
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    latest_progress = session.exec(
        select(StudentProgress)
        .where(StudentProgress.profile_id == profile.id)
        .order_by(StudentProgress.created_at.desc())
    ).first()

    total_exams_taken = (latest_progress.total_exams_taken if latest_progress else 0) + 1
    exams_passed = (latest_progress.exams_passed if latest_progress else 0) + (1 if grade not in [LatestGrade.F, LatestGrade.INCOMPLETE, LatestGrade.FAIL] else 0)
    exams_failed = (latest_progress.exams_failed if latest_progress else 0) + (1 if grade in [LatestGrade.F, LatestGrade.INCOMPLETE, LatestGrade.FAIL] else 0)
    total_points = (latest_progress.total_points if latest_progress else 0) + obtained_marks

    progress_record = StudentProgress(
        profile_id=profile.id,
        date_recorded=datetime.utcnow(),
        last_exam_score=obtained_marks,
        total_exams_taken=total_exams_taken,
        exams_passed=exams_passed,
        exams_failed=exams_failed,
        total_points=total_points,
        overall_grade=None,
        overall_percentage=0.0
    )
    session.add(progress_record)
    session.commit()
    session.refresh(progress_record)

    # Recalculate overall grade and percentage
    all_results = session.exec(select(Result).where(Result.student_id == current_user.id)).all()
    if all_results:
        total_obtained = sum(r.obtained_marks for r in all_results)
        total_max = sum(r.total_marks for r in all_results if r.total_marks > 0)

        if total_max > 0:
            overall_percentage = (total_obtained / total_max) * 100
            progress_record.overall_percentage = overall_percentage
            progress_record.overall_grade = calculate_grade(overall_percentage)

    session.add(progress_record)
    session.commit()
    session.refresh(progress_record)

    response_payload = {
        "overall_result": {
            "result_id": result.id,
            "exam_title": result.exam_title,
            "total_marks": result.total_marks,
            "obtained_marks": result.obtained_marks,
            "grade": result.grade,
            "percentage": result.percentage,
        },
        "question_results": graded_questions,
        "student_progress": {
            "total_exams_taken": progress_record.total_exams_taken,
            "exams_passed": progress_record.exams_passed,
            "exams_failed": progress_record.exams_failed,
            "total_points": progress_record.total_points,
            "overall_percentage": progress_record.overall_percentage,
            "overall_grade": progress_record.overall_grade
        }
    }

    return response_payload
