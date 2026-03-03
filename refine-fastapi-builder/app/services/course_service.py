from fastapi import Depends, HTTPException, status

from app.models.course import Course
from app.repositories.course_repo import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate


class CourseService:
    def __init__(self, repo: CourseRepository = Depends()):
        self.repo = repo

    def create_course(self, course_in: CourseCreate) -> Course:
        db_course = Course.model_validate(course_in)
        return self.repo.create(db_course)

    def get_course(self, course_id: int) -> Course:
        course = self.repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id {course_id} not found",
            )
        return course

    def list_courses(self, offset: int = 0, limit: int = 100) -> list[Course]:
        return self.repo.list_all(offset=offset, limit=limit)

    def update_course(self, course_id: int, course_in: CourseUpdate) -> Course:
        course = self.get_course(course_id)
        update_data = course_in.model_dump(exclude_unset=True)
        course.sqlmodel_update(update_data)
        return self.repo.update(course)

    def delete_course(self, course_id: int) -> None:
        course = self.get_course(course_id)
        self.repo.delete(course)
