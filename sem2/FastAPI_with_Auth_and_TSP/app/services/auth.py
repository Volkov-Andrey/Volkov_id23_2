from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.session import get_db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")

def verify_password(plain_password, hashed_password):
    logger.debug("Verifying password")
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    logger.debug("Hashing password")
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    from app.cruds.user import get_user_by_email
    logger.debug(f"Authenticating user with email: {email}")
    user = get_user_by_email(db, email)
    if not user:
        logger.debug("User not found")
        return False
    if not verify_password(password, user.hashed_password):
        logger.debug("Password verification failed")
        return False
    logger.debug("User authenticated successfully")
    return user

def create_access_token(data: dict):
    logger.debug(f"Creating token with data: {data}")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(f"Generated token: {encoded_jwt}")
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    logger.debug(f"Validating token: {token[:10]}...")  # Частично скрыт для логов
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.debug("No email in token payload")
            raise credentials_exception
    except JWTError as e:
        logger.debug(f"JWTError: {str(e)}")
        raise credentials_exception
    from app.cruds.user import get_user_by_email
    user = get_user_by_email(db, email=email)
    if user is None:
        logger.debug(f"User with email {email} not found")
        raise credentials_exception
    logger.debug(f"Current user retrieved: {user.email}")
    return user