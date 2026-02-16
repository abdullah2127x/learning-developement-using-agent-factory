from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from db.engine import get_session
from models.student import Student, StudentCreate, StudentUpdate
from services import student_service

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=Student, status_code=201)
def create_student(student: StudentCreate, session: Session = Depends(get_session)):
    try:
        return student_service.create_student(session, student)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[Student])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    return student_service.list_students(session, skip, limit)


@router.get("/grade/{grade}", response_model=list[Student])
def get_students_by_grade(grade: str, session: Session = Depends(get_session)):
    return student_service.get_students_by_grade(session, grade)


@router.get("/{student_id}", response_model=Student)
def get_student(student_id: int, session: Session = Depends(get_session)):
    try:
        return student_service.get_student(session, student_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{student_id}", response_model=Student)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    session: Session = Depends(get_session),
):
    try:
        return student_service.update_student(session, student_id, student_update)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, session: Session = Depends(get_session)):
    try:
        student_service.delete_student(session, student_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
