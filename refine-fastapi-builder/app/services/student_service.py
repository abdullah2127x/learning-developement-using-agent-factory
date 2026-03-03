import structlog
from fastapi import Depends, HTTPException, status

from app.models.student import Student
from app.repositories.student_repo import StudentRepository
from app.schemas.student import StudentCreate, StudentUpdate

logger = structlog.get_logger(__name__)


class StudentService:
    def __init__(self, repo: StudentRepository = Depends()):
        self.repo = repo

    def create_student(self, student_in: StudentCreate) -> Student:
        logger.info("creating_student", user_id=student_in.user_id)
        if self.repo.get_by_user_id(student_in.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student profile already exists for this user",
            )
        db_student = Student.model_validate(student_in)
        student = self.repo.create(db_student)
        logger.info("student_created", student_id=student.id)
        return student

    def get_student(self, student_id: int) -> Student:
        student = self.repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with id {student_id} not found",
            )
        return student

    def get_student_by_user_id(self, user_id: int) -> Student | None:
        return self.repo.get_by_user_id(user_id)

    def list_students(self, offset: int = 0, limit: int = 100) -> list[Student]:
        return self.repo.list_all(offset=offset, limit=limit)

    def update_student(self, student_id: int, student_in: StudentUpdate) -> Student:
        student = self.get_student(student_id)
        update_data = student_in.model_dump(exclude_unset=True)
        student.sqlmodel_update(update_data)
        updated = self.repo.update(student)
        logger.info("student_updated", student_id=student_id)
        return updated

    def delete_student(self, student_id: int) -> None:
        student = self.get_student(student_id)
        self.repo.delete(student)
        logger.info("student_deleted", student_id=student_id)
