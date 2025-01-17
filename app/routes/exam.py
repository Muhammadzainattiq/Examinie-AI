from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.handlers.exam import handle_complete_exam_attempt, handle_create_exam, handle_get_full_exam, handle_start_exam_attempt, handle_submit_answer, handle_sumbit_all_answers
from app.schemas.exam import BulkAnswerSubmit, ExamCreate, ExamResponse, FullExamResponse, QuestionCreate, ExamAttemptCreate, ExamAttemptResponse
from app.models.user import  User
from app.utils.auth import get_current_user
from app.utils.db import get_session


exam_router = APIRouter(prefix="/exams")

@exam_router.post("/create_exam/", response_model=ExamResponse)
async def create_exam(
    exam_data: ExamCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    exam = handle_create_exam(session, current_user, exam_data)
    return exam

@exam_router.post("/start_exam_attempt/{exam_id}/")
async def start_exam_attempt(
    exam_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_start_exam_attempt(exam_id, session, current_user)
    return response

@exam_router.post("/complete_exam_attempt/{exam_id}/{attempt_id}", response_model=ExamAttemptResponse)
async def complete_exam_attempt(
    exam_id: UUID,
    attempt_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_complete_exam_attempt(exam_id,attempt_id,session, current_user)
    return response


@exam_router.post("/submit_question_answer/{exam_id}/{question_id}/")
async def submit_answer(
    exam_id: UUID,
    question_id: UUID,
    response: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_submit_answer(exam_id, question_id, response, session, current_user)
    return response


@exam_router.get("/get_full_exam/{exam_id}", response_model=FullExamResponse)
async def get_exam(
    exam_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    exam_data = handle_get_full_exam(exam_id, session)
    return exam_data


@exam_router.post("/submit_all_answers/{exam_id}/")
async def submit_all_answers(
    exam_id: UUID,
    bulk_answers: BulkAnswerSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_sumbit_all_answers(exam_id, bulk_answers, session, current_user)
    return response
