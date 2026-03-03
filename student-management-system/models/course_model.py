from typing import Optional
from sqlmodel import SQLModel, Field, Column, String

class CourseBase(SQLModel):
    name: str = Field(sa_column=Column(String(100), nullable=False))
    code: str = Field(sa_column=Column(String(20), unique=True, index=True, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(String(255)))

class Course(CourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CourseCreate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int

class CourseUpdate(SQLModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
