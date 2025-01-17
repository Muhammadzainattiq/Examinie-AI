from typing import List
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from app.schemas.student import StudentProfileCreate, StudentProfileResponse
from app.models.user import StudentProfile, User
from app.utils.auth import get_current_user
from app.utils.db import get_session
from app.utils.generate_profile_summary import generate_profile_summary


def handle_create_student_profile(
    profile_data: StudentProfileCreate,
    session: Session,
    current_user: User
):
    existing_profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists for this user.")

    student_profile = StudentProfile(
        id=current_user.id,
        name=current_user.username,
        email=current_user.email,
        age=profile_data.age,
        gender=profile_data.gender,
        social_interaction_style=profile_data.social_interaction_style,
        decision_making_approach=profile_data.decision_making_approach,
        current_level_of_education=profile_data.current_level_of_education,
        last_grade=profile_data.last_grade,
        favorite_subject=profile_data.favorite_subject,
        interested_career_paths=profile_data.interested_career_paths,
        free_time_activities=profile_data.free_time_activities,
        motivation_to_study=profile_data.motivation_to_study,
        short_term_academic_goals=profile_data.short_term_academic_goals,
        long_term_academic_goals=profile_data.long_term_academic_goals,
        country=profile_data.country
    )

    profile_data_json = str({
        "name": current_user.username,
        "email": current_user.email,
        "age": profile_data.age,
        "gender": profile_data.gender,
        "social_interaction_style": profile_data.social_interaction_style,
        "decision_making_approach": profile_data.decision_making_approach,
        "current_level_of_education": profile_data.current_level_of_education,
        "last_grade": profile_data.last_grade,
        "favorite_subject": profile_data.favorite_subject,
        "interested_career_paths": profile_data.interested_career_paths,
        "free_time_activities": profile_data.free_time_activities,
        "short_term_academic_goals": profile_data.short_term_academic_goals,
        "long_term_academic_goals": profile_data.long_term_academic_goals,
        "country": profile_data.country
    })

    student_profile.profile_summary = generate_profile_summary(profile_data_json)
    session.add(student_profile)
    session.commit()
    session.refresh(student_profile)
    return student_profile


def handle_get_student_profile(session: Session, current_user: User):
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")
    return profile


def handle_update_student_profile(profile_data: StudentProfileCreate, session: Session, current_user: User):
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    profile.age = profile_data.age
    profile.gender = profile_data.gender
    profile.social_interaction_style = profile_data.social_interaction_style
    profile.decision_making_approach = profile_data.decision_making_approach
    profile.current_level_of_education = profile_data.current_level_of_education
    profile.last_grade = profile_data.last_grade
    profile.favorite_subject = profile_data.favorite_subject
    profile.interested_career_paths = profile_data.interested_career_paths
    profile.free_time_activities = profile_data.free_time_activities
    profile.short_term_academic_goals = profile_data.short_term_academic_goals
    profile.long_term_academic_goals = profile_data.long_term_academic_goals

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def handle_delete_student_profile(session: Session, current_user: User):
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    session.delete(profile)
    session.commit()
    return {"message": "Profile deleted successfully"}


def handle_get_all_student_profiles(session: Session, current_user: User):
    if current_user.email != "zainatteeq@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted to admin only")
    return session.exec(select(StudentProfile)).all()
