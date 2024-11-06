from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.utils.auth import get_password_hash, get_current_user
from app.utils.db import get_session
from sqlmodel import select
from sqlalchemy.orm import selectinload

user_router = APIRouter(prefix = "/user")


# Get All Users Endpoint
@user_router.get("/get_all_users", response_model=List[UserResponse])
def get_all_users(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.email!= "zainatteeq@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can add onboarding questions")
    users = session.exec(select(User)).all()
    return users


# Update User Endpoint
@user_router.put("/update_user/", response_model=UserResponse)
def update_user(user_data: UserCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update fields
    user.username = user_data.username
    user.email = user_data.email
    user.password_hash = get_password_hash(user_data.password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Delete User Endpoint
@user_router.delete("/delete_user/", status_code=status.HTTP_200_OK)
def delete_user(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}



@user_router.get("/get_current_user_details/", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)):
    return current_user


@user_router.get("/get_current_user_full_details/", response_model=UserResponse)
def get_current_user_full_details(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Load the current user along with profile data (either Student or Teacher)
    statement = (
        select(User)
        .options(
            selectinload(User.student_profile),
            selectinload(User.teacher_profile)
        )
        .where(User.id == current_user.id)
    )
    user = session.exec(statement).first()

    # Check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
