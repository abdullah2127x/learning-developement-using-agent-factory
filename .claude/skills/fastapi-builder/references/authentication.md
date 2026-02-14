# FastAPI JWT Authentication

Complete JWT authentication implementation with OAuth2, scopes, and security best practices.

## Overview

FastAPI's security system is built on OAuth2 with Password (and Bearer) flows. JWT tokens provide stateless authentication.

**Key Components**:
- **OAuth2PasswordBearer**: Token extraction from Authorization header
- **OAuth2PasswordRequestForm**: Login form data (username/password)
- **JWT**: Token generation and validation
- **Passlib**: Password hashing (bcrypt/argon2)
- **Security**: Dependency with scope support

---

## Installation

```bash
pip install "python-jose[cryptography]"  # JWT encoding/decoding
pip install "passlib[bcrypt]"            # Password hashing
# OR for better security:
pip install argon2-cffi                  # Argon2 (recommended)
```

---

## Basic JWT Authentication

### Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Generate with: openssl rand -hex 32
    secret_key: str = "your-secret-key-keep-this-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### Password Hashing

```python
# app/core/security.py
from passlib.context import CryptContext

# Using bcrypt (good)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Using argon2 (better - recommended for production)
# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### JWT Token Operations

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.config import settings

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
```

### Models

```python
# app/models/user.py
from sqlmodel import Field, SQLModel
from datetime import datetime

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# app/schemas/user.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
```

### Authentication Dependencies

```python
# app/dependencies.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.security import decode_access_token
from app.database import get_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

### Authentication Endpoints

```python
# app/routers/auth.py
from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.security import verify_password, get_password_hash, create_access_token
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic, Token
from app.config import settings

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, session: SessionDep):
    # Check if user exists
    existing_user = session.exec(
        select(User).where(User.username == user_in.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
):
    # Authenticate user
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

### Protected Endpoints

```python
# app/routers/users.py
from typing import Annotated
from fastapi import APIRouter, Depends

from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter()

@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

@router.put("/me", response_model=UserPublic)
async def update_user_me(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: SessionDep
):
    # Update user logic
    current_user.email = user_update.email
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
```

---

## Advanced: OAuth2 Scopes

Scopes enable fine-grained permissions (e.g., "read:items", "write:items").

### Setup with Scopes

```python
# app/dependencies.py
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "me": "Read information about the current user",
        "items:read": "Read items",
        "items:write": "Create and update items",
        "admin": "Admin access"
    }
)

async def get_current_user_with_scopes(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)]
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    token_scopes = payload.get("scopes", [])

    # Validate scopes
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception

    return user
```

### Token with Scopes

```python
# app/routers/auth.py
@router.post("/token")
async def login_with_scopes(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
):
    user = authenticate_user(form_data.username, form_data.password, session)

    # Determine user scopes based on roles
    scopes = ["me", "items:read"]
    if user.is_superuser:
        scopes.extend(["items:write", "admin"])

    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes}
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

### Protected Endpoint with Scopes

```python
from fastapi import Security

@router.post("/items", response_model=ItemPublic)
async def create_item(
    item: ItemCreate,
    current_user: Annotated[User, Security(get_current_user_with_scopes, scopes=["items:write"])],
    session: SessionDep
):
    # Only users with "items:write" scope can access
    db_item = Item(**item.model_dump(), owner_id=current_user.id)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/items", response_model=list[ItemPublic])
async def read_items(
    current_user: Annotated[User, Security(get_current_user_with_scopes, scopes=["items:read"])],
    session: SessionDep
):
    # Users with "items:read" scope can access
    items = session.exec(select(Item)).all()
    return items
```

---

## Refresh Tokens

For longer sessions, implement refresh tokens.

### Models

```python
class RefreshToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
```

### Token Generation

```python
import secrets

def create_refresh_token(user_id: int, session: Session) -> str:
    # Generate secure random token
    token = secrets.token_urlsafe(32)

    # Store in database
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    session.add(refresh_token)
    session.commit()

    return token
```

### Refresh Endpoint

```python
@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    session: SessionDep
):
    # Validate refresh token
    db_token = session.exec(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    ).first()

    if not db_token or db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get user
    user = session.get(User, db_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Create new access token
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
```

---

## Security Best Practices

### 1. Secret Key Management

```python
# .env
SECRET_KEY=use-openssl-rand-hex-32-to-generate-this
DATABASE_URL=postgresql+psycopg://user:pass@localhost/db

# NEVER commit .env to git!
# Add to .gitignore
```

### 2. Password Requirements

```python
import re

def validate_password(password: str) -> bool:
    """
    Require:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

@router.post("/register")
async def register(user_in: UserCreate, session: SessionDep):
    if not validate_password(user_in.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    # ... rest of registration logic
```

### 3. Rate Limiting

```python
# Using slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/token")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, ...):
    # ... login logic
```

### 4. Token Expiration

```python
# Short-lived access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes

# Long-lived refresh tokens
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days

# Include issued-at time in token
def create_access_token(data: dict):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 5. Response Model Security

```python
# NEVER return hashed_password in responses
class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    # NO hashed_password here!

@router.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    # FastAPI automatically filters out hashed_password
    return user
```

### 6. HTTPS Only in Production

```python
# app/middleware.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

## Testing Authentication

```python
# tests/test_auth.py
from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "hashed_password" not in data

def test_login_success(client: TestClient, test_user):
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user):
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "WrongPassword"
    })
    assert response.status_code == 401

def test_access_protected_endpoint(client: TestClient, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_access_protected_without_token(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401
```

See `references/testing.md` for complete test fixtures.

---

## Common Patterns

### Admin-Only Endpoints

```python
async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: Annotated[User, Depends(get_current_admin_user)],
    session: SessionDep
):
    # Only admins can delete users
    user = session.get(User, user_id)
    session.delete(user)
    session.commit()
    return {"ok": True}
```

### API Key Authentication

```python
from fastapi import Header

async def get_api_key(x_api_key: Annotated[str, Header()]) -> str:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

@router.get("/public-api/data")
async def public_api(api_key: Annotated[str, Depends(get_api_key)]):
    return {"data": "sensitive information"}
```
