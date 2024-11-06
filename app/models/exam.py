# exam.py
from datetime import datetime
from uuid import UUID
import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from app.models.enum import DifficultyLevel, QuestionType
from app.models.user  import StudentProfile, TeacherProfile


class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class Exam(BaseModel, table=True):
    title: str
    questions_type: QuestionType
    difficulty: DifficultyLevel
    num_questions: int
    time_limit: Optional[int]
    marks_per_question: int
    total_marks: Optional[int]

    # Foreign keys for student and teacher creators
    student_id: Optional[UUID] = Field(default=None, foreign_key="studentprofile.id")
    teacher_id: Optional[UUID] = Field(default=None, foreign_key="teacherprofile.id")

    # Relationships
    student_creator: Optional["StudentProfile"] = Relationship(back_populates="created_exams")
    teacher_creator: Optional["TeacherProfile"] = Relationship(back_populates="created_exams")
    questions: List["Question"] = Relationship(back_populates="exam")
    attempts: List["ExamAttempt"] = Relationship(back_populates="exam")

class ExamAttempt(BaseModel, table=True):
    exam_id: UUID = Field(foreign_key="exam.id")  # Foreign key reference
    student_id: UUID = Field(foreign_key="studentprofile.id")  # Foreign key reference
    score: Optional[int] = None
    completed: bool = False
    submitted_at: Optional[datetime] = None

    answers: List["Answer"] = Relationship(back_populates="attempt")
    exam: Optional["Exam"] = Relationship(back_populates="attempts")

class Question(BaseModel, table=True):
    exam_id: UUID = Field(foreign_key="exam.id")  # Foreign key reference
    content: str
    type: QuestionType
    # choices: Optional[List[str]] = Field(default=None)  # Use JSON for choice storage
    correct_answer: Optional[str] = None
    marks: int

    exam: Optional["Exam"] = Relationship(back_populates="questions")

class Answer(BaseModel, table=True):
    attempt_id: UUID = Field(foreign_key="examattempt.id")  # Foreign key reference
    question_id: UUID = Field(foreign_key="question.id")  # Foreign key reference
    response: str
    is_correct: bool = False

    attempt: Optional["ExamAttempt"] = Relationship(back_populates="answers")
    question: Optional["Question"] = Relationship()

class Result(BaseModel, table=True):
    exam_attempt_id: UUID = Field(foreign_key="examattempt.id")  # Foreign key reference
    total_marks: Optional[int] = None
    obtained_marks: int
    grade: Optional[str] = None
    percentage: Optional[float] = None
    feedback: Optional[str] = None

    exam_attempt: Optional["ExamAttempt"] = Relationship()



# ----------------------------------------------------------------
#to avoid circular imports defining types here:

