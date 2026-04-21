# core/cookies.py
from fastapi import Response
from datetime import datetime, timezone, timedelta
from core.config import settings

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set httpOnly cookies for both tokens."""
    
    # Access Token Cookie (short lived)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=settings.cookie_http_only,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    
    # Refresh Token Cookie (long lived)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=settings.cookie_http_only,
        secure=settings.cookie_secure,
        samesite=settings.cookie_same_site,
        max_age=settings.cookie_max_age,
        path="/",
    )

def delete_auth_cookies(response: Response):
    """Logout - clear cookies."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")