from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from app.models.base import BaseModel
from app.models.enum import DifficultyLevel, QuestionType
from app.models.user import StudentProfile, TeacherProfile

class Exam(BaseModel, table=True):
    id: int = Field(default=None, primary_key=True)  # Add a primary key
    title: str
    creator_id: int = Field(foreign_key="user.id")  # Generalized for both roles
    question_type: QuestionType  # Use Enum for question types
    difficulty: DifficultyLevel  # Use Enum for difficulty levels
    num_questions: int
    time_limit: Optional[int]  # Time limit in minutes
    marks_per_question: int
    total_marks: Optional[int]  
    questions: List["Question"] = Relationship(back_populates="exam")
    attempts: List["ExamAttempt"] = Relationship(back_populates="exam")
    creator: Optional[TeacherProfile] = Relationship(back_populates="created_exams")  # If creator is a teacher
    student: Optional[StudentProfile] = Relationship(back_populates="exams")  # If needed, but not strictly required

class ExamAttempt(BaseModel, table=True):
    id: int = Field(default=None, primary_key=True)  # Add a primary key
    exam_id: int = Field(foreign_key="exam.id")
    student_id: int = Field(foreign_key="studentprofile.user_id")
    score: Optional[int]
    completed: bool = False
    submitted_at: Optional[datetime]
    answers: List["Answer"] = Relationship(back_populates="attempt")
    exam: Exam = Relationship(back_populates="attempts")
    student: StudentProfile = Relationship()


class Question(BaseModel, table=True):
    exam_id: int = Field(foreign_key="exam.id")
    content: str
    type: str  # Enum (MCQ, True/False, etc.)
    choices: Optional[List[str]] = Field(default=None)  # JSON format for multiple choices
    correct_answer: Optional[str]  # Store correct answer
    marks: int
    exam: Exam = Relationship(back_populates="questions")

class Answer(BaseModel, table=True):
    attempt_id: int = Field(foreign_key="examattempt.id")
    question_id: int = Field(foreign_key="question.id")
    response: str  # Could be JSON for MCQ or text for other types
    is_correct: bool = False
    attempt: ExamAttempt = Relationship(back_populates="answers")
    question: Question = Relationship()


class Result(BaseModel, table=True):
    exam_attempt_id: int = Field(foreign_key="examattempt.id")
    total_marks: int = Field(foreign_key="examattempt.total_marks")
    obtained_marks: int
    grade: Optional[str] = Field(default=None)  # Grade based on obtained_marks
    percentage: Optional[int] = Field(default=None) # Percentage based on marks
    feedback: Optional[str] = Field(default=None)  # Feedback comments
    exam_attempt: ExamAttempt = Relationship()