from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.handlers.result import handle_generate_and_update_result, handle_get_last_exam_result, handle_get_result, handle_get_student_results
from app.schemas.result import  ResultResponse
from app.utils.db import get_session
from app.utils.auth import get_current_user
from app.models.user import User
from fastapi import APIRouter, Depends
from uuid import UUID

result_router = APIRouter(prefix="/results")

@result_router.get("/get_result/{result_id}/", response_model=ResultResponse)
async def get_result(
    result_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_get_result(result_id, session, current_user)
    return response


@result_router.get("/get_all_student_results/", response_model=List[ResultResponse])
async def get_student_results(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_get_student_results(session, current_user)
    return response

@result_router.get("/get_last_exam_result/", response_model=ResultResponse)
async def get_last_exam_result(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_get_last_exam_result(session, current_user)
    return response


@result_router.post("/generate_and_update_result/{exam_attempt_id}")
async def generate_and_update_result(
    exam_attempt_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    response = handle_generate_and_update_result(exam_attempt_id, session, current_user)
    return response