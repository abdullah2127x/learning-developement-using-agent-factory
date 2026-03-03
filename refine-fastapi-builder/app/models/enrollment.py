from datetime import date, datetime

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.models.course import Course
from app.models.student import Student


class Enrollment(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("student_id", "course_id"),)

    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    enrollment_date: date = Field(default_factory=lambda: datetime.utcnow().date())
    grade: str | None = Field(sa_column=Column(String(2), nullable=True))
    status: str = Field(sa_column=Column(String(10), nullable=False, server_default="enrolled"))

    student: Student = Relationship(back_populates="enrollments")
    course: Course = Relationship(back_populates="enrollments")
