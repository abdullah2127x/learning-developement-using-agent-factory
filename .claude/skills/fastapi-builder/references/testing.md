# FastAPI Testing with Pytest

Comprehensive testing guide using TestClient, fixtures, database testing, and coverage strategies.

## Installation

```bash
pip install pytest pytest-cov httpx
```

## Basic Testing with TestClient

### Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session

# Use in-memory SQLite for tests
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
```

### Basic Endpoint Tests

```python
# tests/test_api.py
def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item(client: TestClient):
    response = client.post(
        "/items",
        json={"name": "Test Item", "price": 10.5}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 10.5
    assert "id" in data

def test_create_item_invalid(client: TestClient):
    response = client.post(
        "/items",
        json={"name": "Test"}  # Missing required 'price'
    )
    assert response.status_code == 422  # Validation error
```

---

## Testing with Database

### Database Fixtures

```python
# tests/conftest.py
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("SecurePass123!")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="test_users")
def test_users_fixture(session: Session):
    users = [
        User(username=f"user{i}", email=f"user{i}@example.com", hashed_password="hashed")
        for i in range(5)
    ]
    session.add_all(users)
    session.commit()
    return users
```

### CRUD Tests

```python
# tests/test_users.py
def test_create_user(client: TestClient):
    response = client.post(
        "/users",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "hashed_password" not in data  # Security check

def test_get_user(client: TestClient, test_user: User):
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username

def test_get_user_not_found(client: TestClient):
    response = client.get("/users/9999")
    assert response.status_code == 404

def test_list_users(client: TestClient, test_users):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

def test_update_user(client: TestClient, test_user: User):
    response = client.put(
        f"/users/{test_user.id}",
        json={"email": "updated@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"

def test_delete_user(client: TestClient, test_user: User):
    response = client.delete(f"/users/{test_user.id}")
    assert response.status_code == 200

    # Verify deleted
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 404
```

---

## Testing Authentication

### Auth Fixtures

```python
# tests/conftest.py
from app.core.security import create_access_token

@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    return create_access_token(data={"sub": test_user.username})

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    return {"Authorization": f"Bearer {auth_token}"}
```

### Auth Tests

```python
# tests/test_auth.py
def test_register(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"

def test_register_duplicate_username(client: TestClient, test_user: User):
    response = client.post(
        "/auth/register",
        json={
            "username": test_user.username,
            "email": "other@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 400

def test_login_success(client: TestClient, test_user: User):
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user: User):
    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401

def test_access_protected_endpoint(client: TestClient, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_access_protected_without_token(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_access_protected_invalid_token(client: TestClient):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
```

---

## Testing Lifespan Events

```python
# tests/test_lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient

items = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    items["foo"] = {"name": "Fighters"}
    items["bar"] = {"name": "Tenders"}
    yield
    # Shutdown
    items.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/items/{item_id}")
async def read_items(item_id: str):
    return items[item_id]

def test_lifespan_events():
    # Before context, items empty
    assert items == {}

    with TestClient(app) as client:
        # Inside context, lifespan started
        assert items == {"foo": {"name": "Fighters"}, "bar": {"name": "Tenders"}}

        response = client.get("/items/foo")
        assert response.status_code == 200
        assert response.json() == {"name": "Fighters"}

    # After context, lifespan ended
    assert items == {}
```

---

## Testing Dependencies

### Override Dependencies

```python
# tests/test_dependencies.py
from app.dependencies import get_current_user

def test_with_dependency_override(client: TestClient):
    # Mock dependency
    def override_get_current_user():
        return User(id=1, username="mockuser", email="mock@example.com")

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == "mockuser"

    # Clean up
    app.dependency_overrides.clear()
```

### Testing Background Tasks

```python
# tests/test_background_tasks.py
from unittest.mock import Mock

def test_endpoint_with_background_task(client: TestClient):
    mock_task = Mock()
    app.dependency_overrides[background_task_dependency] = lambda: mock_task

    response = client.post("/send-notification/test@example.com")
    assert response.status_code == 200

    # Verify background task was called
    mock_task.assert_called_once()

    app.dependency_overrides.clear()
```

---

## Async Testing

### Setup

```bash
pip install pytest-asyncio
```

### Async Tests

```python
# tests/test_async.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

@pytest.mark.asyncio
async def test_async_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/users",
            json={"username": "asyncuser", "email": "async@example.com"}
        )
    assert response.status_code == 201
```

---

## Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("item_data,expected_status", [
    ({"name": "Valid", "price": 10.0}, 201),
    ({"name": "No Price"}, 422),
    ({"price": 10.0}, 422),
    ({"name": "", "price": 10.0}, 422),
])
def test_create_item_parametrized(client: TestClient, item_data, expected_status):
    response = client.post("/items", json=item_data)
    assert response.status_code == expected_status

@pytest.mark.parametrize("username,password,expected_status", [
    ("testuser", "SecurePass123!", 200),
    ("testuser", "WrongPassword", 401),
    ("wronguser", "SecurePass123!", 401),
])
def test_login_parametrized(client: TestClient, test_user, username, password, expected_status):
    response = client.post(
        "/auth/token",
        data={"username": username, "password": password}
    )
    assert response.status_code == expected_status
```

---

## Coverage

### Run Tests with Coverage

```bash
# Run all tests with coverage
pytest --cov=app tests/

# Generate HTML report
pytest --cov=app --cov-report=html tests/

# View coverage for specific file
pytest --cov=app.routers.users tests/

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80 tests/
```

### pytest.ini Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
    -v
```

---

## Testing Best Practices

### 1. Test Structure (AAA Pattern)

```python
def test_create_user(client: TestClient):
    # Arrange
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

    # Act
    response = client.post("/users", json=user_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
```

### 2. Test Isolation

```python
# Each test should be independent
def test_user_creation(client: TestClient, session: Session):
    # Create user
    response = client.post("/users", json={...})

    # Clean up (or use fixture)
    # Session fixture auto-rollback between tests
```

### 3. Test Naming

```python
# Good test names describe what they test
def test_create_user_returns_201_with_valid_data():
    ...

def test_create_user_returns_422_with_invalid_email():
    ...

def test_login_returns_401_with_wrong_password():
    ...
```

### 4. Use Fixtures for Common Setup

```python
@pytest.fixture
def sample_items(session: Session):
    items = [Item(name=f"Item {i}", price=i*10) for i in range(5)]
    session.add_all(items)
    session.commit()
    return items

def test_list_items(client: TestClient, sample_items):
    response = client.get("/items")
    assert len(response.json()) == 5
```

### 5. Test Error Cases

```python
def test_get_user_not_found(client: TestClient):
    response = client.get("/users/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_user_duplicate_email(client: TestClient, test_user):
    response = client.post("/users", json={
        "username": "newuser",
        "email": test_user.email,  # Duplicate
        "password": "pass"
    })
    assert response.status_code == 400
```

---

## Common Test Patterns

### Testing Pagination

```python
def test_pagination(client: TestClient, test_users):
    # Page 1
    response = client.get("/users?offset=0&limit=2")
    assert len(response.json()) == 2

    # Page 2
    response = client.get("/users?offset=2&limit=2")
    assert len(response.json()) == 2

    # Exceeds limit
    response = client.get("/users?offset=0&limit=1000")
    assert response.status_code == 422  # Validation error
```

### Testing File Uploads

```python
def test_upload_file(client: TestClient):
    files = {"file": ("test.txt", b"file content", "text/plain")}
    response = client.post("/upload", files=files)
    assert response.status_code == 200
```

### Testing Relationships

```python
def test_user_with_posts(client: TestClient, test_user, session):
    # Create posts for user
    posts = [Post(title=f"Post {i}", user_id=test_user.id) for i in range(3)]
    session.add_all(posts)
    session.commit()

    # Get user with posts
    response = client.get(f"/users/{test_user.id}/posts")
    assert response.status_code == 200
    assert len(response.json()) == 3
```

---

## Quick Reference

| Test Type | Command |
|-----------|---------|
| All tests | `pytest` |
| Specific file | `pytest tests/test_users.py` |
| Specific test | `pytest tests/test_users.py::test_create_user` |
| With coverage | `pytest --cov=app` |
| Verbose | `pytest -v` |
| Stop on first failure | `pytest -x` |
| Show print statements | `pytest -s` |
| Parallel execution | `pytest -n auto` (requires pytest-xdist) |
