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

## Pre-Implementation Environment Setup

**CRITICAL**: Execute these steps BEFORE writing any code to prevent common errors:

### 1. Dependency Synchronization (If using uv)

If the project uses `uv` package manager:

```bash
uv sync
```

**Why**: Ensures all dependencies (including transitive) are correctly installed and versions match `pyproject.toml` and `uv.lock`.

**Common Error**: `pydantic-core` version mismatch if skipped.

**When to run**:
- After first clone/setup
- After modifying `pyproject.toml`
- Before running tests or starting development
- After any dependency-related error

### 2. Pydantic v2 Configuration (MANDATORY)

**Current requirement**: Use Pydantic v2+ with `ConfigDict` (NOT deprecated class-based config).

**Correct pattern for Settings/BaseModel with environment variables:**

```python
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

# ✅ CORRECT - Pydantic v2
class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    database_url: str
    debug: bool = False

# ❌ WRONG - Pydantic v1 (deprecated)
class Settings(BaseSettings):
    class Config:
        env_file = ".env"
```

**Why `extra="ignore"`**: Allows `.env` files with extra variables that aren't defined in your Settings class. Prevents validation errors when other tools (API_KEY, MAX_CONNECTIONS) are in the same `.env`.

**When you need this**: Every time you load from `.env` or environment variables.

### 3. Platform Compatibility Checks

**Python 3.12+ Required**: Verify before starting:

```bash
python --version
# Should show: Python 3.12.x or higher
```

**Windows-Specific Issue - Unicode in CLI scripts**:

If writing scripts that output to console:
- ❌ DON'T use Unicode characters: `✓`, `✅`, `❌`, `→`
- ✅ DO use ASCII-safe alternatives: `[PASS]`, `[SUCCESS]`, `[ERROR]`, `->`

**Why**: Windows console (cp1252) doesn't support full Unicode by default. Cross-platform scripts must use ASCII.

**Quick test**:
```python
print("[PASS] Health check")  # ✅ Works on Windows
print("✓ Health check")       # ❌ May fail on Windows
```

### 4. Database URL Format (If using PostgreSQL)

**CRITICAL**: Use `psycopg` (v3) driver, NOT `psycopg2`:

```python
# ✅ CORRECT - SQLModel with psycopg (v3)
DATABASE_URL = "postgresql+psycopg://user:password@localhost/dbname"

# ❌ WRONG - Uses old psycopg2
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

If using Neon or cloud PostgreSQL, ensure URL format:
```
postgresql+psycopg://user:password@host:5432/dbname?sslmode=require
```

### 5. ALWAYS Include psycopg[binary] in Dependencies (MANDATORY)

**CRITICAL**: When creating ANY FastAPI project with database support, ALWAYS include `psycopg[binary]` in the project dependencies — even if the initial `.env` uses SQLite. Users frequently switch to PostgreSQL (Neon, Supabase, local Postgres) after project creation.

**Error if missing**: `ModuleNotFoundError: No module named 'psycopg2'` or `No module named 'psycopg'`

**pyproject.toml** — ALWAYS include:
```toml
dependencies = [
    "fastapi[standard]>=0.115.0",
    "sqlmodel>=0.0.22",
    "pydantic-settings>=2.6.0",
    "uvicorn[standard]>=0.32.0",
    "psycopg[binary]>=3.2.0",      # ALWAYS include — PostgreSQL driver
]
```

**requirements.txt** — ALWAYS include:
```
fastapi[standard]>=0.115.0
sqlmodel>=0.0.22
pydantic-settings>=2.6.0
uvicorn[standard]>=0.32.0
psycopg[binary]>=3.2.0            # ALWAYS include — PostgreSQL driver
```

**Why always**: The cost of including it (~5MB) is negligible. The cost of NOT including it (broken app, user frustration, debugging time) is high. Users switch databases frequently, and this prevents the #1 recurring error with this skill.

### Pre-Implementation Checklist

Before writing ANY code:

- [ ] Environment synced (`uv sync` if applicable)
- [ ] Python 3.12+ installed
- [ ] `psycopg[binary]` included in dependencies (MANDATORY — even for SQLite projects)
- [ ] `.env` file created with required variables (DATABASE_URL, DEBUG, etc.)
- [ ] Testing environment set up (pytest installed, TestClient available)
- [ ] Pydantic v2 ConfigDict pattern understood (for Settings/BaseModel)
- [ ] If Windows development: No Unicode in CLI scripts planned
- [ ] If using PostgreSQL: URL uses `postgresql+psycopg://` format (not `postgresql://`)

---

## Common Pitfalls & Prevention

### Pitfall 1: Pydantic Settings Validation Errors

**Error**: `ValidationError: Extra inputs are not permitted [type=extra_forbidden]`

**Cause**: Settings class doesn't define fields that exist in `.env`

