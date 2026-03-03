from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(200), index=True, nullable=False))
    description: str | None = Field(sa_column=Column(Text, nullable=True))
    credit_hours: int = Field(sa_column=Column(Integer, nullable=False, server_default="3"))
    max_students: int = Field(sa_column=Column(Integer, nullable=False, server_default="30"))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    enrollments: list["Enrollment"] = Relationship(back_populates="course")
