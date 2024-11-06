from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.models.onboarding import OnboardingQuestion
from app.schemas.onboarding import OnboardingQuestionCreate, OnboardingQuestionResponse
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.db import get_session
from sqlmodel import select

onboarding_router = APIRouter(prefix = "/onboarding")


@onboarding_router.post("/add_onboarding_question/", response_model=OnboardingQuestionResponse)
async def add_question(question:OnboardingQuestionCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.email!= "zainatteeq@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can add onboarding questions")
    
    new_question = OnboardingQuestion(question = question.question)
    session.add(new_question)
    session.commit()
    session.refresh(new_question)

    return new_question


@onboarding_router.get('/get_onboarding_questions', response_model=List[OnboardingQuestionResponse])
async def get_questions(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    questions = session.exec(select(OnboardingQuestion)).all()
    return questions



@onboarding_router.put("/update_onboarding_question/{question_id}", response_model=OnboardingQuestionResponse)
async def update_question(
    question_id: UUID,
    question_data: OnboardingQuestionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "zainatteeq@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update questions")

    question = session.get(OnboardingQuestion, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    question.question = question_data.question
    session.add(question)
    session.commit()
    session.refresh(question)

    return question


@onboarding_router.delete("/delete_onboarding_question/{question_id}", status_code=status.HTTP_200_OK)
async def delete_question(
    question_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.email != "zainatteeq@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete questions")

    question = session.get(OnboardingQuestion, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    session.delete(question)
    session.commit()

    return {"message": "Question deleted successfully"}


@onboarding_router.get("/get_single_question/{question_id}", response_model=OnboardingQuestionResponse)
async def get_question(
    question_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    question = session.get(OnboardingQuestion, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    return question
