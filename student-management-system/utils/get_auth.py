from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from db.engine import get_session
from services import student_service
from utils.jwt_lib import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


def get_authorization(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    authorize_student = student_service.get_students_by_email(session, email)
    return authorize_student


def verify_self(student_id: int=0, authorized_student=Depends(get_authorization)):
    if authorized_student.role == "admin":
        return authorized_student
    if student_id != authorized_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access you own data",
        )
    return authorized_student