**Fix**:
```python
# Add this to your Settings class
model_config = ConfigDict(env_file=".env", extra="ignore")
```

**Better yet**: Only define fields you'll actually use in Settings, delete unused ones from `.env`.

---

### Pitfall 2: Windows Unicode Encoding Errors

**Error**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Cause**: Script uses Unicode characters (✓, ✅, →) on Windows console

**Fix**: Replace all Unicode in console output:

| Don't Use | Use Instead |
|-----------|-------------|
| `✓` | `[PASS]` |
| `✅` | `[SUCCESS]` |
| `❌` | `[ERROR]` |
| `→` | `->` |
| `🔁` | `[NEXT]` |
| `🧠` | `[NOTE]` |

---

### Pitfall 3: Missing `uv sync`

**Error**: Various dependency version conflicts or imports failing

**Cause**: Environment not synchronized with `pyproject.toml`

**Fix**: Always run after setup or dependency changes:
```bash
uv sync
```

**When in doubt**: Run it. It's safe and idempotent.

---

### Pitfall 4: Incorrect Database URL Format / Missing psycopg Driver

**Error**: `ModuleNotFoundError: No module named 'psycopg2'` or `sqlalchemy.exc.ArgumentError: Invalid database URL`

**Cause**: Missing `psycopg[binary]` in dependencies AND/OR using old psycopg2 driver syntax

**Fix (two steps)**:

**Step 1**: ALWAYS include `psycopg[binary]` in project dependencies:
```toml
# pyproject.toml
dependencies = [
    ...
    "psycopg[binary]>=3.2.0",  # ALWAYS include
]
```

**Step 2**: Use `postgresql+psycopg://` not `postgresql://`:
```python
# ✅ Correct — feed from settings, never hardcode the URL
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True
)

# ❌ Wrong — hardcoded URL, ignores .env
engine = create_engine(
    "postgresql://user:pass@localhost/db"
)
```

---

### Pitfall 5: Settings Class with Unused Environment Variables

**Error**: `.env` has variables your code doesn't use, causing validation failures

**Cause**: Settings class validates ALL env vars against defined fields

**Fix**: Use `extra="ignore"` in ConfigDict:

```python
class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # ← This is KEY
    )
    database_url: str
    debug: bool
    # API_KEY and MAX_CONNECTIONS in .env are silently ignored
```

---

### Pitfall 6: Async/Await Mistakes

**Error**: `RuntimeError: no running event loop` or coroutine not awaited

**Common mistake**:
```python
# ❌ WRONG - Forgot await
result = get_session()  # This is a coroutine!

# ✅ CORRECT - Use await
result = await get_session()

# OR for dependencies, use Depends()
SessionDep = Annotated[Session, Depends(get_session)]
```

**Rule**: If function is `async def`, ALWAYS use `await` when calling it (except with `Depends()`).

---

### Pitfall 7: Missing Input Validation on Schemas

**Error**: Invalid data accepted silently — empty strings, wrong email formats, arbitrary role values, negative numbers.

**Cause**: Using plain `str` or `int` types without `Field()` constraints, `EmailStr`, or `Literal` types.

**MANDATORY Rules** — Apply these EVERY time you create schemas:

1. **Email fields** → ALWAYS use `EmailStr` (from `pydantic`), never plain `str`
2. **Enum-like string fields** (role, status, grade, category) → ALWAYS use `Literal["val1", "val2"]`, never plain `str`
3. **String input fields** (name, title, description) → ALWAYS add `Field(min_length=..., max_length=...)`
4. **Numeric input fields** (price, quantity, credit_hours) → ALWAYS add `Field(ge=..., le=...)` or `Field(gt=...)`
5. **Password fields** → ALWAYS add `Field(min_length=8, max_length=128)`

**Bad — No validation:**
```python
# ❌ WRONG - Accepts any garbage input
class UserCreate(SQLModel):
    username: str              # empty string accepted
    email: str                 # "notanemail" accepted
    password: str              # "1" accepted
    role: str = "student"      # "god" accepted

class EnrollmentUpdate(SQLModel):
    grade: str | None = None   # "ZZZZZ" accepted
    status: str | None = None  # "banana" accepted

class CourseCreate(SQLModel):
    title: str                 # empty string accepted
    credit_hours: int = 3      # -999 accepted
    max_students: int = 30     # 0 accepted
```

**Good — Proper validation:**
```python
# ✅ CORRECT - Strict validation at schema level
from typing import Literal
from pydantic import EmailStr
from sqlmodel import Field, SQLModel

Role = Literal["admin", "student"]
EnrollmentStatus = Literal["enrolled", "completed", "dropped"]
Grade = Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]

class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role = "student"

class EnrollmentUpdate(SQLModel):
    grade: Grade | None = None
    status: EnrollmentStatus | None = None

class CourseCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    credit_hours: int = Field(default=3, ge=1, le=12)
    max_students: int = Field(default=30, ge=1, le=500)
```

