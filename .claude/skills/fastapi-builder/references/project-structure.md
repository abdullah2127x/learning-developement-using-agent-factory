# FastAPI Project Structures

Progressive project structures from hello world to enterprise scale.

## Hello World (Single File)

**When**: Learning, proof of concept, <10 endpoints

```
myapp/
├── main.py
├── requirements.txt
└── .env
```

**main.py**:
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

**requirements.txt**:
```
fastapi[standard]>=0.115.0
```

**Run**:
```bash
fastapi dev main.py
```

---

## Small Project (10-20 endpoints)

**When**: Simple APIs, single domain, 1-3 models

```
myapp/
├── main.py          # App initialization, all endpoints
├── models.py        # Pydantic/SQLModel models
├── database.py      # DB connection, session
├── requirements.txt
├── .env
└── .env.example
```

**Organized by sections in main.py**:
```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# User endpoints
@app.post("/users")
async def create_user(...): ...

@app.get("/users/{user_id}")
async def get_user(...): ...

# Item endpoints
@app.post("/items")
async def create_item(...): ...

@app.get("/items")
async def list_items(...): ...
```

---

## Medium Project (20-50 endpoints)

**When**: Multiple domains, modular organization, team collaboration

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Settings (BaseSettings)
│   ├── database.py          # DB engine, session dependency
│   ├── models.py            # SQLModel table models
│   ├── schemas.py           # Pydantic API models (request/response)
│   ├── dependencies.py      # Shared dependencies (auth, etc.)
│   └── routers/
│       ├── __init__.py
│       ├── users.py         # User endpoints
│       ├── items.py         # Item endpoints
│       └── auth.py          # Authentication endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_users.py
│   ├── test_items.py
│   └── test_auth.py
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── requirements.txt
├── pyproject.toml
├── .env
├── .env.example
├── Dockerfile
└── README.md
```

**app/main.py**:
```python
from fastapi import FastAPI
from app.routers import users, items, auth
from app.database import create_db_and_tables

app = FastAPI(title="My API", version="1.0.0")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(items.router, prefix="/items", tags=["Items"])

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**app/routers/users.py**:
```python
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas import UserCreate, UserPublic
from app.dependencies import get_current_user

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=UserPublic)
async def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
```

**app/config.py**:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

---

## Large/Enterprise Project (50+ endpoints)

**When**: Multiple teams, complex business logic, microservices

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── exceptions.py        # Custom exceptions
│   ├── middleware.py        # Custom middleware
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py      # Auth utilities
│   │   ├── database.py      # DB connection
│   │   └── logging.py       # Logging config
│   ├── models/              # Database models (SQLModel)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── item.py
│   │   └── order.py
│   ├── schemas/             # API models (Pydantic)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── item.py
│   │   └── order.py
│   ├── api/                 # API layer
│   │   ├── __init__.py
│   │   ├── dependencies.py  # Shared dependencies
│   │   └── v1/              # API version 1
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── users.py
│   │       │   ├── items.py
│   │       │   ├── orders.py
│   │       │   └── auth.py
│   │       └── api.py       # v1 router aggregation
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── item_service.py
│   │   └── order_service.py
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repo.py
│   │   ├── item_repo.py
│   │   └── order_repo.py
│   └── utils/
│       ├── __init__.py
│       ├── email.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_services/
│   │   └── test_repositories/
│   ├── integration/
│   │   └── test_api/
│   └── e2e/
├── alembic/
│   ├── versions/
│   └── env.py
├── scripts/                 # Utility scripts
│   ├── init_db.py
│   └── seed_data.py
├── docs/                    # Additional documentation
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

**app/main.py**:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router as v1_router
from app.core.database import create_db_and_tables
from app.core.logging import setup_logging
from app.config import settings
from app.middleware import add_custom_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    create_db_and_tables()
    yield
    # Shutdown
    # Cleanup resources here

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
add_custom_middleware(app)

# API routers
app.include_router(v1_router, prefix=settings.api_v1_prefix)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**app/api/v1/api.py** (Router aggregation):
```python
from fastapi import APIRouter
from app.api.v1.endpoints import users, items, orders, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(items.router, prefix="/items", tags=["Items"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
```

**Layered Architecture**:

```python
# app/api/v1/endpoints/users.py (API layer)
from fastapi import APIRouter, Depends
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserPublic

router = APIRouter()

@router.post("/", response_model=UserPublic)
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends()
):
    return await user_service.create_user(user_in)

# app/services/user_service.py (Business logic)
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserService:
    def __init__(self, repo: UserRepository = Depends()):
        self.repo = repo

    async def create_user(self, user_in: UserCreate):
        hashed_password = get_password_hash(user_in.password)
        return await self.repo.create(user_in, hashed_password)

# app/repositories/user_repo.py (Data access)
from sqlmodel import Session, select
from app.models.user import User

class UserRepository:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def create(self, user_data, hashed_password):
        db_user = User(**user_data.model_dump(), hashed_password=hashed_password)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
```

---

## Key Principles

### Separation of Concerns

| Layer | Responsibility | Should NOT |
|-------|---------------|------------|
| **API (routers)** | HTTP request/response, validation | Contain business logic, DB queries |
| **Services** | Business logic, orchestration | Know about HTTP, handle DB connections |
| **Repositories** | Data access, queries | Contain business logic |
| **Models** | Data structure, validation | Contain business logic |

### File Organization Rules

1. **models/** = Database tables (SQLModel with `table=True`)
2. **schemas/** = API request/response models (Pydantic without `table=True`)
3. **routers/endpoints/** = HTTP layer only
4. **services/** = Business logic (no HTTP knowledge)
5. **repositories/** = Database operations only

### When to Split Files

- **Single model per file** when models >100 lines
- **Router per resource** when >5 endpoints per resource
- **Service layer** when business logic >50 lines
- **Repository layer** when complex queries or multiple data sources

---

## Migration Path

### From Small → Medium

1. Create `app/` directory
2. Move `main.py` → `app/main.py`
3. Split endpoints into `app/routers/`
4. Extract models to `app/models.py`
5. Add tests in `tests/`

### From Medium → Large

1. Split `models.py` → `models/` directory
2. Split `schemas.py` → `schemas/` directory
3. Create `services/` for business logic
4. Create `repositories/` for data access
5. Add API versioning (`api/v1/`)
6. Separate environment requirements

---

## Quick Decision Guide

```
How many endpoints?
├─ <10 → Single file (hello world)
├─ 10-20 → Small project (organized single file)
├─ 20-50 → Medium project (routers, modular)
└─ 50+ → Large project (layered architecture)

How many developers?
├─ 1-2 → Small/Medium
├─ 3-5 → Medium
└─ 5+ → Large (with layers)

Business logic complexity?
├─ Simple CRUD → Medium (routers only)
└─ Complex workflows → Large (service layer)

Multiple data sources?
├─ Single DB → Medium
└─ Multiple DBs/APIs → Large (repository layer)
```
