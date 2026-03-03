from datetime import timedelta

import structlog
from fastapi import Depends, HTTPException, status

from app.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import Token, UserCreate

logger = structlog.get_logger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    def register(self, user_in: UserCreate) -> User:
        logger.info("registering_user", username=user_in.username)
        if self.user_repo.get_by_username(user_in.username):
            logger.warning("registration_failed", reason="username_taken", username=user_in.username)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        if self.user_repo.get_by_email(user_in.email):
            logger.warning("registration_failed", reason="email_taken", email=user_in.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
        )
        user = self.user_repo.create(db_user)
        logger.info("user_registered", user_id=user.id, username=user.username)
        return user

    def authenticate(self, username: str, password: str) -> Token:
        logger.info("authenticating_user", username=username)
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            logger.warning("authentication_failed", username=username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            logger.warning("authentication_failed", reason="inactive_user", username=username)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        logger.info("user_authenticated", user_id=user.id)
        return Token(access_token=access_token)
