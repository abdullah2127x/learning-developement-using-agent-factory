from fastapi import Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.user import User


class UserRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def list_all(self, offset: int = 0, limit: int = 100) -> list[User]:
        statement = select(User).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())
