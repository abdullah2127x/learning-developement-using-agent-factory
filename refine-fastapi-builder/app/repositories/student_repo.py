from fastapi import Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.student import Student


class StudentRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_by_id(self, student_id: int) -> Student | None:
        return self.session.get(Student, student_id)

    def get_by_user_id(self, user_id: int) -> Student | None:
        statement = select(Student).where(Student.user_id == user_id)
        return self.session.exec(statement).first()

    def create(self, student: Student) -> Student:
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)
        return student

    def update(self, student: Student) -> Student:
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)
        return student

    def delete(self, student: Student) -> None:
        self.session.delete(student)
        self.session.commit()

    def list_all(self, offset: int = 0, limit: int = 100) -> list[Student]:
        statement = select(Student).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())
