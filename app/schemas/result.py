from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from sqlmodel import SQLModel
from app.models.enum import LatestGrade

# ResultCreate schema without grade and percentage fields
class ResultCreate(BaseModel):
    exam_title: Optional[str] = None  # New field for storing exam title
    total_marks: Optional[int] = None
    obtained_marks: int



class ResultResponse(BaseModel):
    id: UUID
    exam_attempt_id: UUID
    student_id: Optional[UUID]
    exam_title: Optional[str]  # New field for response
    total_marks: Optional[int]
    obtained_marks: int
    grade: Optional[str]
    percentage: Optional[float]
    created_at: datetime

    class Config:
        orm_mode = True


class StudentProgressResponse(BaseModel):
    id: UUID
    total_points: int
    overall_percentage: Optional[float] = None
    overall_grade: Optional[LatestGrade] = None
    total_exams_taken: int
    exams_passed: int
    exams_failed: int
    last_exam_score: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True


class QuestionResult(SQLModel):
    marks: int
    feedback: str