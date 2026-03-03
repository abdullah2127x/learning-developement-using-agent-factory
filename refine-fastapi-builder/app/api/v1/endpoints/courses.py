from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.schemas.course import CourseCreate, CoursePublic, CourseUpdate
from app.services.course_service import CourseService
from app.utils.rate_limit import limiter, READ_RATE, WRITE_RATE

router = APIRouter()


@router.get(
    "/",
    response_model=list[CoursePublic],
    summary="List all courses",
)
@limiter.limit(READ_RATE)
def list_courses(
    request: Request,
    _user: Annotated[User, Depends(get_current_active_user)],
    course_service: CourseService = Depends(),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """Any authenticated user can view courses."""
    return course_service.list_courses(offset=offset, limit=limit)


@router.get(
    "/{course_id}",
    response_model=CoursePublic,
    summary="Get course by ID",
)
@limiter.limit(READ_RATE)
def get_course(
    request: Request,
    course_id: int,
    _user: Annotated[User, Depends(get_current_active_user)],
    course_service: CourseService = Depends(),
):
    """Any authenticated user can view a course."""
    return course_service.get_course(course_id)


@router.post(
    "/",
    response_model=CoursePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course",
)
@limiter.limit(WRITE_RATE)
def create_course(
    request: Request,
    course_in: CourseCreate,
    _admin: Annotated[User, Depends(require_admin)],
    course_service: CourseService = Depends(),
):
    """Admin only."""
    return course_service.create_course(course_in)


@router.put(
    "/{course_id}",
    response_model=CoursePublic,
    summary="Update a course",
)
@limiter.limit(WRITE_RATE)
def update_course(
    request: Request,
    course_id: int,
    course_in: CourseUpdate,
    _admin: Annotated[User, Depends(require_admin)],
    course_service: CourseService = Depends(),
):
    """Admin only."""
    return course_service.update_course(course_id, course_in)


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course",
)
@limiter.limit(WRITE_RATE)
def delete_course(
    request: Request,
    course_id: int,
    _admin: Annotated[User, Depends(require_admin)],
    course_service: CourseService = Depends(),
):
    """Admin only."""
    course_service.delete_course(course_id)
