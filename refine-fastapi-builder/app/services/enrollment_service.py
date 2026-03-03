from fastapi import Depends, HTTPException, status

from app.models.enrollment import Enrollment
from app.repositories.course_repo import CourseRepository
from app.repositories.enrollment_repo import EnrollmentRepository
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate


class EnrollmentService:
    def __init__(
        self,
        repo: EnrollmentRepository = Depends(),
        course_repo: CourseRepository = Depends(),
    ):
        self.repo = repo
        self.course_repo = course_repo

    def enroll_student(self, enrollment_in: EnrollmentCreate) -> Enrollment:
        # Check duplicate enrollment
        existing = self.repo.get_by_student_and_course(
            enrollment_in.student_id, enrollment_in.course_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student is already enrolled in this course",
            )

        # Check course capacity
        course = self.course_repo.get_by_id(enrollment_in.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id {enrollment_in.course_id} not found",
            )
        current_count = self.repo.count_by_course(enrollment_in.course_id)
        if current_count >= course.max_students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course has reached maximum enrollment capacity",
            )

        db_enrollment = Enrollment.model_validate(enrollment_in)
        return self.repo.create(db_enrollment)

    def get_enrollment(self, enrollment_id: int) -> Enrollment:
        enrollment = self.repo.get_by_id(enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment with id {enrollment_id} not found",
            )
        return enrollment

    def list_enrollments(self, offset: int = 0, limit: int = 100) -> list[Enrollment]:
        return self.repo.list_all(offset=offset, limit=limit)

    def list_by_student(
        self, student_id: int, offset: int = 0, limit: int = 100
    ) -> list[Enrollment]:
        return self.repo.list_by_student(student_id, offset=offset, limit=limit)

    def update_enrollment(
        self, enrollment_id: int, enrollment_in: EnrollmentUpdate
    ) -> Enrollment:
        enrollment = self.get_enrollment(enrollment_id)
        update_data = enrollment_in.model_dump(exclude_unset=True)
        enrollment.sqlmodel_update(update_data)
        return self.repo.update(enrollment)

    def drop_enrollment(self, enrollment_id: int) -> None:
        enrollment = self.get_enrollment(enrollment_id)
        self.repo.delete(enrollment)
