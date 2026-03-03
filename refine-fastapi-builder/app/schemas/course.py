from datetime import datetime

from sqlmodel import Field, SQLModel


class CourseCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    credit_hours: int = Field(default=3, ge=1, le=12)
    max_students: int = Field(default=30, ge=1, le=500)


class CoursePublic(SQLModel):
    id: int
    title: str
    description: str | None
    credit_hours: int
    max_students: int
    created_at: datetime


class CourseUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    credit_hours: int | None = Field(default=None, ge=1, le=12)
    max_students: int | None = Field(default=None, ge=1, le=500)
