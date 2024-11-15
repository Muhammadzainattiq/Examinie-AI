# auth_handlers.py

from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.models.user import User
from app.schemas.user import UserCreate, Token
from app.utils.auth import get_password_hash, verify_password, create_access_token, get_current_user


# Signup handler function
def handle_signup(user_create: UserCreate, session: Session) -> User:
    user_exists = session.exec(select(User).where(User.email == user_create.email)).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = get_password_hash(user_create.password)
    new_user = User(username=user_create.username, email=user_create.email, password_hash=hashed_password, role = user_create.role)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

# Login handler function
def handle_login(form_data, session: Session) -> Token:
    db_user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Refresh token handler function
def handle_refresh_token(current_user: User) -> Token:
    access_token = create_access_token(data={"sub": str(current_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
