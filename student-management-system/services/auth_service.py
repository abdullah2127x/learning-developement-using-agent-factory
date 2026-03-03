from fastapi import HTTPException, status
from sqlmodel import Session

from models.auth_model import Login
from models.student_model import Student, StudentRead
from repositories import student_repo
from utils.hash_lib import verify_password
from utils.jwt_lib import create_access_token


def login_user(login_data: Login, session: Session):
    existing_student: Student = student_repo.get_by_email(session, login_data.email)
    if not existing_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email does not exist",
        )
    authenticated_user = verify_password(login_data.password, existing_student.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        ) 
    student = StudentRead.model_validate(existing_student).model_dump()
    
    token = create_access_token(student)
    print(f"token: {token}") 
    # return existing_student
    return token
