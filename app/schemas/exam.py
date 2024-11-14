from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.enum import DifficultyLevel, QuestionType

class ExamCreate(BaseModel):
    title: str
    questions_type: QuestionType
    difficulty: DifficultyLevel
    num_questions: int
    time_limit: Optional[int] = None
    marks_per_question: int
    total_marks: Optional[int] = None

class ExamResponse(BaseModel):
    id: UUID
    title: str
    questions_type: QuestionType
    difficulty: DifficultyLevel
    num_questions: int
    time_limit: Optional[int] = None
    marks_per_question: int
    total_marks: Optional[int] = None
    created_at: datetime
    student_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None

    class Config:
        orm_mode = True

class ExamAttemptCreate(BaseModel):
    score: Optional[int] = None
    completed: bool = False
    submitted_at: Optional[datetime] = None

class ExamAttemptResponse(BaseModel):
    id: UUID
    exam_id: UUID
    student_id: UUID
    score: Optional[int] = None
    completed: bool
    submitted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

class QuestionCreate(BaseModel):
    content: str
    type: QuestionType
    correct_answer: Optional[str] = None
    marks: int

class QuestionResponse(BaseModel):
    id: UUID
    exam_id: UUID
    content: str
    type: QuestionType
    correct_answer: Optional[str]
    marks: int
    created_at: datetime

    class Config:
        orm_mode = True

class AnswerCreate(BaseModel):
    attempt_id: UUID
    question_id: UUID
    response: str
    is_correct: bool

class AnswerResponse(BaseModel):
    id: UUID
    attempt_id: UUID
    question_id: UUID
    response: str
    is_correct: bool
    created_at: datetime

    class Config:
        orm_mode = True
