# app/routes/student.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.schemas.student import StudentProfileCreate, StudentProfileResponse
from app.models.user import StudentProfile
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.db import get_session

student_router = APIRouter(prefix="/student")

@student_router.post("/create_profile/", response_model=StudentProfileResponse)
def create_student_profile(
    profile_data: StudentProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if the user already has a student profile
    existing_profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists for this user.")

    # Create a new student profile
    student_profile = StudentProfile(
        id=current_user.id,
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
        exam_question_handling=profile_data.exam_question_handling,
        short_term_academic_goals=profile_data.short_term_academic_goals,
        long_term_academic_goals=profile_data.long_term_academic_goals,
        coumtry=profile_data.country
    )

    # Save the new profile to the database
    session.add(student_profile)
    session.commit()
    session.refresh(student_profile)

    return student_profile


@student_router.get('/get_student_profile', response_model=StudentProfileResponse)
def get_student_profile(session: Session = Depends(get_session),
                         current_user: User = Depends(get_current_user)):
    # Get the student profile of the current user
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")
    return profile


@student_router.put("/update_profile", response_model=StudentProfileResponse)
def update_student_profile(
    profile_data: StudentProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve the user's existing profile
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    # Update profile fields
    profile.age = profile_data.age
    profile.gender = profile_data.gender
    profile.social_interaction_style = profile_data.social_interaction_style
    profile.decision_making_approach = profile_data.decision_making_approach
    profile.current_level_of_education = profile_data.current_level_of_education
    profile.last_grade = profile_data.last_grade
    profile.favorite_subject = profile_data.favorite_subject
    profile.interested_career_paths = profile_data.interested_career_paths
    profile.free_time_activities = profile_data.free_time_activities
    profile.motivation_to_study = profile_data.motivation_to_study
    profile.exam_question_handling = profile_data.exam_question_handling
    profile.short_term_academic_goals = profile_data.short_term_academic_goals
    profile.long_term_academic_goals = profile_data.long_term_academic_goals

    # Save updates
    session.add(profile)
    session.commit()
    session.refresh(profile)

    return profile


@student_router.delete("/delete_profile", response_model=dict)
def delete_student_profile(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Retrieve the user's profile
    profile = session.exec(select(StudentProfile).where(StudentProfile.id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    # Delete the profile
    session.delete(profile)
    session.commit()

    return {"message": "Profile deleted successfully"}

@student_router.get("/get_all_profiles", response_model=List[StudentProfileResponse])
def get_all_student_profiles(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Only allow admin to view all profiles
    if current_user.email != "zainatteeq@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted to admin only")

    profiles = session.exec(select(StudentProfile)).all()
    return profiles
