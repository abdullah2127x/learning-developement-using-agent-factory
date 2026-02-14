---
name: fastapi-builder
description: |
  Build FastAPI applications from hello world to production-ready enterprise APIs with PostgreSQL, SQLModel, JWT authentication, and Docker deployment. Covers REST APIs, microservices, full-stack apps, and real-time WebSocket applications. This skill should be used when users want to create FastAPI projects, add endpoints, implement authentication, integrate databases, write tests, or deploy FastAPI applications with Docker. Emphasizes async-first patterns, security best practices, pytest testing, and anti-pattern avoidance.
---

# FastAPI Builder

Build production-ready FastAPI applications from simple prototypes to enterprise-scale APIs.

## What This Skill Does

- Create FastAPI projects at any scale (hello world → enterprise)
- Implement REST APIs with automatic validation and documentation
- Integrate PostgreSQL databases using SQLModel ORM
- Set up JWT authentication and authorization
- Configure Docker deployments with Uvicorn
- Write pytest-based tests for endpoints and dependencies
- Implement WebSocket support for real-time features
- Apply async-first patterns with sync fallback support
- Prevent common anti-patterns and optimize performance

## What This Skill Does NOT Do

- Generate non-FastAPI web frameworks (Flask, Django, etc.)
- Handle frontend/client code generation
- Manage cloud infrastructure (use IaC tools for that)
- Provide database migration tooling beyond basic Alembic setup
- Generate production monitoring/observability stack (Prometheus, Grafana, etc.)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing FastAPI structure, current models, routers, dependencies, database setup |
| **Conversation** | User's specific requirements, endpoints needed, business logic, constraints |
| **Skill References** | FastAPI patterns from `references/` (auth, database, testing, deployment) |
| **User Guidelines** | Project-specific conventions, team standards, deployment environment |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Core Implementation Workflow

### 1. Determine Project Scale

Ask user or infer from context:

| Scale | Indicators | Structure |
|-------|-----------|-----------|
| **Hello World** | Learning, PoC, <10 endpoints | Single file (`main.py`) |
| **Small** | Simple API, 10-20 endpoints, 1-2 models | Single file with organized sections |
| **Medium** | Modular API, 20-50 endpoints, multiple models | Directory structure with routers |
| **Large/Enterprise** | 50+ endpoints, complex business logic, teams | Full package structure with layers |

See `references/project-structure.md` for detailed structures.

### 2. Implementation Phases

Execute in order based on project scale:

```
Phase 1: Project Setup
  → Create directory structure
  → Initialize pyproject.toml/requirements.txt
  → Set up main FastAPI app

Phase 2: Core Features
  → Define Pydantic/SQLModel models
  → Implement path operations (endpoints)
  → Add request/response validation

Phase 3: Database Integration (if needed)
  → Configure PostgreSQL connection
  → Create SQLModel table models
  → Implement session dependency
  → Add CRUD operations

Phase 4: Authentication (if needed)
  → Set up JWT token generation
  → Implement OAuth2PasswordBearer
  → Create authentication dependencies
  → Add protected endpoints

Phase 5: Testing
  → Set up pytest with TestClient
  → Write endpoint tests
  → Test authentication flows
  → Test database operations

Phase 6: Production Readiness
  → Add CORS middleware
  → Implement error handlers
  → Configure logging
  → Create Dockerfile
  → Add health check endpoint

Phase 7: Documentation & Deployment
  → Document environment variables
  → Create docker-compose.yml
  → Add README with setup instructions
```

### 3. Decision Trees

#### When to Use Async vs Sync?

```
Is the operation I/O-bound? (DB, API, file)
  ├─ YES → Use async def + await
  └─ NO → Is it CPU-intensive computation?
      ├─ YES → Use def (runs in threadpool)
      └─ NO → Use async def (default)
```

#### How to Structure Dependencies?

```
What is the dependency for?
  ├─ Authentication/Authorization → Use Security() with scopes
  ├─ Database session → Use Depends() with yield pattern
  ├─ Common parameters → Use Depends() with callable
  └─ Application state → Use app.state or lifespan
```

#### When to Use APIRouter?

```
How many endpoints in this module?
  ├─ <5 endpoints, single file → Direct @app decorators
  └─ ≥5 endpoints OR modular organization → APIRouter
      → Create separate router files by resource
      → Include routers in main app with prefixes/tags
```

See `references/patterns.md` for comprehensive decision guides.

---

## FastAPI Fundamentals

### Path Operations (Endpoints)

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.get("/items/{item_id}")
async def read_item(item_id: int) -> Item:
    # Path parameter validation automatic
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item) -> Item:
    # Request body validation automatic
    # Response validation automatic
    return item
```

**Key Points**:
- Use type hints for automatic validation
- Use `async def` for I/O operations
- Return Pydantic models for automatic serialization
- Use HTTPException for error responses

### Dependency Injection

```python
from typing import Annotated
from fastapi import Depends, Header, HTTPException

async def get_token_header(x_token: Annotated[str, Header()]) -> str:
    if x_token != "fake-secret-token":
        raise HTTPException(status_code=400, detail="Invalid token")
    return x_token

@app.get("/items/", dependencies=[Depends(get_token_header)])
async def read_items():
    return [{"item": "Foo"}]
