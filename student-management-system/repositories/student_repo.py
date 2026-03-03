from typing import Literal, Optional

from pydantic import EmailStr
from sqlmodel import Session, select

from models import student_model
from models.student_model import Student, StudentCreate, StudentUpdate


def get_by_id(session: Session, student_id: int) -> Student | None:
    student = session.get(Student, student_id)
    return student


def get_by_email(session: Session, email: EmailStr):
    statement = select(Student).where(Student.email == email)
    student = session.exec(statement).first()
    return student

# Get all the students with a specific age
def get_by_age(session: Session, age: int, sort: Literal["ge", "le", "eq"] = "eq"):
    if sort == "ge":
        statement = select(Student).where(Student.age >= age)
    elif sort == "le":
        statement = select(Student).where(Student.age <= age)
    elif sort == "eq":
        statement = select(Student).where(Student.age == age)
    student = session.exec(statement).all()
    return student


def get_all(session: Session):
    statement = select(Student)
    students = session.exec(statement).all()
    return students


def create(session: Session, student: StudentCreate):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student




def update(session: Session, student: Student, student_update: StudentUpdate):
    for key, value in student_update.model_dump(exclude_unset=True).items():
        print(key, value)
        setattr(student, key, value)
    print("After update", student)
    session.commit()
    session.refresh(student)
    return student

def delete(session: Session, student:Student)->None:    
    session.delete(student)
    session.commit()
    