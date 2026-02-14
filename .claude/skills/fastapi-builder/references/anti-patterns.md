# FastAPI Anti-Patterns and Common Mistakes

Common mistakes to avoid when building FastAPI applications, based on official documentation and production experience.

## 1. Security Anti-Patterns

### ❌ Hardcoded Secrets

```python
# BAD: Never do this!
SECRET_KEY = "my-secret-key-123"
DATABASE_URL = "postgresql://user:password@localhost/db"
API_KEY = "abc123"
```

### ✅ Use Environment Variables

```python
# GOOD: Use environment variables
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

### ❌ Exposing Sensitive Data in Responses

```python
# BAD: Returns hashed_password!
@app.get("/users/{user_id}")
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    return user  # Includes hashed_password field!
```

### ✅ Use Response Models

```python
# GOOD: Filters sensitive fields
class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    # hashed_password NOT included

@app.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    return user  # FastAPI filters to UserPublic fields only
```

### ❌ Weak CORS Configuration

```python
# BAD: Allows any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # DANGER!
    allow_credentials=True,  # Security risk with "*"
)
```

### ✅ Explicit CORS Origins

```python
# GOOD: Specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",
        "https://app.example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 2. Database Anti-Patterns

### ❌ Not Closing Database Sessions

```python
# BAD: Session leak!
def get_user(user_id: int):
    session = Session(engine)
    user = session.get(User, user_id)
    return user  # Session never closed!
```

### ✅ Use Dependency with Yield

```python
# GOOD: Auto-closes session
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/users/{user_id}")
async def get_user(user_id: int, session: SessionDep):
    return session.get(User, user_id)
```

### ❌ N+1 Query Problem

```python
# BAD: Executes N+1 queries
users = session.exec(select(User)).all()
for user in users:
    print(user.team.name)  # Separate query for each user!
```

### ✅ Use Eager Loading

```python
# GOOD: Single query with join
from sqlalchemy.orm import selectinload

statement = select(User).options(selectinload(User.team))
users = session.exec(statement).all()
for user in users:
    print(user.team.name)  # No extra queries
```

### ❌ No Pagination on Lists

```python
# BAD: Could return millions of records
@app.get("/users")
async def list_users(session: SessionDep):
    return session.exec(select(User)).all()  # DANGER!
```

### ✅ Always Paginate

```python
# GOOD: Limit results
@app.get("/users")
async def list_users(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100)  # Max 100
):
    statement = select(User).offset(offset).limit(limit)
    return session.exec(statement).all()
```

### ❌ Forgetting to Commit

```python
# BAD: Changes not saved!
@app.post("/users")
async def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    # Missing: session.commit()
    return db_user  # Not actually in database!
```

### ✅ Always Commit

```python
# GOOD: Commit changes
@app.post("/users")
async def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)  # Get generated ID
    return db_user
```

---

## 3. Async/Sync Misuse

### ❌ Using Sync DB in Async Function

```python
# BAD: Blocks event loop!
@app.get("/users")
async def list_users(session: SessionDep):  # async but...
    users = session.exec(select(User)).all()  # ...sync DB call!
    return users
```

### ✅ Use Async DB with Async Function

```python
# GOOD: Fully async
@app.get("/users")
async def list_users(session: AsyncSessionDep):
    result = await session.exec(select(User))
    return result.all()
```

### ❌ Unnecessary async

```python
# BAD: No I/O, doesn't need async
@app.get("/hello")
async def hello():
    return {"message": "Hello"}  # No await, why async?
```

### ✅ Use def for Simple Handlers

```python
# GOOD: Simpler without async
@app.get("/hello")
def hello():
    return {"message": "Hello"}
```

---

## 4. Dependency Injection Anti-Patterns

### ❌ Not Using Depends()

```python
# BAD: Manual dependency management
@app.get("/users/me")
async def get_current_user(token: str):
    if not token:
        raise HTTPException(401)
    # Duplicate auth logic everywhere!
    ...
```

### ✅ Use Depends() for Reusability

```python
# GOOD: Reusable dependency
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # Auth logic once, reuse everywhere
    ...

@app.get("/users/me")
async def read_users_me(user: Annotated[User, Depends(get_current_user)]):
    return user
```

### ❌ Missing Annotated with Depends

```python
# BAD: Won't work in Python 3.10+
@app.get("/items")
async def list_items(session: Session = Depends(get_session)):
    ...
```

### ✅ Use Annotated

```python
# GOOD: Type-safe and future-proof
from typing import Annotated

@app.get("/items")
async def list_items(session: Annotated[Session, Depends(get_session)]):
    ...
```

---

## 5. Validation Anti-Patterns

### ❌ Not Using Pydantic Models

```python
# BAD: No validation!
@app.post("/users")
async def create_user(username: str, email: str, password: str):
    # What if email is invalid? Password too short?
    ...
```

### ✅ Use Pydantic for Validation

```python
# GOOD: Automatic validation
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr  # Validates email format
    password: str

@app.post("/users")
async def create_user(user: UserCreate):
    # Already validated!
    ...
```

