# PostgreSQL + SQLModel Integration

Complete database integration guide for FastAPI with SQLModel, async support, migrations, and best practices.

## Overview

**SQLModel** = SQLAlchemy + Pydantic. It provides:
- Table models (ORM) with `table=True`
- API models (validation) without `table=True`
- Type hints for validation and documentation
- Async support with `asyncpg`

---

## Installation

```bash
# Sync PostgreSQL (psycopg3)
pip install sqlmodel psycopg[binary]

# Async PostgreSQL (recommended for production)
pip install sqlmodel asyncpg

# Migrations
pip install alembic
```

---

## Database Connection (Sync)

### Basic Setup

```python
# app/database.py
from sqlmodel import SQLModel, create_engine, Session

# PostgreSQL connection string
DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/dbname"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max connections beyond pool_size
)

def create_db_and_tables():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for database sessions"""
    with Session(engine) as session:
        yield session
```

### Usage in FastAPI

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(lifespan=lifespan)
```

---

## Database Connection (Async)

### Async Setup

```python
# app/database.py
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Async PostgreSQL connection string
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_size=5,
    max_overflow=10
)

# Session maker
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_async_session():
    async with async_session_maker() as session:
        yield session
```

### Async Usage

```python
from typing import Annotated
from fastapi import Depends
from sqlmodel import select

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]

@app.get("/users")
async def list_users(session: AsyncSessionDep):
    result = await session.exec(select(User))
    users = result.all()
    return users

@app.post("/users")
async def create_user(user: UserCreate, session: AsyncSessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
```

---

## SQLModel Models

### Table Models vs API Models

```python
# app/models/user.py
from sqlmodel import Field, SQLModel
from datetime import datetime

# Base model (shared fields)
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    is_active: bool = True

# Table model (database)
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# app/schemas/user.py
from sqlmodel import SQLModel

# API models (request/response)
class UserCreate(UserBase):
    password: str  # Plain password for input

class UserPublic(UserBase):
    id: int
    created_at: datetime
    # Note: hashed_password excluded for security

class UserUpdate(SQLModel):
    email: str | None = None
    full_name: str | None = None
    password: str | None = None
```

### Relationships

```python
from sqlmodel import Field, Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Relationship to users
    users: list["User"] = Relationship(back_populates="team")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    team_id: int | None = Field(default=None, foreign_key="team.id")

    # Relationship to team
    team: Team | None = Relationship(back_populates="users")

# Many-to-many example
class ProjectUserLink(SQLModel, table=True):
    project_id: int = Field(foreign_key="project.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)

class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    users: list["User"] = Relationship(back_populates="projects", link_model=ProjectUserLink)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    projects: list[Project] = Relationship(back_populates="users", link_model=ProjectUserLink)
```

---

## CRUD Operations

### Create

```python
from sqlmodel import Session, select

def create_user(user_in: UserCreate, session: Session) -> User:
    # Method 1: Direct instantiation
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )

    # Method 2: Using model_validate (preferred)
    db_user = User.model_validate(user_in, update={"hashed_password": hashed})

    session.add(db_user)
    session.commit()
    session.refresh(db_user)  # Get generated id and defaults
    return db_user
```

### Read (Select)

```python
from sqlmodel import select

# Get by ID
def get_user(user_id: int, session: Session) -> User | None:
    return session.get(User, user_id)

# Get by field
def get_user_by_username(username: str, session: Session) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

# List with pagination
def list_users(session: Session, offset: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(offset).limit(limit)
    return session.exec(statement).all()

# Filter and order
def list_active_users(session: Session) -> list[User]:
    statement = select(User).where(User.is_active == True).order_by(User.created_at.desc())
    return session.exec(statement).all()

# Join example
def get_users_with_teams(session: Session):
    statement = select(User).join(Team).where(Team.name == "Engineering")
    return session.exec(statement).all()
```

### Update

```python
def update_user(user_id: int, user_update: UserUpdate, session: Session) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get only set fields (exclude_unset=True)
    user_data = user_update.model_dump(exclude_unset=True)

    # Handle password update
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

    # Update model
    db_user.sqlmodel_update(user_data)
    db_user.updated_at = datetime.utcnow()

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
```

### Delete

```python
def delete_user(user_id: int, session: Session) -> dict:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    session.commit()
    return {"ok": True}

# Soft delete (preferred for production)
def soft_delete_user(user_id: int, session: Session) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_active = False
    db_user.deleted_at = datetime.utcnow()
    session.add(db_user)
    session.commit()
    return db_user
```

---

## Database Migrations (Alembic)

### Setup

```bash
# Initialize Alembic
alembic init alembic

# Configure alembic.ini
# Edit: sqlalchemy.url = postgresql+psycopg://user:password@localhost/dbname
```

### Configure Alembic for SQLModel

```python
# alembic/env.py
from sqlmodel import SQLModel
from app.models.user import User  # Import all models
from app.models.item import Item
from app.config import settings

# Set target metadata
target_metadata = SQLModel.metadata

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = create_engine(configuration["sqlalchemy.url"])

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

### Create and Apply Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1

# Check current version
alembic current

# View history
alembic history
```

---

## Connection Pooling

### Pool Configuration

```python
from sqlmodel import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,          # Number of connections to maintain
    max_overflow=10,      # Max connections beyond pool_size
    pool_timeout=30,      # Seconds to wait for connection
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_pre_ping=True,   # Test connection before using
    echo_pool=True        # Log pool operations (dev only)
)
```

### Environment-Specific Pools

```python
from app.config import settings

if settings.environment == "production":
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
        echo=False
    )
