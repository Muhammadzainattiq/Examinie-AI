# user.py
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional
import uuid
from sqlmodel import SQLModel, Field, Relationship
from app.models.enum import (
    CareerPath,
    Country,
    Gender,
    Role,
    CurrentLevelOfEducation,
    DecisionMakingApproach,
    FavoriteSubject,
    LatestGrade,
    MotivationToStudy,
    SocialInteractionStyle
)


if TYPE_CHECKING:
    from app.models.exam import Exam, Result

class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class User(BaseModel, table=True):
    username: str
    email: str = Field(unique=True)
    password_hash: str
    role: Role

    # Define relationships
    student_profile: Optional["StudentProfile"] = Relationship(back_populates="user")
    teacher_profile: Optional["TeacherProfile"] = Relationship(back_populates="user")
    


class StudentProfile(SQLModel, table=True):
    id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)  # Foreign key reference
    name: Optional[str]
    email: Optional[str]
    age: Optional[int]
    gender: Optional[Gender]
    country: Optional[Country]
    social_interaction_style: Optional[SocialInteractionStyle]
    decision_making_approach: Optional[DecisionMakingApproach]
    current_level_of_education: Optional[CurrentLevelOfEducation]
    last_grade: Optional[LatestGrade]
    favorite_subject: Optional[FavoriteSubject]
    free_time_activities: Optional[str]
    motivation_to_study: Optional[MotivationToStudy]
    short_term_academic_goals: Optional[str]
    long_term_academic_goals: Optional[str]
    interested_career_paths: Optional[CareerPath] 
    profile_summary : Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Define relationships
    exam_results: List["Result"] = Relationship(back_populates="student")
    user: Optional["User"] = Relationship(back_populates="student_profile")  # Ensure this line is present
    created_exams: List["Exam"] = Relationship(back_populates="student_creator")
    progress_records: List["StudentProgress"] = Relationship(back_populates="student_profile")


class StudentProgress(BaseModel, table=True):
    profile_id: uuid.UUID = Field(foreign_key="studentprofile.id")  # Foreign key reference
    date_recorded: date
    last_exam_score: Optional[float]
    total_exams_taken: int = Field(default=0)
    exams_passed: int = Field(default=0)
    exams_failed: int = Field(default=0)
    total_points: int = Field(default=0)
    overall_grade: Optional[LatestGrade]
    overall_percentage: Optional[float]


    # Relationships
    student_profile: Optional["StudentProfile"] = Relationship(back_populates="progress_records")



class TeacherProfile(SQLModel, table=True):
    id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)  # Foreign key reference
    created_exams: List["Exam"] = Relationship(back_populates="teacher_creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    user: Optional["User"] = Relationship(back_populates="teacher_profile")