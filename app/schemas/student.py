# app/schemas/student.py
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from app.models.enum import (
    CareerPath,
    Country,
    Gender,
    SocialInteractionStyle,
    DecisionMakingApproach,
    CurrentLevelOfEducation,
    LatestGrade,
    FavoriteSubject,
    MotivationToStudy,
)

class StudentProfileCreate(BaseModel):
    age: Optional[int]
    gender: Optional[Gender]
    country: Optional[Country]
    social_interaction_style: Optional[SocialInteractionStyle]
    decision_making_approach: Optional[DecisionMakingApproach]
    current_level_of_education: Optional[CurrentLevelOfEducation]
    last_grade: Optional[LatestGrade]
    favorite_subject: Optional[FavoriteSubject]
    interested_career_paths: Optional[CareerPath]
    free_time_activities: Optional[str]
    motivation_to_study: Optional[MotivationToStudy]
    short_term_academic_goals: Optional[str]
    long_term_academic_goals: Optional[str]


class StudentProfileResponse(StudentProfileCreate):
    id: UUID
    name: str
    email: str
    profile_summary: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class StudentProgressResponse(BaseModel):
    id: UUID
    profile_id: UUID
    date_recorded: date
    last_exam_score: Optional[float] = None
    total_exams_taken: int
    exams_passed: int
    exams_failed: int
    total_points: int
    overall_grade: Optional[LatestGrade] = None
    overall_percentage: Optional[float] = None

    class Config:
        orm_mode = True