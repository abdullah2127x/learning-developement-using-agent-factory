from fastapi import APIRouter, Depends
from sqlmodel import Session

from db.engine import get_session
from models.auth_model import Login
from models.student_model import Student, StudentRead
from services import auth_service


router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/")
def login(login_data:Login, session:Session=Depends(get_session)):
    student = auth_service.login_user(login_data, session)
    return student
