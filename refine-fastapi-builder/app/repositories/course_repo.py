from fastapi import Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.course import Course


class CourseRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_by_id(self, course_id: int) -> Course | None:
        return self.session.get(Course, course_id)

    def create(self, course: Course) -> Course:
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course

    def update(self, course: Course) -> Course:
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course

    def delete(self, course: Course) -> None:
        self.session.delete(course)
        self.session.commit()

    def list_all(self, offset: int = 0, limit: int = 100) -> list[Course]:
        statement = select(Course).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())
