from typing import Literal, Optional

from fastapi import HTTPException, status
from sqlmodel import Session

from models.student_model import Student, StudentCreate, StudentUpdate
from repositories import student_repo
from utils.hash_lib import hash_password


def create_student(student_create: StudentCreate, session: Session):
    existing_student = student_repo.get_by_email(session, student_create.email)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student with email already exists",
        )
    student_create.password = hash_password(student_create.password)
    db_student = Student(**student_create.model_dump())
    student = student_repo.create(session, db_student)
    return student


def get_student(session: Session, id: int):
    student = student_repo.get_by_id(session, id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    return student


def list_students(session: Session):
    students = student_repo.get_all(session)
    return students


def get_students_by_email(session: Session, email: str):
    students = student_repo.get_by_email(session, email)
    if not students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No students found"
        )
    return students


def update_student(session: Session, id: int, update_student: StudentUpdate) -> Student:
    student = student_repo.get_by_id(session, id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    student = student_repo.update(session, student, update_student)
    return student


def delete_student(session: Session, id: int) -> None:
    student = student_repo.get_by_id(session, id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    student_repo.delete(session, student)
