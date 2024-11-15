from datetime import datetime
from typing import Optional
import uuid
from pydantic import Field
from sqlmodel import SQLModel, Field

class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class OnboardingQuestion(BaseModel, table=True):
    question: str