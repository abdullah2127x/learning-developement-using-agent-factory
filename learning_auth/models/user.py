# # models/user.py
# ------------------------------Manual setup-------------------//
# from datetime import datetime
# from typing import Annotated, Optional

# from pydantic import EmailStr
# from sqlmodel import Field, SQLModel

# from core.config import settings
# from core.security import get_password_hash, verify_password


# class UserBase(SQLModel):
#     email: EmailStr = Field(index=True, unique=True, max_length=255)
#     is_active: bool = Field(default=True)
#     is_verified: bool = Field(default=False)
#     role: str = Field(default="user", max_length=50)   # We will turn this into Enum later

    

# class User(UserBase, table=True):
#     __tablename__ = "users"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     hashed_password: str = Field(min_length=60, max_length=500)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})

#     # Type-safe helper methods
#     def set_password(self, plain_password: str) -> None:
#         """Use the configured hasher from settings."""
#         self.hashed_password = get_password_hash(
#             plain_password,
#             hasher=settings.password_hasher
#         )

#     def verify_password(self, plain_password: str) -> bool:
#         """Verify using the same hasher that was used to create the hash."""
#         return verify_password(
#             plain_password,
#             self.hashed_password,
#             hasher=settings.password_hasher
#         )

# # Response model (never returns hashed_password)
# class UserRead(UserBase):
#     id: int
#     created_at: datetime
#     # hashed_password is excluded automatically because it's not in this model


# -------------------------setup to sync with better auth-------------------------//
# models/user.py
from datetime import datetime
from typing import Annotated, Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from core.config import settings
from core.security import get_password_hash, verify_password


class UserBase(SQLModel):
    pass
    # email: EmailStr = Field(index=True, unique=True, max_length=255)
    # is_active: bool = Field(default=True)
    # is_verified: bool = Field(default=False)
    # role: str = Field(default="user", max_length=50)   # We will turn this into Enum later

    

class User(UserBase,table=True):
    __tablename__ = "user"
    email: EmailStr = Field(index=True, unique=True, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    # id: Optional[int] = Field(default=None, primary_key=True)
    id: Optional[str] = Field(default=None, primary_key=True)
    # hashed_password: str = Field(min_length=60, max_length=500)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})

class UserRead(UserBase):
    id: str
    createdAt: datetime