from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from app.models.base import BaseModel
from app.models.enum import FileType
from app.models.exam import Exam

class Content(BaseModel, table=True):
    title: str
    description: Optional[str] = Field(default=None)
    file_type: FileType  # Type of the file (PDF, DOCX, image, video, etc.)
    file_url: str   # URL or path to the uploaded file
    exam_id: Optional[int] = Field(default=None, foreign_key="exam.id")
    exam: Optional[Exam] = Relationship(back_populates="contents")