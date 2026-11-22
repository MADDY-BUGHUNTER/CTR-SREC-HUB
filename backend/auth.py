"""Handle password hashing, login tokens and the current logged-in user."""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User


security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password: plain text goes in; a safe hash comes out."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against its stored hash; never return the password."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    """Create a signed token that expires after the configured minutes."""
    expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    expires = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    secret = os.getenv("JWT_SECRET", "replace-this-with-a-long-random-secret")
    return jwt.encode({"sub": str(user_id), "exp": expires}, secret, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Read and validate a bearer token, then return its saved user."""
    secret = os.getenv("JWT_SECRET", "replace-this-with-a-long-random-secret")
    try:
        payload = jwt.decode(credentials.credentials, secret, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in again.",
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in again.",
        )
    return user
