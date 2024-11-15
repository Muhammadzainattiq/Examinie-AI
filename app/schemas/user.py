from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import EmailStr
from sqlmodel import SQLModel
from app.models.enum import Role


class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str
    role: Role
class UserResponse(SQLModel):
    username: str
    email: EmailStr
    role: str
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]


class Token(SQLModel):
    access_token: str
    token_type: str