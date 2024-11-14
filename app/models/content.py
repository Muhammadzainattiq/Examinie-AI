from datetime import datetime
from uuid import UUID
import uuid
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING, Optional
from app.models.base import BaseModel
from app.models.enum import FileType

if TYPE_CHECKING:
    from app.models.exam import Exam

class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
class Content(BaseModel, table=True):
    title: str
    description: Optional[str] = Field(default=None)
    file_type: FileType  # Type of the file (PDF, DOCX, image, video, etc.)
    contents: str
    exam_id: Optional[UUID] = Field(default=None, foreign_key="exam.id")
    exam: Optional["Exam"] = Relationship(back_populates="contents")