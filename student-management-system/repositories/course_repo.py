from typing import List, Optional
from sqlmodel import Session, select
from models.course_model import Course, CourseCreate, CourseUpdate

def get_by_id(session: Session, course_id: int) -> Optional[Course]:
    return session.get(Course, course_id)

def get_by_code(session: Session, code: str) -> Optional[Course]:
    statement = select(Course).where(Course.code == code)
    return session.exec(statement).first()

def get_all(session: Session):
    statement = select(Course)
    return session.exec(statement).all()

def create(session: Session, course: Course):
    session.add(course)
    session.commit()
    session.refresh(course)
    return course

def update(session: Session, course: Course, course_update: CourseUpdate):
    for key, value in course_update.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    session.commit()
    session.refresh(course)
    return course

def delete(session: Session, course: Course) -> None:
    session.delete(course)
    session.commit()
