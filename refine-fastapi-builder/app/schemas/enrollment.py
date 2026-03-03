from datetime import date
from typing import Literal

from sqlmodel import SQLModel

EnrollmentStatus = Literal["enrolled", "completed", "dropped"]
Grade = Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]


class EnrollmentCreate(SQLModel):
    student_id: int
    course_id: int


class EnrollmentPublic(SQLModel):
    id: int
    student_id: int
    course_id: int
    enrollment_date: date
    grade: Grade | None
    status: EnrollmentStatus


class EnrollmentUpdate(SQLModel):
    grade: Grade | None = None
    status: EnrollmentStatus | None = None
