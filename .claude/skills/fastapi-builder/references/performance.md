# FastAPI Performance Optimization

Performance best practices, async patterns, caching strategies, and optimization techniques for production FastAPI applications.

## 1. Async vs Sync - When to Use What

### Decision Tree

```
Is the operation I/O-bound (DB, API, file, network)?
├─ YES → Use async def + await
│   ├─ Database query → async def with AsyncSession
│   ├─ HTTP request → async def with httpx.AsyncClient
│   ├─ File I/O → async def with aiofiles
│   └─ Redis/cache → async def with aioredis
│
└─ NO → Is it CPU-intensive?
    ├─ YES → Use def (runs in threadpool)
    │   └─ Heavy computation, image processing
    └─ NO → Use async def (default for simple responses)
```

### Examples

```python
# ✅ Async for I/O-bound
@app.get("/users/{user_id}")
async def get_user(user_id: int, session: AsyncSessionDep):
    result = await session.exec(select(User).where(User.id == user_id))
    return result.first()

# ✅ Sync for CPU-bound
@app.post("/process")
def process_data(data: DataInput):
    # Heavy computation - runs in threadpool
    result = expensive_calculation(data)
    return result

# ✅ Async for simple responses (no real I/O)
@app.get("/health")
async def health():
    return {"status": "ok"}

# ❌ Don't mix - blocking sync in async
@app.get("/bad")
async def bad_example():
    # BAD: Blocks event loop
    import time
    time.sleep(1)
    return {"message": "slow"}
```

---

## 2. Database Optimization

### Connection Pooling

```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # Number of permanent connections
    max_overflow=10,      # Max additional connections
    pool_timeout=30,      # Wait time for connection
    pool_recycle=3600,    # Recycle after 1 hour
    pool_pre_ping=True,   # Verify connection before use
    echo=False            # Disable SQL logging in prod
)
```

### Environment-Specific Pools

```python
if settings.environment == "production":
    pool_config = {
        "pool_size": 20,
        "max_overflow": 40,
        "pool_pre_ping": True,
    }
elif settings.environment == "development":
    pool_config = {
        "pool_size": 5,
        "max_overflow": 10,
        "echo": True,  # Log queries
    }

engine = create_engine(DATABASE_URL, **pool_config)
```

### Eager Loading (Avoid N+1)

```python
from sqlalchemy.orm import selectinload, joinedload

# ❌ N+1 queries
users = session.exec(select(User)).all()
for user in users:
    print(user.posts)  # Separate query per user!

# ✅ Eager load with selectinload
statement = select(User).options(selectinload(User.posts))
users = session.exec(statement).all()
for user in users:
    print(user.posts)  # No extra queries!

# ✅ Eager load with joinedload (single SQL JOIN)
statement = select(User).options(joinedload(User.team))
users = session.exec(statement).all()
```

### Select Specific Columns

```python
# ❌ Select all columns
statement = select(User)

# ✅ Select only needed columns
from sqlalchemy import column
statement = select(User.id, User.username, User.email)
```

### Use Indexes

```python
from sqlmodel import Field, SQLModel, Index

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)  # Single column index
    email: str = Field(index=True, unique=True)
    team_id: int | None = Field(foreign_key="team.id", index=True)

    # Composite index
    __table_args__ = (
        Index("idx_user_team_active", "team_id", "is_active"),
    )
```

### Batch Operations

```python
# ❌ Individual inserts
for i in range(1000):
    user = User(username=f"user{i}")
    session.add(user)
    session.commit()  # 1000 commits!

# ✅ Bulk insert
users = [User(username=f"user{i}") for i in range(1000)]
session.add_all(users)
session.commit()  # 1 commit
```

---

## 3. Response Optimization

### Use response_model

```python
# ❌ Returns everything
@app.get("/users/{user_id}")
async def get_user(user_id: int, session: SessionDep):
    return session.get(User, user_id)
    # Includes hashed_password, internal fields, etc.

# ✅ Filters to only needed fields
@app.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, session: SessionDep):
    return session.get(User, user_id)
    # Only id, username, email returned
```

### response_model_exclude_unset

```python
class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    bio: str | None = None

@app.patch(
    "/users/{user_id}",
    response_model=UserPublic,
    response_model_exclude_unset=True  # Only set fields
)
async def update_user(user_id: int, update: UserUpdate, session: SessionDep):
    # If only username was updated, only return username
    ...
```

### Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress >1KB
```

---

## 4. Caching Strategies

### In-Memory Cache (Simple)

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_expensive_config():
    # Cached for lifetime of process
    return compute_expensive_config()

@app.get("/config")
async def config():
    return get_expensive_config()
```

### Redis Cache

```python
import redis.asyncio as redis
from datetime import timedelta

redis_client = redis.from_url("redis://localhost")

async def get_user_cached(user_id: int, session: AsyncSessionDep):
    # Try cache first
    cache_key = f"user:{user_id}"
    cached = await redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Cache miss - fetch from DB
    result = await session.exec(select(User).where(User.id == user_id))
    user = result.first()

    # Store in cache
    await redis_client.setex(
        cache_key,
        timedelta(minutes=5),
        json.dumps(user.model_dump())
    )

    return user
```

