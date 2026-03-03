from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import Token, UserCreate, UserPublic
from app.services.auth_service import AuthService
from app.utils.rate_limit import limiter

router = APIRouter()


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
@limiter.limit("10/hour")  # Max 10 registrations per hour to prevent spam
def register(
    request: Request,
    user_in: UserCreate,
    auth_service: AuthService = Depends(),
):
    return auth_service.register(user_in)


@router.post(
    "/token",
    response_model=Token,
    summary="Login and get access token",
)
@limiter.limit("5/minute")  # Max 5 login attempts per minute
def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(),
):
    return auth_service.authenticate(form_data.username, form_data.password)
