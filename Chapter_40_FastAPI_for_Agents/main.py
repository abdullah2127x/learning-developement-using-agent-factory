from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

# Settings
class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost/students")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()

# Models
class StudentBase(SQLModel):
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    grade: int = Field(ge=0, le=12)

class Student(StudentBase, table=True):
    __tablename__ = "students"
    id: int | None = Field(default=None, primary_key=True)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    grade: int | None = Field(None, ge=0, le=12)

class StudentPublic(StudentBase):
    id: int

# Database setup
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown

app = FastAPI(
    title="Student Management API",
    description="CRUD API for managing student records",
    version="0.1.0",
    lifespan=lifespan,
)

# Routes
@app.post("/students", response_model=StudentPublic, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate, session: SessionDep) -> Student:
    """Create a new student record."""
    db_student = Student.model_validate(student)
    session.add(db_student)
    try:
        session.commit()
        session.refresh(db_student)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create student. Email may already exist.",
        )
    return db_student

@app.get("/students", response_model=list[StudentPublic])
async def list_students(
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: str | None = Query(None),
    grade: int | None = Query(None, ge=0, le=12),
) -> list[Student]:
    """List all students with optional filtering."""
    statement = select(Student)

    if name:
        statement = statement.where(Student.name.ilike(f"%{name}%"))
    if grade is not None:
        statement = statement.where(Student.grade == grade)

    statement = statement.offset(offset).limit(limit)
    students = session.exec(statement).all()
    return students

@app.get("/students/{student_id}", response_model=StudentPublic)
async def get_student(student_id: int, session: SessionDep) -> Student:
    """Get a specific student by ID."""
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student

@app.put("/students/{student_id}", response_model=StudentPublic)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    session: SessionDep,
) -> Student:
    """Update a student record."""
    db_student = session.get(Student, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    update_data = student_update.model_dump(exclude_unset=True)
    db_student.sqlmodel_update(update_data)
    session.add(db_student)
    try:
        session.commit()
        session.refresh(db_student)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update student. Email may already exist.",
        )
    return db_student

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: int, session: SessionDep) -> None:
    """Delete a student record."""
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    session.delete(student)
    session.commit()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
