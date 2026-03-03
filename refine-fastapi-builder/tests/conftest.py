import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.database import get_session
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session):
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        role="admin",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="student_user")
def student_user_fixture(session: Session):
    user = User(
        username="student1",
        email="student1@example.com",
        hashed_password=get_password_hash("StudentPass123!"),
        role="student",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(admin_user: User):
    token = create_access_token(
        data={"sub": admin_user.username, "role": admin_user.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="student_headers")
def student_headers_fixture(student_user: User):
    token = create_access_token(
        data={"sub": student_user.username, "role": student_user.role}
    )
    return {"Authorization": f"Bearer {token}"}
