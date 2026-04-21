# routers/auth.py
from datetime import timedelta

from fastapi import APIRouter, Depends 
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from uuid import uuid4
from datetime import timedelta

from core.auth import CurrentUser, get_current_user
from core.config import settings
from core.cookies import delete_auth_cookies, set_auth_cookies
from core.database import get_db 
from models.user import User, UserRead

from uuid import uuid4
from datetime import timedelta
import  datetime

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str          # ← NEW
    token_type: str = "bearer"
    user: UserRead
    

# @router.post("/register", response_model=UserRead)
# async def register_user(
#     email: EmailStr,
#     password: str,
#     db: Session = Depends(get_db)
# ):
#     existing = db.exec(select(User).where(User.email == email)).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     user = User(email=email)
#     user.set_password(password) # Uses argon2id or bcrypt from settings

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     return user

# @router.post("/login", response_model=TokenResponse)
# async def login_for_access_token(
#     form_data: LoginRequest,
#     db: Session = Depends(get_db),
#     response: Response = None,
# ):
#     """Authenticate user and set JWTs in httpOnly cookies."""
#     # Find user
#     user = db.exec(select(User).where(User.email == form_data.email)).first()
#     if not user or not user.verify_password(form_data.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     # Create JWT
#     access_token = create_access_token(subject=user.id)

#     refresh_token = create_refresh_token(subject=user.id)

#     # Set httpOnly cookies
#     set_auth_cookies(response, access_token, refresh_token)

#     return TokenResponse(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         user=UserRead.model_validate(user)
#     )


# @router.post("/refresh", response_model=TokenResponse)
# async def refresh_access_token(
#     user: User = Depends(get_refresh_token_from_cookie),  # FastAPI handles token extraction + db
#     response: Response = None,  
# ):
#     """Use refresh token to get a new access token + new refresh token (rotation)."""
#     new_access_token = create_access_token(subject=user.id)
#     new_refresh_token = create_refresh_token(subject=user.id)   # rotation

#     set_auth_cookies(response, new_access_token, new_refresh_token)

#     return TokenResponse(
#         access_token=new_access_token,
#         refresh_token=new_refresh_token,
#         user=UserRead.model_validate(user)
#     )



# =============================
# @router.get("/me", response_model=UserRead)
# # async def read_users_me(current_user:User= Depends(get_current_user_from_cookie)):
# async def read_users_me(current_user:User= Depends(get_current_user)):
# # async def read_users_me(current_user:User= Depends(get_current_user_from_cookie)):
#     """Protected route - requires valid JWT"""
#     return current_user


@router.get("/me", response_model=User)
async def read_users_me(current_user:User= Depends(get_current_user)):
# async def read_users_me(current_user:User= Depends(get_current_user_from_cookie)):
    """Protected route - requires valid JWT"""
    print("final result - Current user in /me endpoint:", current_user)  # Debugging line
    return current_user
# ==================/
# @router.post("/logout")
# async def logout(response: Response):
#     delete_auth_cookies(response)
#     return {"message": "Successfully logged out"}

# @router.post("/verify-email")

