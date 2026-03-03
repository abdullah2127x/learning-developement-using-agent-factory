from typing import List, Optional
from fastapi import HTTPException,status
from sqlmodel import Session
from models.course_model import Course, CourseCreate, CourseUpdate
from repositories import course_repo

def create_course(course_create: CourseCreate, session: Session):
    existing_course = course_repo.get_by_code(session, course_create.code)
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course with code already exists",
        )
    db_course = Course(**course_create.model_dump())
    course = course_repo.create(session, db_course)
    return course

def get_course(session: Session, id: int):
    course = course_repo.get_by_id(session, id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course

def list_courses(session: Session):
    courses = course_repo.get_all(session)
    return courses

def update_course(session: Session, id: int, update_course_data: CourseUpdate) -> Course:
    course = course_repo.get_by_id(session, id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    course = course_repo.update(session, course, update_course_data)
    return course

def delete_course(session: Session, id: int) -> None:
    course = course_repo.get_by_id(session, id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    course_repo.delete(session, course)
