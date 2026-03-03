from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from db.engine import get_session
from models.student_model import Student, StudentCreate, StudentUpdate
from services import student_service
from utils.get_auth import get_authorization, verify_self

router = APIRouter(
    prefix="/students", tags=["Students"], dependencies=[Depends(get_authorization)]
)

public_router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=list[Student])
async def get_all(session: Session = Depends(get_session), self=Depends(verify_self)):
    print("in the get all route the self is ", self)
    
    if self.role == "admin":
        return student_service.list_students(session=session)
    return [self]


@router.get("/{student_id}")
async def get_students(
    student_id: int, session: Session = Depends(get_session), self=Depends(verify_self)
):
    return student_service.get_student(session=session, id=student_id)


@public_router.post(
    "/",
    response_model=Student,
)
async def create_student(
    student: StudentCreate,
    session: Session = Depends(get_session),
    # self=Depends(verify_self),
):
    student = student_service.create_student(student, session)
    return student


@router.put("/")
async def update_student(
    id: int,
    student_update: StudentUpdate,
    session: Session = Depends(get_session),
    self=Depends(verify_self),
):
    student = student_service.update_student(
        session=session, id=id, update_student=student_update
    )
    return student


@router.delete("/", response_model=Student)
async def delete_student(id: int, session: Session = Depends(get_session)):
    return student_service.delete_student(session=session, id=id)
