# core/auth.py
from typing import Annotated

from fastapi import Depends, Cookie, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlmodel import Session

from core.config import settings
from core.jwt import verify_token
from core.database import get_db
from models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scheme_name="JWT"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Main dependency: verifies JWT and returns full User object from Neon."""
    try:
        # print("Hit get_current_user with token:", token)  # Debugging line
        payload = verify_token(token)
        
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Invalid token payload")

        print("user id str in the get current user is :",user_id_str)  # Debugging line

        user = db.get(User, user_id_str)
        print("User fetched from DB:", user)  # Debugging line
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # if not user.is_active:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Inactive user"
        #     )
        return user 

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print("Unexpected error:", str(e))  # Debugging line
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Role-based authorization (still works the same)
def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required. You have '{current_user.role}'"
            )
        return current_user
    return role_checker

# async def get_current_user_from_refresh_token(
#     token: str = Depends(oauth2_scheme),   # we still use the same scheme
#     db: Session = Depends(get_db),
# ) -> User:
#     """Used ONLY by the refresh endpoint."""
#     try:
#         payload = verify_token(token, token_type="refresh")
#         user_id = int(payload.get("sub"))
#         user = db.get(User, user_id)
#         if not user or not user.is_active:
#             raise HTTPException(status_code=401, detail="Invalid refresh token")
#         return user
#     except ValueError as e:
#         raise HTTPException(status_code=401, detail=str(e))


# async def get_current_user_from_cookie(
#     access_token: str | None = Cookie(default=None),
#     db: Session = Depends(get_db),
# ) -> User:
#     """Read access_token from httpOnly cookie."""
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Not authenticated")
    
#     try:
#         payload = verify_token(access_token, token_type="access")
#         user_id = int(payload.get("sub"))
#         user = db.get(User, user_id)
#         if not user or not user.is_active:
#             raise HTTPException(status_code=401, detail="Invalid user")
#         return user
#     except ValueError:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")


# # For refresh endpoint
# async def get_refresh_token_from_cookie(
#     refresh_token: str | None = Cookie(default=None),
#     db: Session = Depends(get_db),
# ) -> User:
#     if not refresh_token:
#         raise HTTPException(status_code=401, detail="No refresh token")
    
#     try:
#         payload = verify_token(refresh_token, token_type="refresh")
#         user_id = int(payload.get("sub"))
#         user = db.get(User, user_id)
#         if not user or not user.is_active:
#             raise HTTPException(status_code=401, detail="Invalid refresh token")
#         return user
#     except ValueError:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")
    
# Type alias for clean usage
CurrentUser = Annotated[User, Depends(get_current_user)]