**Why this matters**: Without these constraints, invalid data silently enters your database. FastAPI only auto-validates types — it does NOT check format, length, or allowed values unless you specify constraints.

**Import rule**: ALWAYS import `Field` from `sqlmodel`, not from `pydantic`. `sqlmodel.Field` is a superset — it supports all Pydantic validation args (`min_length`, `ge`, `gt`, etc.) PLUS DB-specific ones (`primary_key`, `foreign_key`, `index`, `unique`). Only import `EmailStr` from `pydantic`.

---

### Pitfall 8: Missing sa_column on Table Models

**Error**: Unlimited TEXT columns in PostgreSQL — no DB-level length constraints. Data bypassing the API (migrations, admin panels, other services) can insert invalid data.

**Cause**: Using `Field(index=True)` without `sa_column=Column(...)` on string fields in `table=True` models.

**MANDATORY Rule** — For `table=True` models, ALWAYS use `sa_column=Column(...)` on string fields to enforce DB-level constraints:

**Bad — No DB-level constraints:**
```python
# ❌ WRONG - Creates unlimited TEXT columns in PostgreSQL
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)      # TEXT (unlimited)
    email: str = Field(unique=True, index=True)          # TEXT (unlimited)
    hashed_password: str                                  # TEXT (unlimited)
    role: str = Field(default="student")                  # TEXT (unlimited)
```

**Good — Proper DB-level constraints:**
```python
# ✅ CORRECT - VARCHAR with explicit length at DB level
from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String(50), unique=True, index=True, nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, index=True, nullable=False))
    hashed_password: str = Field(sa_column=Column(String(1024), nullable=False))
    role: str = Field(sa_column=Column(String(10), nullable=False, server_default="student"))
```

**When to use `sa_column`**:
- ALL string fields on `table=True` models (use `String(N)` for bounded, `Text` for unbounded like descriptions)
- Integer fields that need `server_default` (use `Column(Integer, server_default="3")`)
- Any field that needs DB-level constraints beyond what `Field()` provides

**When NOT to use `sa_column`**:
- Schema models (no `table=True`) — use `Field(min_length, max_length)` instead
- `id` fields — `Field(default=None, primary_key=True)` is fine
- Foreign key fields — `Field(foreign_key="table.id")` is fine
- Date/datetime fields — `Field(default_factory=...)` is fine

**Two-layer protection pattern**: Schema validates at API level, `sa_column` enforces at DB level. Both are mandatory.

---

## Implementation Workflow (After Setup)

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
  → Initialize pyproject.toml/requirements.txt (MUST include psycopg[binary])
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
  → Configure structured logging via structlog in `app/core/logging.py`
  → Add RequestLoggingMiddleware for request_id correlation
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
from pydantic import BaseModel, Field

app = FastAPI()

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
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
from datetime import datetime
from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel

# Table model (database) — ALWAYS use sa_column for string fields
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), index=True, nullable=False))
    secret_name: str = Field(sa_column=Column(String(100), nullable=False))
    age: int | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# API models (separate concerns) — ALWAYS add Field constraints
class HeroCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    secret_name: str = Field(min_length=1, max_length=100)
    age: int | None = Field(default=None, ge=0, le=150)

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
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    database_url: str        # loaded from DATABASE_URL in .env — no default = required
    debug: bool = False      # loaded from DEBUG in .env — defaults to False

settings = Settings()

engine = create_engine(settings.database_url, echo=settings.debug, pool_pre_ping=True)

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
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    secret_key: str                        # loaded from SECRET_KEY in .env — required, no default
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()

password_hash = PasswordHash((Argon2Hasher(),))
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
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
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
- [ ] Hash passwords with pwdlib[argon2]
- [ ] Validate all inputs: EmailStr for emails, Literal for enum-like fields, Field(min/max) for strings/numbers
- [ ] Use response_model to prevent data leaks
- [ ] Implement rate limiting via `utils/rate_limit.py` (auth: 5/min, signup: 10/hr, writes: 30/min, reads: 60/min)
- [ ] Register rate limiter in `main.py` with `setup_rate_limiter(app)`
- [ ] Use Redis storage for rate limits when running multiple workers
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
- [ ] `Field` imported from `sqlmodel` (not `pydantic`) in all files
- [ ] EmailStr on all email fields (never plain str)
- [ ] Literal types on all enum-like string fields (role, status, grade, category)
- [ ] Field(min_length, max_length) on all string input fields in schemas
- [ ] Field(ge, le) or Field(gt) on all numeric input fields in schemas
- [ ] `sa_column=Column(String(N))` on all string fields in table models
- [ ] `server_default` on columns with default values in table models
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
