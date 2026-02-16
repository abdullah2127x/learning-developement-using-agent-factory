from sqlmodel import Session
from models.student import Student, StudentCreate, StudentUpdate
from repositories import student_repo


def create_student(session: Session, data: StudentCreate) -> Student:
    if student_repo.get_by_email(session, data.email):
        raise ValueError("Email already exists")
    return student_repo.create(session, data)


def get_student(session: Session, student_id: int) -> Student:
    student = student_repo.get_by_id(session, student_id)
    if not student:
        raise LookupError("Student not found")
    return student


def list_students(session: Session, skip: int, limit: int) -> list[Student]:
    return student_repo.get_all(session, skip, limit)


def get_students_by_grade(session: Session, grade: str) -> list[Student]:
    return student_repo.get_by_grade(session, grade)


def update_student(session: Session, student_id: int, data: StudentUpdate) -> Student:
    student = student_repo.get_by_id(session, student_id)
    if not student:
        raise LookupError("Student not found")
    return student_repo.update(session, student, data)


def delete_student(session: Session, student_id: int) -> None:
    student = student_repo.get_by_id(session, student_id)
    if not student:
        raise LookupError("Student not found")
    student_repo.delete(session, student)