### Response Caching

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/items")
@cache(expire=60)  # Cache for 60 seconds
async def list_items():
    # Expensive operation
    return await fetch_items_from_db()
```

---

## 5. Background Tasks

### Use BackgroundTasks for Slow Operations

```python
from fastapi import BackgroundTasks

def send_email(to: str, subject: str, body: str):
    # Slow email sending
    time.sleep(5)
    print(f"Email sent to {to}")

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    # Add to background queue
    background_tasks.add_task(send_email, email, "Hello", "Body")

    # Return immediately
    return {"message": "Notification queued"}
```

### Use Task Queue for Heavy Work

```python
# Using Celery for distributed task processing
from celery import Celery

celery_app = Celery("tasks", broker="redis://localhost:6379")

@celery_app.task
def process_video(video_id: int):
    # Heavy video processing
    ...

@app.post("/upload-video")
async def upload_video(video: UploadFile, background_tasks: BackgroundTasks):
    video_id = save_video(video)

    # Queue heavy processing
    process_video.delay(video_id)

    return {"video_id": video_id, "status": "processing"}
```

---

## 6. Pagination Best Practices

### Offset-Based Pagination

```python
from fastapi import Query

@app.get("/items")
async def list_items(
    offset: int = 0,
    limit: int = Query(default=20, le=100),  # Max 100
    session: SessionDep
):
    statement = select(Item).offset(offset).limit(limit)
    items = session.exec(statement).all()

    return {
        "items": items,
        "offset": offset,
        "limit": limit,
    }
```

### Cursor-Based Pagination (Better for Large Datasets)

```python
@app.get("/items")
async def list_items(
    cursor: int | None = None,  # Last item ID
    limit: int = Query(default=20, le=100),
    session: SessionDep
):
    statement = select(Item)

    if cursor:
        statement = statement.where(Item.id > cursor)

    statement = statement.order_by(Item.id).limit(limit)
    items = session.exec(statement).all()

    next_cursor = items[-1].id if items else None

    return {
        "items": items,
        "next_cursor": next_cursor,
    }
```

---

## 7. Uvicorn Workers

### Calculate Workers

```python
# Formula: (2 x CPU cores) + 1

# For 2 CPUs:
# workers = (2 x 2) + 1 = 5

# For 4 CPUs:
# workers = (2 x 4) + 1 = 9
```

### Configuration

```dockerfile
# In Dockerfile
CMD ["fastapi", "run", "main.py", "--port", "80", "--workers", "4"]
```

```python
# In Python
import multiprocessing

workers = (2 * multiprocessing.cpu_count()) + 1

uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8000,
    workers=workers
)
```

### Worker Class (Async)

```bash
# Use uvloop for better async performance
pip install uvloop

# Uvicorn will auto-detect and use uvloop
```

---

## 8. Monitoring and Profiling

### Add Timing Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Prometheus Metrics

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

# Metrics available at /metrics
```

### Request Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

---

## 9. Static Files and CDN

### Serve Static Files Efficiently

```python
from fastapi.staticfiles import StaticFiles

# Let Nginx/CDN handle static files in production
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Use CDN for Production

```python
# Development
STATIC_URL = "/static"

# Production
STATIC_URL = "https://cdn.example.com/static"
```

---

## 10. HTTP/2 and Keep-Alive

### Enable HTTP/2 (via Nginx)

```nginx
server {
    listen 443 ssl http2;
    # ... rest of config
}
```

### Connection Pooling (Client Side)

```python
import httpx

# Reuse HTTP client
http_client = httpx.AsyncClient(
    timeout=10.0,
    limits=httpx.Limits(max_keepalive_connections=5)
)

@app.get("/external-api")
async def call_external_api():
    response = await http_client.get("https://api.example.com/data")
    return response.json()
```

---

## Performance Checklist

### Database
- [ ] Connection pooling configured
- [ ] Indexes on frequently queried columns
- [ ] Eager loading for relationships
- [ ] Pagination on list endpoints
- [ ] Bulk operations for batch inserts

### Async
- [ ] async/await for I/O-bound operations
- [ ] AsyncSession for database
- [ ] httpx.AsyncClient for HTTP requests
- [ ] Background tasks for slow operations

### Caching
- [ ] Redis for frequently accessed data
- [ ] @lru_cache for static config
- [ ] Response caching for expensive endpoints
- [ ] CDN for static files

### Response
- [ ] response_model filters sensitive data
- [ ] GZip compression enabled
- [ ] Pagination implemented
- [ ] Only return needed fields

### Deployment
- [ ] Uvicorn workers = (2 x CPU) + 1
- [ ] HTTP/2 enabled
- [ ] Health checks configured
- [ ] Monitoring/metrics added

### General
- [ ] No blocking I/O in async functions
- [ ] Connection pooling for external APIs
- [ ] Logging configured appropriately
- [ ] Static files served by Nginx/CDN
