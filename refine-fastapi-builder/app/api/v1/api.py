from fastapi import APIRouter

from app.api.v1.endpoints import auth, courses, enrollments, students

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(
    enrollments.router, prefix="/enrollments", tags=["Enrollments"]
)
