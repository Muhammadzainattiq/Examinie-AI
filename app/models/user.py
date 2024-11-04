from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from app.models.base import BaseModel
from app.models.enum import DecisionMakingApproach, ExamQuestionHandling, MotivationToStudy, SocialInteractionStyle
from datetime import date

from app.models.exam import Exam, ExamAttempt
from app.models.student import StudentProfile
from app.models.teacher import TeacherProfile


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str = Field(unique=True)
    password_hash: str
    role: str  # Enum ('student' or 'teacher')
    student_profile: Optional["StudentProfile"] = Relationship(back_populates="user")
    teacher_profile: Optional["TeacherProfile"] = Relationship(back_populates="user")

