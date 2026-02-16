import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from main import Student, StudentCreate, app, get_session

@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
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
    """Create a test client with the test database."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_student(client: TestClient):
    """Test creating a new student."""
    student_data = {"name": "John Doe", "email": "john@example.com", "grade": 10}
    response = client.post("/students", json=student_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["grade"] == 10
    assert data["id"] is not None

def test_create_student_duplicate_email(client: TestClient):
    """Test creating a student with duplicate email fails."""
    student_data = {"name": "John Doe", "email": "john@example.com", "grade": 10}
    response1 = client.post("/students", json=student_data)
    assert response1.status_code == 201

    response2 = client.post("/students", json=student_data)
    assert response2.status_code == 400

def test_create_student_invalid_grade(client: TestClient):
    """Test creating a student with invalid grade fails."""
    student_data = {"name": "John Doe", "email": "john@example.com", "grade": 15}
    response = client.post("/students", json=student_data)
    assert response.status_code == 422

def test_list_students(client: TestClient):
    """Test listing all students."""
    # Create some students
    for i in range(3):
        student_data = {
            "name": f"Student {i}",
            "email": f"student{i}@example.com",
            "grade": 9 + i,
        }
        client.post("/students", json=student_data)

    response = client.get("/students")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_list_students_with_pagination(client: TestClient):
    """Test listing students with offset and limit."""
    # Create 5 students
    for i in range(5):
        student_data = {
            "name": f"Student {i}",
            "email": f"student{i}@example.com",
            "grade": 10,
        }
        client.post("/students", json=student_data)

    response = client.get("/students?offset=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_list_students_filter_by_name(client: TestClient):
    """Test filtering students by name."""
    # Create students
    client.post("/students", json={"name": "Alice Smith", "email": "alice@example.com", "grade": 10})
    client.post("/students", json={"name": "Bob Jones", "email": "bob@example.com", "grade": 11})
    client.post("/students", json={"name": "Alice Brown", "email": "alice2@example.com", "grade": 9})

    response = client.get("/students?name=alice")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("Alice" in student["name"] for student in data)

def test_list_students_filter_by_grade(client: TestClient):
    """Test filtering students by grade."""
    # Create students
    client.post("/students", json={"name": "Student A", "email": "a@example.com", "grade": 10})
    client.post("/students", json={"name": "Student B", "email": "b@example.com", "grade": 10})
    client.post("/students", json={"name": "Student C", "email": "c@example.com", "grade": 11})

    response = client.get("/students?grade=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(student["grade"] == 10 for student in data)

def test_get_student(client: TestClient):
    """Test getting a specific student."""
    # Create a student
    create_response = client.post(
        "/students",
        json={"name": "John Doe", "email": "john@example.com", "grade": 10}
    )
    student_id = create_response.json()["id"]

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == student_id
    assert data["name"] == "John Doe"

def test_get_nonexistent_student(client: TestClient):
    """Test getting a nonexistent student returns 404."""
    response = client.get("/students/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_student(client: TestClient):
    """Test updating a student."""
    # Create a student
    create_response = client.post(
        "/students",
        json={"name": "John Doe", "email": "john@example.com", "grade": 10}
    )
    student_id = create_response.json()["id"]

    # Update the student
    update_response = client.put(
        f"/students/{student_id}",
        json={"name": "Jane Doe", "grade": 11}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Jane Doe"
    assert data["grade"] == 11
    assert data["email"] == "john@example.com"  # Unchanged

def test_update_nonexistent_student(client: TestClient):
    """Test updating a nonexistent student returns 404."""
    response = client.put(
        "/students/999",
        json={"name": "Jane Doe"}
    )
    assert response.status_code == 404

def test_delete_student(client: TestClient):
    """Test deleting a student."""
    # Create a student
    create_response = client.post(
        "/students",
        json={"name": "John Doe", "email": "john@example.com", "grade": 10}
    )
    student_id = create_response.json()["id"]

    # Delete the student
    delete_response = client.delete(f"/students/{student_id}")
    assert delete_response.status_code == 204

    # Verify student is deleted
    get_response = client.get(f"/students/{student_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_student(client: TestClient):
    """Test deleting a nonexistent student returns 404."""
    response = client.delete("/students/999")
    assert response.status_code == 404
