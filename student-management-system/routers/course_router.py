from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from db.engine import get_session
from models.course_model import CourseCreate, CourseRead, CourseUpdate
from services import course_service
from utils.get_auth import get_authorization

router = APIRouter(
    prefix="/courses", tags=["Courses"], dependencies=[Depends(get_authorization)]
)


@router.post("/", response_model=CourseRead)
def create_course(
    course_create: CourseCreate,
    session: Session = Depends(get_session),
):
    return course_service.create_course(course_create, session)


@router.get("/", response_model=List[CourseRead])
def list_courses(
    session: Session = Depends(get_session),
):
    return course_service.list_courses(session)


@router.get("/{id}", response_model=CourseRead)
def get_course(id: int, session: Session = Depends(get_session)):
    return course_service.get_course(session, id)


@router.patch("/{id}", response_model=CourseRead)
def update_course(
    id: int, update_course: CourseUpdate, session: Session = Depends(get_session)
):
    return course_service.update_course(session, id, update_course)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(id: int, session: Session = Depends(get_session)):
    course_service.delete_course(session, id)
