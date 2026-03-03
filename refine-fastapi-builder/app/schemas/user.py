from typing import Literal

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

Role = Literal["admin", "student"]


class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role = "student"


class UserPublic(SQLModel):
    id: int
    username: str
    email: str
    role: Role
    is_active: bool


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
