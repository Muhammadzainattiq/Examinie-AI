from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.enum import QuestionType
from app.models.exam import Answer, Exam, ExamAttempt, Question
from app.schemas.exam import ExamCreate, ExamResponse, QuestionCreate, ExamAttemptCreate, ExamAttemptResponse
from app.models.user import StudentProfile, User
from app.utils.auth import get_current_user
from app.utils.db import get_session

exam_router = APIRouter(prefix="/exams")

@exam_router.post("/create_exam/", response_model=ExamResponse)
async def create_exam(
    exam_data: ExamCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if the current user has a StudentProfile
    student_profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    
    if student_profile:
        # User is a student, assign student_id
        new_exam = Exam(**exam_data.dict(), student_id=student_profile.id)
    else:
        # If user is not a student, raise an error or assign teacher_id as needed
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not have a student profile")

    session.add(new_exam)
    session.commit()
    session.refresh(new_exam)
    return new_exam


@exam_router.get("/get_exam/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve a specific exam by ID
    exam = session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return exam

@exam_router.post("/start_exam_attempt/{exam_id}/")
async def start_exam_attempt(
    exam_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if an existing attempt exists; otherwise, create a new one
    attempt = session.exec(
        select(ExamAttempt)
        .where(ExamAttempt.exam_id == exam_id)
        .where(ExamAttempt.student_id == current_user.id)
    ).first()

    if not attempt:
        # Create a new ExamAttempt record
        attempt = ExamAttempt(
            exam_id=exam_id,
            student_id=current_user.id,
            score=None,  # Initialize score
            completed=False
        )
        session.add(attempt)
        session.commit()
        session.refresh(attempt)

    return attempt


@exam_router.get("/{exam_id}/questions", response_model=List[QuestionCreate])
async def get_exam_questions(
    exam_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve questions for a specific exam
    questions = session.exec(select(Question).where(Question.exam_id == exam_id)).all()
    if not questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questions not found for this exam")
    return questions


@exam_router.post("/complete_exam_attempt/{exam_id}/{attempt_id}", response_model=ExamAttemptResponse)
async def complete_exam_attempt(
    exam_id: UUID,
    attempt_id: UUID,
    score: int,  # Calculated score based on responses
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve the specific exam attempt to mark as completed
    attempt = session.get(ExamAttempt, attempt_id)
    if not attempt or attempt.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam attempt not found")

    # Mark the attempt as completed, add score, and timestamp
    attempt.completed = True
    attempt.score = score
    attempt.submitted_at = datetime.utcnow()
    session.add(attempt)
    session.commit()
    session.refresh(attempt)
    return attempt


@exam_router.post("/add_question/{exam_id}/", response_model=QuestionCreate)
async def add_question_to_exam(
    exam_id: UUID,
    question_data: QuestionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    exam = session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

    # Create question based on type and add it to the exam
    question = Question(**question_data.dict(), exam_id=exam_id)
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


@exam_router.post("/submit_question_answer/{exam_id}/{question_id}/")
async def submit_answer(
    exam_id: UUID,
    question_id: UUID,
    response: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    question = session.get(Question, question_id)
    if not question or question.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found in this exam")

    # Retrieve the exam attempt for this student and exam
    attempt = session.exec(
        select(ExamAttempt)
        .where(ExamAttempt.exam_id == exam_id)
        .where(ExamAttempt.student_id == current_user.id)
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam attempt not found. Ensure the exam has been started."
        )

    # Logic for handling different question types
    if question.type == QuestionType.MCQ:
        # Verify response against Choice table for MCQ
        is_correct = any(choice.text == response and choice.is_correct for choice in question.choices)
    else:
        # For non-MCQ, mark `is_correct` as None, to be evaluated later if needed
        is_correct = None

    # Record answer with the found attempt_id
    answer = Answer(
        attempt_id=attempt.id,  # Use the found attempt ID here
        question_id=question_id,
        response=response,
        is_correct=is_correct
    )
    session.add(answer)
    session.commit()
    session.refresh(answer)
    return answer
