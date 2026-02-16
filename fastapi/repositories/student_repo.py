from sqlmodel import Session, select
from models.student import Student, StudentCreate, StudentUpdate


def get_by_id(session: Session, student_id: int) -> Student | None:
    return session.get(Student, student_id)


def get_by_email(session: Session, email: str) -> Student | None:
    statement = select(Student).where(Student.email == email)
    return session.exec(statement).first()


def get_all(session: Session, skip: int, limit: int) -> list[Student]:
    statement = select(Student).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_by_grade(session: Session, grade: str) -> list[Student]:
    statement = select(Student).where(Student.grade == grade)
    return session.exec(statement).all()


def create(session: Session, data: StudentCreate) -> Student:
    student = Student.model_validate(data)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def update(session: Session, student: Student, data: StudentUpdate) -> Student:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def delete(session: Session, student: Student) -> None:
    session.delete(student)
    session.commit()
