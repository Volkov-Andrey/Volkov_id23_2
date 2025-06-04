from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.cruds.user import create_user, get_user_by_email
from app.schemas.user import UserCreate, User, UserResponse
from app.services.auth import authenticate_user, create_access_token, get_current_user
from app.db.session import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/sign-up/", response_model=UserResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    logger.debug(f"Sign-up attempt for email: {user.email}")
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        logger.debug("Email already registered")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    new_user = create_user(db, user)
    token = create_access_token(data={"sub": new_user.email})
    logger.debug(f"User signed up: {new_user.email}, token: {token[:10]}...")
    return UserResponse(id=new_user.id, email=new_user.email, token=token)

@router.post("/login/", response_model=dict)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.debug(f"Login attempt for username: {form_data.username}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.debug("Login failed: incorrect email or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.email})
    logger.debug(f"Login successful for {user.email}, token: {token[:10]}...")
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/me/", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    logger.debug(f"Fetching user: {current_user.email}")
    return current_user