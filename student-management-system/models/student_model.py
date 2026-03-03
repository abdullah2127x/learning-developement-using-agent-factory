from typing import Literal, Optional

from pydantic import EmailStr
from sqlmodel import ARRAY, Column, Field, Integer, SQLModel, String


class BaseStudent(SQLModel):
    name: str = Field(sa_column=Column(String(100)))
    email: EmailStr = Field(nullable=False)
    courses: list[str] = Field(sa_column=Column(ARRAY(String(100)), nullable=False))
    role: Literal["user", "admin"] = Field(
        sa_column=Column(String(100), default="user")
    )


class Student(BaseStudent, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str = Field(sa_column=Column(String(100), nullable=False))


class StudentCreate(BaseStudent):
    password: str = Field(sa_column=Column(String(100), nullable=False))


class StudentRead(BaseStudent):
    pass


class StudentUpdate(SQLModel):
    name: Optional[str] = Field(default=None)
    courses: Optional[list[str]] = Field(default=None)
    password: Optional[str] = Field(default=None)
