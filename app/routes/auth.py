# auth_routes.py

from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.utils.db import get_session
from app.utils.auth import get_current_user
from app.handlers.auth import handle_signup, handle_login, handle_refresh_token

auth_router = APIRouter(prefix="/auth")

# Signup Endpoint
@auth_router.post("/signup", response_model=UserResponse)
def signup(user_create: UserCreate, session: Session = Depends(get_session)):
    return handle_signup(user_create, session)

# Login Endpoint
@auth_router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)], session: Session = Depends(get_session)):
    return handle_login(form_data, session)

# Token Refresh Endpoint
@auth_router.post("/token/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    return handle_refresh_token(current_user)