elif settings.environment == "testing":
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:  # development
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        echo=True  # Log queries in dev
    )
```

---

## Advanced Queries

### Complex Filters

```python
from sqlmodel import select, or_, and_

# OR condition
statement = select(User).where(
    or_(User.email == "test@example.com", User.username == "testuser")
)

# AND condition
statement = select(User).where(
    and_(User.is_active == True, User.created_at > some_date)
)

# IN clause
user_ids = [1, 2, 3]
statement = select(User).where(User.id.in_(user_ids))

# LIKE clause
statement = select(User).where(User.username.like("%admin%"))

# IS NULL
statement = select(User).where(User.team_id.is_(None))
```

### Aggregations

```python
from sqlalchemy import func

# Count
statement = select(func.count(User.id))
total_users = session.exec(statement).one()

# Group by
statement = select(User.team_id, func.count(User.id)).group_by(User.team_id)
results = session.exec(statement).all()

# Having
statement = (
    select(User.team_id, func.count(User.id).label("user_count"))
    .group_by(User.team_id)
    .having(func.count(User.id) > 5)
)
```

### Subqueries

```python
# Scalar subquery
subquery = select(func.count(User.id)).where(User.team_id == Team.id).scalar_subquery()
statement = select(Team.name, subquery.label("user_count"))

# Subquery in WHERE
active_user_ids = select(User.id).where(User.is_active == True).subquery()
statement = select(Project).join(ProjectUserLink).where(
    ProjectUserLink.user_id.in_(active_user_ids)
)
```

---

## Transaction Management

### Auto-commit (Default)

```python
def create_user(user_in: UserCreate, session: Session):
    db_user = User.model_validate(user_in)
    session.add(db_user)
    session.commit()  # Auto-committed
    return db_user
```

### Manual Transactions

```python
def create_user_with_team(user_in: UserCreate, team_name: str, session: Session):
    try:
        # Create team
        team = Team(name=team_name)
        session.add(team)
        session.flush()  # Get team.id without committing

        # Create user with team
        db_user = User.model_validate(user_in, update={"team_id": team.id})
        session.add(db_user)

        # Commit both
        session.commit()
        return db_user
    except Exception as e:
        session.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=str(e))
```

### Nested Transactions (Savepoints)

```python
def complex_operation(session: Session):
    session.begin_nested()  # Create savepoint
    try:
        # Risky operation
        db_user = User(username="test")
        session.add(db_user)
        session.commit()  # Commit savepoint
    except Exception:
        session.rollback()  # Rollback to savepoint
        # Continue with alternative logic
```

---

## Performance Best Practices

### 1. Use Eager Loading

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# N+1 problem (BAD)
users = session.exec(select(User)).all()
for user in users:
    print(user.team.name)  # Separate query for each user!

# Eager loading (GOOD)
statement = select(User).options(selectinload(User.team))
users = session.exec(statement).all()
for user in users:
    print(user.team.name)  # No extra queries
```

### 2. Pagination

```python
@app.get("/users")
def list_users(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100)  # Max 100
):
    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()
    return users
```

### 3. Indexes

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)  # Single column index
    email: str = Field(index=True, unique=True)
    team_id: int | None = Field(foreign_key="team.id", index=True)

    __table_args__ = (
        # Composite index
        Index("idx_user_team_active", "team_id", "is_active"),
    )
```

### 4. Select Only Needed Columns

```python
# Select specific columns
statement = select(User.id, User.username, User.email)
results = session.exec(statement).all()
```

### 5. Batch Operations

```python
# Bulk insert
users = [User(username=f"user{i}") for i in range(100)]
session.add_all(users)
session.commit()

# Bulk update
statement = update(User).where(User.is_active == False).values(deleted_at=datetime.utcnow())
session.exec(statement)
session.commit()
```

---

## Common Patterns

### Repository Pattern

```python
# app/repositories/user_repo.py
from sqlmodel import Session, select

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def list(self, offset: int = 0, limit: int = 100) -> list[User]:
        statement = select(User).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
```

### Testing Database

See `testing.md` for complete database testing patterns.
