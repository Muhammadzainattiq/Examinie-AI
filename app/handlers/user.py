from typing import List
from fastapi import  HTTPException, status
from sqlmodel import Session, select
from app.schemas.user import UserCreate
from app.models.user import User
from app.utils.auth import get_password_hash

def handle_get_all_users(session: Session, current_user: User):
    if current_user.email != "zainatteeq@gmail.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can add onboarding questions")
    return session.exec(select(User)).all()


def handle_update_user(user_data: UserCreate, session: Session, current_user: User):
    user_id = current_user.id
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.username = user_data.username
    user.email = user_data.email
    user.password_hash = get_password_hash(user_data.password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def handle_delete_user(session: Session, current_user: User):
    user_id = current_user.id
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}


def handle_get_user_details(current_user: User):
    return current_user
