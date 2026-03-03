from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.schemas.student import StudentCreate, StudentPublic, StudentUpdate
from app.services.student_service import StudentService

router = APIRouter()


@router.get(
    "/",
    response_model=list[StudentPublic],
    summary="List students",
)
def list_students(
    current_user: Annotated[User, Depends(get_current_active_user)],
    student_service: StudentService = Depends(),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """Admin: all students. Student: own profile only."""
    if current_user.role == "admin":
        return student_service.list_students(offset=offset, limit=limit)
    # Student role: return own profile as list
    student = student_service.get_student_by_user_id(current_user.id)
    return [student] if student else []


@router.get(
    "/{student_id}",
    response_model=StudentPublic,
    summary="Get student by ID",
)
def get_student(
    student_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    student_service: StudentService = Depends(),
):
    """Admin: any student. Student: only own profile."""
    student = student_service.get_student(student_id)
    if current_user.role != "admin" and student.user_id != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Not enough privileges")
    return student


@router.post(
    "/",
    response_model=StudentPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a student profile",
)
def create_student(
    student_in: StudentCreate,
    _admin: Annotated[User, Depends(require_admin)],
    student_service: StudentService = Depends(),
):
    """Admin only."""
    return student_service.create_student(student_in)


@router.put(
    "/{student_id}",
    response_model=StudentPublic,
    summary="Update a student profile",
)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    _admin: Annotated[User, Depends(require_admin)],
    student_service: StudentService = Depends(),
):
    """Admin only."""
    return student_service.update_student(student_id, student_in)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student profile",
)
def delete_student(
    student_id: int,
    _admin: Annotated[User, Depends(require_admin)],
    student_service: StudentService = Depends(),
):
    """Admin only."""
    student_service.delete_student(student_id)
