from datetime import date, datetime

from sqlmodel import Field, SQLModel


class StudentCreate(SQLModel):
    user_id: int
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date | None = None


class StudentPublic(SQLModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    date_of_birth: date | None
    created_at: datetime


class StudentUpdate(SQLModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
