from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentPublic, EnrollmentUpdate
from app.services.enrollment_service import EnrollmentService
from app.services.student_service import StudentService
from app.utils.rate_limit import limiter, READ_RATE, WRITE_RATE

router = APIRouter()


@router.post(
    "/",
    response_model=EnrollmentPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll in a course",
)
@limiter.limit(WRITE_RATE)
def enroll(
    request: Request,
    enrollment_in: EnrollmentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    enrollment_service: EnrollmentService = Depends(),
    student_service: StudentService = Depends(),
):
    """Student: can only self-enroll. Admin: can enroll anyone."""
    if current_user.role != "admin":
        student = student_service.get_student_by_user_id(current_user.id)
        if not student or student.id != enrollment_in.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only enroll themselves",
            )
    return enrollment_service.enroll_student(enrollment_in)


@router.get(
    "/",
    response_model=list[EnrollmentPublic],
    summary="List enrollments",
)
@limiter.limit(READ_RATE)
def list_enrollments(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    enrollment_service: EnrollmentService = Depends(),
    student_service: StudentService = Depends(),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """Admin: all enrollments. Student: own enrollments only."""
    if current_user.role == "admin":
        return enrollment_service.list_enrollments(offset=offset, limit=limit)
    student = student_service.get_student_by_user_id(current_user.id)
    if not student:
        return []
    return enrollment_service.list_by_student(
        student.id, offset=offset, limit=limit
    )


@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Drop an enrollment",
)
@limiter.limit(WRITE_RATE)
def drop_enrollment(
    request: Request,
    enrollment_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    enrollment_service: EnrollmentService = Depends(),
    student_service: StudentService = Depends(),
):
    """Student: can only drop own enrollment. Admin: can drop any."""
    enrollment = enrollment_service.get_enrollment(enrollment_id)
    if current_user.role != "admin":
        student = student_service.get_student_by_user_id(current_user.id)
        if not student or student.id != enrollment.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only drop their own enrollments",
            )
    enrollment_service.drop_enrollment(enrollment_id)


@router.patch(
    "/{enrollment_id}",
    response_model=EnrollmentPublic,
    summary="Update enrollment (grade/status)",
)
@limiter.limit(WRITE_RATE)
def update_enrollment(
    request: Request,
    enrollment_id: int,
    enrollment_in: EnrollmentUpdate,
    _admin: Annotated[User, Depends(require_admin)],
    enrollment_service: EnrollmentService = Depends(),
):
    """Admin only: update grade or status."""
    return enrollment_service.update_enrollment(enrollment_id, enrollment_in)
