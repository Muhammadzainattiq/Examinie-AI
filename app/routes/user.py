from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.db import get_session
from app.handlers.user import (
    handle_get_all_users,
    handle_update_user,
    handle_delete_user,
    handle_get_user_details,
)

user_router = APIRouter(prefix="/user")


@user_router.get("/get_all_users", response_model=List[UserResponse])
def get_all_users(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return handle_get_all_users(session, current_user)


@user_router.put("/update_user/", response_model=UserResponse)
def update_user(user_data: UserCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return handle_update_user(user_data, session, current_user)


@user_router.delete("/delete_user/", status_code=status.HTTP_200_OK)
def delete_user(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return handle_delete_user(session, current_user)


@user_router.get("/get_current_user_details/", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)):
    return handle_get_user_details(current_user)
