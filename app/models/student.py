# student.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date
from app.models.base import BaseModel
from app.models.exam import Exam
from app.models.user import User  # Import User to link to StudentProfile
from app.models.enum import CurrentLevelOfEducation, DecisionMakingApproach, ExamQuestionHandling, FavoriteSubject, LatestGrade, MotivationToStudy, SocialInteractionStyle

class StudentProfile(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    age: Optional[int]
    gender: Optional[str]
    social_interaction_style: Optional[SocialInteractionStyle]
    decision_making_approach: Optional[DecisionMakingApproach]
    current_level_of_education: Optional[CurrentLevelOfEducation]
    last_grade: Optional[LatestGrade]
    favorite_subjects: Optional[List[FavoriteSubject]]
    interested_career_paths: Optional[str]
    free_time_activities: Optional[str]
    motivation_to_study: Optional[MotivationToStudy]
    exam_question_handling: Optional[ExamQuestionHandling]
    short_term_academic_goals: Optional[str]
    long_term_academic_goals: Optional[str]

    exams: List[Exam] = Relationship(back_populates="student")
    user: User = Relationship(back_populates="student_profile")
    progress_records: List["StudentProgress"] = Relationship(back_populates="student_profile")

class StudentProgress(BaseModel, table=True):
    id: int = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="studentprofile.user_id")
    date_recorded: date
    last_exam_score: Optional[float]
    total_exams_taken: int = Field(default=0)
    exams_passed: int = Field(default=0)
    exams_failed: int = Field(default=0)
    total_points: int = Field(default=0)
    overall_grade: Optional[str]
    overall_percentage: Optional[float]
    time_spent: int = Field(default=0)

    student_profile: StudentProfile = Relationship(back_populates="progress_records")