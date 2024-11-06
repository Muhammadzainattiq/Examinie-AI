# app/schemas/student.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from app.models.enum import (
    CareerPath,
    SocialInteractionStyle,
    DecisionMakingApproach,
    CurrentLevelOfEducation,
    LatestGrade,
    FavoriteSubject,
    MotivationToStudy,
    ExamQuestionHandling,
)

class StudentProfileCreate(BaseModel):
    age: Optional[int]
    gender: Optional[str]
    social_interaction_style: Optional[SocialInteractionStyle]
    decision_making_approach: Optional[DecisionMakingApproach]
    current_level_of_education: Optional[CurrentLevelOfEducation]
    last_grade: Optional[LatestGrade]
    favorite_subject: Optional[FavoriteSubject]
    interested_career_paths: Optional[CareerPath]
    free_time_activities: Optional[str]
    motivation_to_study: Optional[MotivationToStudy]
    exam_question_handling: Optional[ExamQuestionHandling]
    short_term_academic_goals: Optional[str]
    long_term_academic_goals: Optional[str]


class StudentProfileResponse(StudentProfileCreate):
    user_id: UUID
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True