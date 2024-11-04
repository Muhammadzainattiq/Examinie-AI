# teacher.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from app.models.base import BaseModel
from app.models.exam import Exam
from app.models.user import User  # Importing User to link to TeacherProfile

class TeacherProfile(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    created_exams: List["Exam"] = Relationship(back_populates="creator")
    user: User = Relationship(back_populates="teacher_profile")
