from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.user import User


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    first_name: str = Field(sa_column=Column(String(100), nullable=False))
    last_name: str = Field(sa_column=Column(String(100), nullable=False))
    date_of_birth: date | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship()
    enrollments: list["Enrollment"] = Relationship(back_populates="student")