### ❌ Not Setting Constraints

```python
# BAD: No limits
class Item(BaseModel):
    name: str  # Could be empty or 10,000 chars
    price: float  # Could be negative
```

### ✅ Add Field Constraints

```python
# GOOD: Enforced limits
from pydantic import Field

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)  # Greater than 0
    quantity: int = Field(ge=0, le=1000)  # 0-1000
```

---

## 6. Error Handling Anti-Patterns

### ❌ Generic Error Messages

```python
# BAD: Not helpful
@app.get("/users/{user_id}")
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404)  # Just "Not Found"
    return user
```

### ✅ Descriptive Error Messages

```python
# GOOD: Clear messages
@app.get("/users/{user_id}")
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    return user
```

### ❌ Exposing Internal Errors

```python
# BAD: Leaks internal details
@app.post("/users")
async def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()  # Might raise IntegrityError with SQL details!
    return db_user
```

### ✅ Catch and Sanitize Errors

```python
# GOOD: User-friendly errors
from sqlalchemy.exc import IntegrityError

@app.post("/users")
async def create_user(user: UserCreate, session: SessionDep):
    try:
        db_user = User.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
```

---

## 7. Performance Anti-Patterns

### ❌ No Connection Pooling

```python
# BAD: New connection every time
engine = create_engine(DATABASE_URL)  # No pool config
```

### ✅ Configure Connection Pool

```python
# GOOD: Reuses connections
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
```

### ❌ Returning Entire Objects

```python
# BAD: Returns ALL fields
@app.get("/users")
async def list_users(session: SessionDep):
    return session.exec(select(User)).all()
    # Includes hashed_password, internal fields, etc.
```

### ✅ Use response_model

```python
# GOOD: Returns only needed fields
@app.get("/users", response_model=list[UserPublic])
async def list_users(session: SessionDep):
    return session.exec(select(User)).all()
    # Filters to UserPublic fields
```

### ❌ Synchronous I/O in Async Function

```python
# BAD: Blocks event loop
@app.get("/data")
async def get_data():
    response = requests.get("https://api.example.com/data")  # Blocks!
    return response.json()
```

### ✅ Use Async HTTP Client

```python
# GOOD: Non-blocking
import httpx

@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()
```

---

## 8. Testing Anti-Patterns

### ❌ Not Isolating Tests

```python
# BAD: Tests affect each other
def test_create_user(client):
    client.post("/users", json={"username": "test"})

def test_user_exists(client):
    # Assumes test_create_user ran first!
    response = client.get("/users/1")
    assert response.status_code == 200
```

### ✅ Use Fixtures for Isolation

```python
# GOOD: Each test independent
@pytest.fixture
def test_user(session):
    user = User(username="test")
    session.add(user)
    session.commit()
    return user

def test_get_user(client, test_user):
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
```

### ❌ Testing Against Production DB

```python
# BAD: Uses real database
DATABASE_URL = "postgresql://prod_user:pass@prod_server/prod_db"
```

### ✅ Use Test Database

```python
# GOOD: In-memory or test DB
@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

---

## 9. Documentation Anti-Patterns

### ❌ No Endpoint Descriptions

```python
# BAD: No context in /docs
@app.post("/users")
async def create_user(user: UserCreate):
    ...
```

### ✅ Add Descriptions and Tags

```python
# GOOD: Clear documentation
@app.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Create a new user",
    description="Register a new user with username, email, and password"
)
async def create_user(user: UserCreate):
    """
    Create a new user:
    - **username**: Unique username (3-50 chars)
    - **email**: Valid email address
    - **password**: Min 8 chars with uppercase, lowercase, digit
    """
    ...
```

---

## 10. Project Structure Anti-Patterns

### ❌ Everything in main.py

```python
# BAD: 2000+ lines in main.py
# All models, routes, dependencies, config...
```

### ✅ Modular Structure

```
app/
├── main.py
├── config.py
├── database.py
├── models/
├── schemas/
├── routers/
└── dependencies.py
```

### ❌ Circular Imports

```python
# BAD: models.py imports schemas.py, schemas.py imports models.py
# Results in ImportError
```

### ✅ Proper Import Hierarchy

```
config.py
  ↓
database.py
  ↓
models.py
  ↓
schemas.py
  ↓
dependencies.py
  ↓
routers.py
  ↓
main.py
```

---

## Quick Checklist

Before deploying, verify:

- [ ] No hardcoded secrets
- [ ] Sensitive data excluded from responses
- [ ] CORS configured with specific origins
- [ ] Database sessions closed properly
- [ ] Pagination on list endpoints
- [ ] Connection pooling configured
- [ ] async/await used correctly
- [ ] Dependencies use Annotated[Type, Depends(...)]
- [ ] Pydantic models for all inputs
- [ ] Error messages are user-friendly
- [ ] Tests use isolated fixtures
- [ ] Endpoints have descriptions
- [ ] Code is modular (not all in main.py)
