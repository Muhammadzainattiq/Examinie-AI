from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel

class OnboardingQuestionCreate(SQLModel):
    question: str

class OnboardingQuestionResponse(SQLModel):
    question: str
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]