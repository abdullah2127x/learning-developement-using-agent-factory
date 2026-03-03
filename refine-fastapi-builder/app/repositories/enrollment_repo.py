from fastapi import Depends
from sqlmodel import Session, select, func

from app.core.database import get_session
from app.models.enrollment import Enrollment


class EnrollmentRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_by_id(self, enrollment_id: int) -> Enrollment | None:
        return self.session.get(Enrollment, enrollment_id)

    def get_by_student_and_course(
        self, student_id: int, course_id: int
    ) -> Enrollment | None:
        statement = select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
        )
        return self.session.exec(statement).first()

    def count_by_course(self, course_id: int) -> int:
        statement = select(func.count(Enrollment.id)).where(
            Enrollment.course_id == course_id,
            Enrollment.status == "enrolled",
        )
        return self.session.exec(statement).one()

    def create(self, enrollment: Enrollment) -> Enrollment:
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment

    def update(self, enrollment: Enrollment) -> Enrollment:
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment

    def delete(self, enrollment: Enrollment) -> None:
        self.session.delete(enrollment)
        self.session.commit()

    def list_all(self, offset: int = 0, limit: int = 100) -> list[Enrollment]:
        statement = select(Enrollment).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def list_by_student(
        self, student_id: int, offset: int = 0, limit: int = 100
    ) -> list[Enrollment]:
        statement = (
            select(Enrollment)
            .where(Enrollment.student_id == student_id)
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())