```

**Key Points**:
- Use `Depends()` for reusable logic
- Use `Annotated[Type, Depends(callable)]` pattern
- Dependencies can be chained
- Use `yield` for cleanup (e.g., database sessions)

See `references/dependency-injection.md` for advanced patterns.

---

## Database Integration (PostgreSQL + SQLModel)

### Model Definition

```python
from sqlmodel import Field, SQLModel
from datetime import datetime

# Table model (database)
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# API models (separate concerns)
class HeroCreate(SQLModel):
    name: str
    secret_name: str
    age: int | None = None

class HeroPublic(SQLModel):
    id: int
    name: str
    age: int | None
    # Note: secret_name excluded for security
```

### Session Dependency

```python
from typing import Annotated
from sqlmodel import Session, create_engine
from fastapi import Depends

DATABASE_URL = "postgresql+psycopg://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

### CRUD Operations

```python
from sqlmodel import select

@app.post("/heroes", response_model=HeroPublic)
async def create_hero(hero: HeroCreate, session: SessionDep) -> Hero:
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/heroes", response_model=list[HeroPublic])
async def list_heroes(session: SessionDep, offset: int = 0, limit: int = 100):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
```

See `references/database.md` for connection pooling, migrations, and advanced patterns.

---

## Authentication (JWT)

### Setup

```python
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

### Token Operations

```python
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Fetch user from database
    return user
```

See `references/authentication.md` for complete implementation, scopes, and refresh tokens.

---

## Testing with Pytest

### Basic Setup

```python
from fastapi.testclient import TestClient
from myapp.main import app

client = TestClient(app)

def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "name": "Foo"}

def test_create_item():
    response = client.post("/items", json={"name": "Bar", "price": 10.5})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bar"
```

### Testing with Database

```python
import pytest
from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool

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
```

See `references/testing.md` for authentication testing, fixtures, and coverage.

---

## Production Best Practices

### Security Checklist

- [ ] Use environment variables for secrets (never hardcode)
- [ ] Enable HTTPS redirect middleware
- [ ] Configure CORS with explicit origins (not `["*"]`)
- [ ] Hash passwords with bcrypt/argon2
- [ ] Validate and sanitize all inputs
- [ ] Use response_model to prevent data leaks
- [ ] Implement rate limiting for auth endpoints
- [ ] Add request size limits
- [ ] Use Security headers (Helmet equivalent)

### Performance Optimization

- [ ] Use async def for I/O-bound operations
- [ ] Configure database connection pooling
- [ ] Add response caching where appropriate
- [ ] Use pagination for list endpoints (offset/limit)
- [ ] Implement background tasks for slow operations
- [ ] Use response_model_exclude_unset=True to reduce payload
- [ ] Configure Uvicorn workers based on CPU cores

### Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )
```

See `references/anti-patterns.md` for common mistakes to avoid.
See `references/performance.md` for optimization strategies.

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["fastapi", "run", "main.py", "--port", "80", "--workers", "4"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:80"
    environment:
      - DATABASE_URL=postgresql+psycopg://user:pass@db/dbname
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

See `references/deployment.md` for production configurations, health checks, and multi-stage builds.

---

## Implementation Checklist

Before marking implementation complete:

### Functionality
- [ ] All endpoints return correct status codes
- [ ] Request validation working (try invalid inputs)
- [ ] Response models excluding sensitive data
- [ ] Database operations commit/rollback correctly
- [ ] Authentication protecting required endpoints

### Code Quality
- [ ] Type hints on all functions
- [ ] Pydantic/SQLModel models for validation
- [ ] Error handling for edge cases
- [ ] No hardcoded secrets or credentials
- [ ] Async/sync used appropriately

### Testing
- [ ] Tests for happy paths
- [ ] Tests for error cases (401, 404, 422)
- [ ] Authentication flow tested
- [ ] Database operations tested
- [ ] Coverage >80% for critical paths

### Production Readiness
- [ ] Environment variables documented
- [ ] CORS configured
- [ ] Error handlers registered
- [ ] Health check endpoint added
- [ ] Dockerfile builds successfully
- [ ] README with setup instructions

### Documentation
- [ ] OpenAPI docs accessible at /docs
- [ ] Endpoint descriptions clear
- [ ] Response models documented
- [ ] Environment variables listed in README

---

## Quick Reference

| Need | See |
|------|-----|
| Project structures | `references/project-structure.md` |
| JWT authentication patterns | `references/authentication.md` |
| PostgreSQL + SQLModel setup | `references/database.md` |
| Pytest testing examples | `references/testing.md` |
| Docker deployment | `references/deployment.md` |
| Common mistakes to avoid | `references/anti-patterns.md` |
| Performance optimization | `references/performance.md` |
| Complete examples | `references/examples/` |

---

## Example Usage

**User**: "Create a FastAPI app with user authentication"

**Claude**:
1. Determines scale (asks if small/medium/large)
2. Gathers requirements (endpoints, user fields, etc.)
3. Creates project structure
4. Implements User model with SQLModel
5. Sets up JWT authentication
6. Creates registration and login endpoints
7. Adds protected endpoints
8. Writes tests
9. Creates Dockerfile and docker-compose.yml
10. Provides setup instructions
