# 🎯 Complete Learning Roadmap
## Backend Development Mastery Path

**Created**: 2026-03-31   
**Based On**: Your Todo Chatbot Backend Implementation  
**Level**: Intermediate → Advanced  
**Estimated Time**: 12-16 weeks (3-4 months)  
**Focus**: Full-Stack Backend Development with FastAPI, Python, AI Integration

---

## 📊 Current Knowledge Assessment

Based on our work together building your backend, here's an honest assessment of your current understanding:

| Topic | Exposure Level | Current Understanding | Priority |
|-------|---------------|----------------------|----------|
| **FastAPI routers** | ✅ Used extensively | 🟡 Partial | HIGH |
| **Dependency injection** | ✅ Used (CurrentUser, DbSession) | 🔴 Unclear | HIGH |
| **Pydantic schemas** | ✅ Used for validation | 🟡 Partial | MEDIUM |
| **SQLModel/SQLAlchemy** | ✅ Used for DB operations | 🟡 Partial | HIGH |
| **JWT authentication** | ✅ Integrated via Better Auth | 🔴 Unclear | HIGH |
| **Better Auth** | ✅ Configured | 🔴 Black box | MEDIUM |
| **MCP protocol** | ✅ Implemented | 🔴 New concept | MEDIUM |
| **SSE streaming** | ✅ Implemented | 🟡 Surface level | MEDIUM |
| **Rate limiting** | ✅ Added | 🟡 Surface level | LOW |
| **Logging** | ✅ Enhanced | 🟡 Basic usage | LOW |
| **Python async/await** | ✅ Used throughout | 🟡 Partial | HIGH |
| **Type hints** | ✅ Seen everywhere | 🔴 Unclear | MEDIUM |
| **Decorators** | ✅ Used (@router.post, @limiter.limit) | 🔴 Unclear | MEDIUM |

**Legend**: 
- ✅ Exposed to it
- 🟡 Partial understanding
- 🔴 Unclear/Black box

---

## 📚 Learning Roadmap (Step-by-Step)

### **Phase 1: Python Fundamentals** (2-3 weeks)
*Foundation for everything else*

---

#### **Week 1: Advanced Python Concepts**

##### **1. Type Hints & Generics** 🔴 Priority: MEDIUM

**What You See But Might Not Understand**:
```python
# You see this everywhere in your code
from typing import Optional, List, AsyncGenerator, Dict, Annotated

def get_user(user_id: str) -> Optional[Dict[str, any]]:
    pass

async def stream_tokens() -> AsyncGenerator[str, None]:
    pass

# In your routers
CurrentUser = Annotated[str, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_session)]
```

**What to Learn**:
- [ ] What are type hints and why use them?
- [ ] `Optional[T]` vs `T | None` (Python 3.10+)
- [ ] Generic types: `List[T]`, `Dict[K, V]`, `Callable[[args], return]`
- [ ] Type variables and generics
- [ ] Runtime type checking with Pydantic
- [ ] `Annotated[T, metadata]` for dependency injection

**Resources**:
- [Python Type Hints Official Docs](https://docs.python.org/3/library/typing.html)
- [Real Python Type Hints Guide](https://realpython.com/python-type-checking/)
- Practice: Add type hints to any untyped code in your project

**Practice Exercises**:
1. Add type hints to `backend/src/utils/helpers.py`
2. Create a generic function that works with any SQLModel
3. Use `Annotated` to create a custom dependency type

---

##### **2. Decorators** 🔴 Priority: HIGH

**What You Use But Might Not Understand**:
```python
# You use these everywhere
@router.post("/chat")
@limiter.limit("20/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    user_id: CurrentUser,
    session: DbSession,
):
    pass
```

**What to Learn**:
- [ ] What is a decorator? (Function that modifies another function)
- [ ] Function decorators vs class decorators
- [ ] Decorators with arguments (`@limiter.limit("20/minute")`)
- [ ] Writing your own decorators
- [ ] `functools.wraps` for preserving metadata
- [ ] Stack multiple decorators (order matters!)

**Resources**:
- [Python Decorators - Real Python](https://realpython.com/primer-on-python-decorators/)
- [Python Decorators - Official Docs](https://docs.python.org/3/glossary.html#term-decorator)

**Practice Exercises**:
1. Write a `@timing_decorator` that logs how long a function takes
2. Write a `@retry` decorator that retries failed functions 3 times
3. Write a `@log_calls` decorator that logs every function call
4. Apply your decorators to existing functions in your codebase

---

##### **3. Context Managers** 🟡 Priority: MEDIUM

**What You've Seen**:
```python
# In your main.py lifespan
async with AsyncExitStack() as stack:
    await stack.enter_async_context(mcp.session_manager.run())
    yield

# In your database session
with Session(engine) as session:
    try:
        session.add(task)
        session.commit()
    finally:
        session.close()
```

**What to Learn**:
- [ ] `with` statement and context managers
- [ ] `__enter__` and `__exit__` methods
- [ ] `contextlib` module (`@contextmanager` decorator)
- [ ] Async context managers (`async with`)
- [ ] Resource management (files, DB connections, locks)
- [ ] Why context managers prevent resource leaks

**Resources**:
- [Python Context Managers - Real Python](https://realpython.com/python-with-context-manager/)
- [contextlib Documentation](https://docs.python.org/3/library/contextlib.html)

**Practice Exercises**:
1. Write a context manager that times code execution
2. Write an async context manager for database sessions
3. Use `@contextmanager` to simplify your context managers

---

#### **Week 2: Async/Await Mastery**

##### **1. Event Loop & Coroutines** 🔴 Priority: HIGH

**What You Use**:
```python
# Every endpoint in your backend
async def handle_chat(
    user_id: str,
    message: str,
    conversation_id: Optional[str],
    session: Session,
) -> ChatResponse:
    result = await Runner.run(agent, input)
    return result
```

**What to Learn**:
- [ ] What is an event loop?
- [ ] Synchronous vs Asynchronous code
- [ ] `async def` vs regular `def`
- [ ] `await` keyword and what it does
- [ ] `asyncio.run()`, `asyncio.create_task()`
- [ ] Blocking the event loop (and why it's bad)
- [ ] CPU-bound vs I/O-bound operations

**Resources**:
- [Async IO in Python - Real Python](https://realpython.com/async-io-python/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

**Practice Exercises**:
1. Convert a synchronous function to async
2. Use `asyncio.gather()` to run multiple tasks concurrently
3. Identify and fix any blocking calls in your code

---

##### **2. Concurrent Execution** 🟡 Priority: MEDIUM

**What You Could Use**:
```python
# Running multiple async operations concurrently
async def process_multiple():
    task1 = asyncio.create_task(fetch_user())
    task2 = asyncio.create_task(fetch_tasks())
    results = await asyncio.gather(task1, task2)
    return results
```

**What to Learn**:
- [ ] `asyncio.gather()` - run multiple tasks
- [ ] `asyncio.wait()` - wait for tasks with options
- [ ] `asyncio.create_task()` - schedule coroutines
- [ ] Task cancellation and timeouts
- [ ] Race conditions in async code
- [ ] Async locks and semaphores

**Resources**:
- [Asyncio Tasks Documentation](https://docs.python.org/3/library/asyncio-task.html)

**Practice Exercises**:
1. Fetch data from 3 APIs concurrently using `asyncio.gather()`
2. Add timeout to long-running operations
3. Implement a retry mechanism with exponential backoff

---

##### **3. Async Generators** 🔴 Priority: HIGH

**Your Streaming Implementation**:
```python
# Your SSE streaming function
async def handle_chat_stream(
    user_id: str,
    message: str,
    conversation_id: Optional[str],
    session: Session,
) -> AsyncGenerator[str, None]:
    
    async for event in streamed.stream_events():
        if event.type == "raw_response_event":
            text_delta = event.data
            yield json.dumps({'type': 'token', 'content': text_delta})
```

**What to Learn**:
- [ ] Regular generators (`yield`)
- [ ] Async generators (`async for`, `async yield`)
- [ ] `AsyncGenerator[T, Y]` type hint
- [ ] Memory-efficient streaming
- [ ] Backpressure handling
- [ ] When to use generators vs lists

**Resources**:
- [Python Generators - Real Python](https://realpython.com/introduction-to-python-generators/)
- [Async Generators PEP](https://www.python.org/dev/peps/pep-0525/)

**Practice Exercises**:
1. Write a generator that yields numbers 1-100
2. Convert it to an async generator
3. Build a streaming file reader using async generators

---

#### **Week 3: Python Best Practices**

##### **1. Error Handling** 🟡 Priority: HIGH

**Your Current Pattern**:
```python
try:
    result =n()
except Exception as e:
    logger.error(f"Agent error: {e}", exc_info=True)
    yield json.dumps({'type': 'error', 'content': str(e)})
```

**What to Learn**:
- [ ] `try/except/else/finally` blocks
- [ ] Custom exception classes
- [ ] Exception chaining (`raise await agent.ru ... from ...`)
- [ ] When to catch vs when to let propagate
- [ ] Logging exceptions properly (`exc_info=True`)
- [ ] Creating exception hierarchies

**Resources**:
- [Python Exception Handling - Real Python](https://realpython.com/python-exceptions/)

**Practice Exercises**:
1. Create custom exceptions: `TaskNotFoundError`, `UnauthorizedError`
2. Add proper error handling to all your endpoints
3. Implement exception handlers for common errors

---

##### **2. Logging Best Practices** 🟡 Priority: MEDIUM

**Your Current Logging**:
```python
logger.info(f"Chat request from user {user_id}: {message[:50]}...")
logger.debug(f"Conversation ID: {conversation.id}")
logger.error(f"Agent error: {e}", exc_info=True)
```

**What to Learn**:
- [ ] Logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [ ] Structured logging (JSON format)
- [ ] Log handlers and formatters
- [ ] Performance impact of logging
- [ ] Security (don't log sensitive data)
- [ ] Log aggregation and analysis

**Resources**:
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Structlog Documentation](https://www.structlog.org/)

**Practice Exercises**:
1. Add JSON logging to your backend
2. Create different log formats for dev vs production
3. Add request ID tracking across log entries

---

##### **3. Code Organization** 🟡 Priority: MEDIUM

**Your Current Structure**:
```
src/
  ├── routers/      # API endpoints
  ├── services/     # Business logic
  ├── repositories/ # Data access
  └── models/       # Database models
```

**What to Learn**:
- [ ] Layered architecture (Clean Architecture)
- [ ] Separation of concerns
- [ ] Dependency injection patterns
- [ ] Module and package organization
- [ ] Import cycles and how to avoid them
- [ ] Code cohesion and coupling

**Resources**:
- Book: "Architecture Patterns with Python" (Free online)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

**Practice Exercises**:
1. Document why your architecture is organized this way
2. Identify any violations of layer boundaries
3. Refactor a messy module to follow clean architecture

---

### **Phase 2: FastAPI Deep Dive** (3-4 weeks)
*Master the framework you're using*

---

#### **Week 4: FastAPI Fundamentals**

##### **1. Request/Response Lifecycle** 🔴 Priority: HIGH

**Your Endpoint**:
```python
@router.post("/chat")
@limiter.limit("20/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    user_id: CurrentUser,
    session: DbSession,
):
    response = await handle_chat(...)
    return response
```

**What to Learn**:
- [ ] How FastAPI processes requests (step by step)
- [ ] Middleware stack (order matters!)
- [ ] Dependency injection execution order
- [ ] Request validation (Pydantic)
- [ ] Response serialization
- [ ] Starlette under FastAPI

**Resources**:
- [FastAPI Documentation](https://fastapi.tiangolo.com/tutorial/)
- [Starlette Documentation](https://www.starlette.io/)

**Practice Exercises**:
1. Add custom middleware that logs request duration
2. Create a dependency that validates custom headers
3. Add response compression for large responses

---

##### **2. Path Operations & Routers** 🟡 Priority: MEDIUM

**Your Router Setup**:
```python
router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(...):
    pass

@router.get("/chat/history/{conversation_id}")
async def get_history(...):
    pass
```

**What to Learn**:
- [ ] `APIRouter` vs `FastAPI` app
- [ ] Path parameters (`{id}`)
- [ ] Query parameters (`?limit=50`)
- [ ] Request body vs form data
- [ ] File uploads
- [ ] Response models and status codes

**Resources**:
- [FastAPI Path Operations](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)

**Practice Exercises**:
1. Add file upload endpoint for task attachments
2. Implement pagination with query parameters
3. Add different response models for different status codes

---

##### **3. Request & Response Models** 🟡 Priority: MEDIUM

**Your Pydantic Schemas**:
```python
class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's natural language message"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID"
    )
```

**What to Learn**:
- [ ] Pydantic `BaseModel`
- [ ] Field validation (`min_length`, `max_length`, `regex`)
- [ ] Nested models
- [ ] Custom validators (`@validator`, `@field_validator`)
- [ ] Response models (exclude fields, aliases)
- [ ] Model inheritance

**Resources**:
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)

**Practice Exercises**:
1. Add custom validator for email format
2. Create nested request models
3. Exclude sensitive fields from response models

---

#### **Week 5: Dependency Injection**

##### **1. FastAPI Dependencies** 🔴 Priority: HIGH

**Your Dependencies**:
```python
from fastapi import Depends
from typing import Annotated

CurrentUser = Annotated[str, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_session)]

async def chat(
    user_id: CurrentUser,
    session: DbSession,
):
    pass
```

**What to Learn**:
- [ ] What is dependency injection?
- [ ] `Depends()` function
- [ ] Dependency graph (dependencies can have dependencies)
- [ ] Yield dependencies (for cleanup)
- [ ] Testing with dependency overrides
- [ ] Dependency caching

**Resources**:
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Advanced Dependencies](https://fastapi.tiangolo.com/advanced/dependencies/)

**Practice Exercises**:
1. Create a dependency that requires authentication
2. Build a pagination dependency
3. Override dependencies in tests

---

##### **2. Building Reusable Dependencies** 🟡 Priority: MEDIUM

**Your Auth Dependency**:
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = credentials.credentials
    payload = verify_jwt(token)
    user_id = payload.get("sub")
    return user_id
```

**What to Learn**:
- [ ] Class-based dependencies
- [ ] Dependency caching (same dependency called multiple times)
- [ ] Sub-dependencies
- [ ] Dependency security patterns
- [ ] Optional dependencies

**Resources**:
- [Advanced Dependencies](https://fastapi.tiangolo.com/advanced/dependencies/)

**Practice Exercises**:
1. Create a class-based dependency for pagination
2. Build a dependency that requires another dependency
3. Create an optional dependency with default values

---

##### **3. Database Session Management** 🔴 Priority: HIGH

**Your Session Dependency**:
```python
def get_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()  # Always close!
```

**What to Learn**:
- [ ] Why yield instead of return?
- [ ] Resource cleanup in dependencies
- [ ] Session per request pattern
- [ ] Transaction management
- [ ] Connection pooling
- [ ] Session isolation

**Resources**:
- [SQLAlchemy Session Management](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [FastAPI Database Dependencies](https://fastapi.tiangolo.com/tutorial/sql-databases/)

**Practice Exercises**:
1. Add transaction rollback on error
2. Implement connection pooling
3. Create a dependency that manages transaction lifecycle

---

#### **Week 6: Advanced FastAPI**

##### **1. Middleware** 🟡 Priority: MEDIUM

**Your Middleware Stack**:
```python
# Order matters! First added = outermost layer
app.middleware("http")(logging_middleware)      # 1. Log + X-Process-Time
app.middleware("http")(error_handler_middleware) # 2. Handle errors
configure_cors(app)                              # 3. CORS
app.add_middleware(GZipMiddleware, minimum_size=500)  # 4. Compress
```

**What to Learn**:
- [ ] What is middleware?
- [ ] Middleware execution order
- [ ] Writing custom middleware
- [ ] CORS middleware configuration
- [ ] Performance impact of middleware
- [ ] BaseHTTPMiddleware vs @app.middleware

**Resources**:
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Starlette Middleware](https://www.starlette.io/middleware/)

**Practice Exercises**:
1. Add request timing middleware
2. Create middleware that adds custom headers
3. Implement request ID tracking middleware

---

##### **2. Background Tasks** 🔴 Priority: MEDIUM

**What You Could Use**:
```python
from fastapi import BackgroundTasks

async def send_email(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email_task, email)
    return {"message": "Email will be sent"}
```

**What to Learn**:
- [ ] When to use background tasks
- [ ] `BackgroundTasks` vs Celery
- [ ] Task queues (Redis, RabbitMQ)
- [ ] Email sending, file processing
- [ ] Error handling in background tasks

**Resources**:
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Celery Documentation](https://docs.celeryq.dev/)

**Practice Exercises**:
1. Add email notification feature using background tasks
2. Implement file processing in background
3. Set up Celery for heavy background processing

---

##### **3. WebSockets & SSE** 🟡 Priority: MEDIUM

**Your SSE Implementation**:
```python
from sse_starlette.sse import EventSourceResponse

@router.post("/chat/stream")
async def chat_stream(...):
    async def event_generator():
        async for chunk in handle_chat_stream(...):
            yield chunk
    return EventSourceResponse(event_generator())
```

**What to Learn**:
- [ ] WebSockets vs SSE vs HTTP polling
- [ ] When to use each
- [ ] SSE protocol details
- [ ] WebSocket bidirectional communication
- [ ] Connection management
- [ ] Handling disconnections

**Resources**:
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [SSE Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)

**Practice Exercises**:
1. Add WebSocket endpoint for real-time updates
2. Implement connection heartbeat
3. Add reconnection logic on client side

---

##### **4. Testing FastAPI Apps** 🟡 Priority: HIGH

**Your Test Structure**:
```python
def test_chat_with_valid_jwt(client, mock_auth):
    response = client.post("/api/chat", json={"message": "test"})
    assert response.status_code == 200
```

**What to Learn**:
- [ ] `TestClient` for testing
- [ ] Dependency overrides in tests
- [ ] Mocking external services
- [ ] Async test functions
- [ ] Test coverage measurement
- [ ] Integration vs unit tests

**Resources**:
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Documentation](https://docs.pytest.org/)

**Practice Exercises**:
1. Write tests for all new chat endpoints
2. Mock the AI agent in tests
3. Add integration tests for full chat flow
4. Measure and improve test coverage

---

### **Phase 3: Authentication & Security** (2-3 weeks)
*Understand what protects your app*

---

#### **Week 7: Authentication Fundamentals**

##### **1. Authentication vs Authorization** 🔴 Priority: HIGH

**Concept**:
```python
# Authentication: Who are you?
user_id = get_current_user(token)

# Authorization: What can you do?
if user.role == "admin":
    delete_task(...)
```

**What to Learn**:
- [ ] Authentication (AuthN) vs Authorization (AuthZ)
- [ ] Session-based vs Token-based auth
- [ ] OAuth2 flows (Authorization Code, Client Credentials)
- [ ] Single Sign-On (SSO)
- [ ] Multi-Factor Authentication (MFA)
- [ ] Password hashing (bcrypt, argon2)

**Resources**:
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- Book: "Web Security for Developers"

**Practice Exercises**:
1. Document your current auth flow
2. Add role-based authorization
3. Implement password reset flow

---

##### **2. JWT Deep Dive** 🔴 Priority: HIGH

**Your JWT Verification**:
```python
def verify_jwt(token: str) -> Dict[str, any]:
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
    )
    return payload
```

**What to Learn**:
- [ ] JWT structure (header, payload, signature)
- [ ] Signing algorithms (HS256, RS256, EdDSA)
- [ ] JWKS (JSON Web Key Set)
- [ ] Token expiration and refresh
- [ ] Security considerations
- [ ] Common JWT vulnerabilities

**Resources**:
- [JWT.io Introduction](https://jwt.io/introduction)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)

**Practice Exercises**:
1. Implement token refresh flow
2. Add token blacklisting for logout
3. Audit your JWT implementation for vulnerabilities

---

##### **3. Better Auth Internals** 🔴 Priority: MEDIUM

**Your Configuration**:
```python
auth = betterAuth({
    database: pool,
    emailAndPassword: { enabled: true },
    plugins: [jwt()],
})
```

**What to Learn**:
- [ ] How Better Auth works internally
- [ ] User session management
- [ ] Password hashing (bcrypt, argon2)
- [ ] Email verification flow
- [ ] Plugin system
- [ ] Security features

**Resources**:
- [Better Auth Documentation](https://www.better-auth.com/)
- Read Better Auth source code on GitHub

**Practice Exercises**:
1. Read Better Auth source code
2. Add custom Better Auth plugin
3. Implement email verification

---

#### **Week 8: Security Best Practices**

##### **1. Common Vulnerabilities** 🔴 Priority: HIGH

**What to Learn**:
- [ ] SQL Injection (you're safe with SQLModel)
- [ ] XSS (Cross-Site Scripting)
- [ ] CSRF (Cross-Site Request Forgery)
- [ ] Rate limiting bypass
- [ ] JWT vulnerabilities
- [ ] Session fixation

**Resources**:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)

**Practice Exercises**:
1. Audit your code for vulnerabilities
2. Add CSRF protection
3. Implement security headers

---

##### **2. Input Validation & Sanitization** 🟡 Priority: MEDIUM

**Your Validation**:
```python
message: str = Field(..., min_length=1, max_length=5000)
```

**What to Learn**:
- [ ] Why validate input?
- [ ] Server-side vs client-side validation
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (escaping output)
- [ ] File upload security
- [ ] Content-Type validation

**Resources**:
- [Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

**Practice Exercises**:
1. Add input sanitization for all user inputs
2. Validate Content-Type headers
3. Implement file upload security

---

##### **3. Rate Limiting** 🟡 Priority: LOW

**Your Rate Limiting**:
```python
@limiter.limit("20/minute")
async def chat(...):
    pass
```

**What to Learn**:
- [ ] Why rate limiting?
- [ ] Algorithms (token bucket, sliding window)
- [ ] Distributed rate limiting (Redis)
- [ ] Bypass techniques and prevention
- [ ] User-friendly error messages

**Resources**:
- [SlowAPI Documentation](https://slowapi.readthedocs.io/)

**Practice Exercises**:
1. Implement custom rate limit strategy
2. Add Redis-based distributed rate limiting
3. Create rate limit bypass for trusted IPs

---

### **Phase 4: Database & ORM** (2-3 weeks)
*Master data persistence*

---

#### **Week 9: SQLModel & SQLAlchemy**

##### **1. SQLModel Fundamentals** 🔴 Priority: HIGH

**Your Models**:
```python
class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=utc_now)
```

**What to Learn**:
- [ ] SQLModel vs SQLAlchemy vs Pydantic
- [ ] Table definition with models
- [ ] Field types and constraints
- [ ] Primary keys, foreign keys
- [ ] Indexes for performance
- [ ] Default values and factories

**Resources**:
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

**Practice Exercises**:
1. Design schema for a new feature
2. Add indexes for frequently queried fields
3. Create composite primary keys

---

##### **2. Relationships** 🟡 Priority: MEDIUM

**Your Relationships**:
```python
class Conversation(SQLModel, table=True):
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

**What to Learn**:
- [ ] One-to-many relationships
- [ ] Many-to-many relationships (your Task-Tag)
- [ ] One-to-one relationships
- [ ] Lazy loading vs eager loading
- [ ] Cascade deletes
- [ ] Self-referential relationships

**Resources**:
- [SQLModel Relationships](https://sqlmodel.tiangolo.com/tutorial/relationships/)

**Practice Exercises**:
1. Add many-to-many relationship
2. Implement cascade deletes
3. Add self-referential relationship (e.g., parent task)

---

##### **3. Query Building** 🔴 Priority: HIGH

**Your Queries**:
```python
statement = (
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
)
conversations = session.exec(statement).all()
```

**What to Learn**:
- [ ] `select()`, `insert()`, `update()`, `delete()`
- [ ] Filtering with `where()`
- [ ] Joins (inner, outer, left, right)
- [ ] Aggregations (COUNT, SUM, AVG)
- [ ] Subqueries
- [ ] Raw SQL when needed

**Resources**:
- [SQLAlchemy Core Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)

**Practice Exercises**:
1. Write complex queries with joins
2. Add aggregations (count conversations per user)
3. Optimize slow queries

---

#### **Week 10: Advanced Database**

##### **1. Transactions** 🔴 Priority: HIGH

**Current Pattern**:
```python
with Session(engine) as session:
    try:
        session.add(task)
        session.commit()
    except:
        session.rollback()
        raise
```

**What to Learn**:
- [ ] ACID properties
- [ ] Transaction isolation levels
- [ ] Savepoints
- [ ] Deadlocks and prevention
- [ ] Optimistic vs pessimistic locking
- [ ] Nested transactions

**Resources**:
- [SQLAlchemy Transactions](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)

**Practice Exercises**:
1. Add explicit transactions to multi-step operations
2. Implement optimistic locking
3. Handle deadlocks gracefully

---

##### **2. Database Performance** 🟡 Priority: MEDIUM

**What to Learn**:
- [ ] Query optimization
- [ ] Index strategies
- [ ] N+1 query problem
- [ ] Connection pooling
- [ ] Database monitoring
- [ ] Query profiling

**Resources**:
- Book: "High Performance MySQL" (concepts apply to PostgreSQL)

**Practice Exercises**:
1. Identify and fix N+1 queries
2. Add missing indexes
3. Set up query logging and monitoring

---

##### **3. Database Migrations** 🔴 Priority: HIGH

**What to Learn**:
- [ ] Why migrations?
- [ ] Alembic setup and configuration
- [ ] Creating migration files
- [ ] Upgrading/downgrading
- [ ] Data migrations
- [ ] Migration testing

**Resources**:
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

**Practice Exercises**:
1. Set up Alembic for your project
2. Create migration for new models
3. Write data migration script

---

### **Phase 5: MCP & AI Integration** (2 weeks)
*Understand the AI agent system*

---

#### **Week 11: MCP Protocol**

##### **1. MCP Fundamentals** 🔴 Priority: MEDIUM

**What to Learn**:
- [ ] What is Model Context Protocol?
- [ ] MCP architecture (client, server, tools)
- [ ] JSON-RPC 2.0 protocol
- [ ] Tool discovery and invocation
- [ ] Security considerations
- [ ] Error handling in MCP

**Resources**:
- [MCP Specification](https://modelcontextprotocol.io/)
- Your own `mcp_server/` code!

**Practice Exercises**:
1. Document your MCP architecture
2. Add new MCP tool
3. Implement MCP tool testing

---

##### **2. Building MCP Servers** 🟡 Priority: MEDIUM

**Your MCP Server**:
```python
@mcp.tool(name="add_task")
async def add_task(user_id: str, title: str) -> str:
    result = _add_task(user_id=user_id, title=title)
    return json.dumps(result)
```

**What to Learn**:
- [ ] Tool definition and annotations
- [ ] Error handling in tools
- [ ] Tool security (input validation, user isolation)
- [ ] Testing MCP tools
- [ ] Performance optimization
- [ ] Tool versioning

**Resources**:
- Your `backend/MCP_SETUP_GUIDE.md`

**Practice Exercises**:
1. Add comprehensive error handling to tools
2. Implement tool-level rate limiting
3. Write integration tests for all tools

---

#### **Week 12: AI Agent Integration**

##### **1. OpenAI Agents SDK** 🔴 Priority: MEDIUM

**Your Agent Setup**:
```python
agent = Agent(
    name="Todo Assistant",
    instructions=AGENT_SYSTEM_PROMPT,
    mcp_servers=[mcp_server],
    model=model,
)

result = await Runner.run_streamed(agent, input=messages)
```

**What to Learn**:
- [ ] Agent architecture
- [ ] System prompts and instructions
- [ ] Tool calling with MCP
- [ ] Streaming with `run_streamed()`
- [ ] Conversation management
- [ ] Error handling

**Resources**:
- [OpenAI Agents SDK Docs](https://github.com/openai/openai-agents-python)
- Your `.claude/skills/openai-agents-sdk/` files!

**Practice Exercises**:
1. Optimize your system prompt
2. Add conversation summarization
3. Implement agent fallback on errors

---

##### **2. LLM Best Practices** 🟡 Priority: LOW

**What to Learn**:
- [ ] Prompt engineering
- [ ] Context window management
- [ ] Token counting and limits
- [ ] Cost optimization
- [ ] Error handling (rate limits, timeouts)
- [ ] Model selection

**Resources**:
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

**Practice Exercises**:
1. Implement token counting
2. Add cost tracking
3. Optimize prompts for better responses

---

### **Phase 6: Production & DevOps** (Ongoing)
*Deploy and maintain your app*

---

#### **Topics to Learn**:

##### **1. Docker & Containerization**
- [ ] Dockerfile best practices
- [ ] Multi-stage builds
- [ ] Docker Compose for local development
- [ ] Container security
- [ ] Image optimization

##### **2. CI/CD**
- [ ] GitHub Actions
- [ ] Automated testing
- [ ] Automated deployment
- [ ] Rollback strategies
- [ ] Environment promotion

##### **3. Monitoring & Observability**
- [ ] Logging aggregation (ELK stack)
- [ ] Metrics (Prometheus, Grafana)
- [ ] Tracing (OpenTelemetry)
- [ ] Alerting
- [ ] Health checks

##### **4. Cloud Deployment**
- [ ] Railway, Render, or AWS
- [ ] Database hosting (Neon, Supabase)
- [ ] Environment management
- [ ] Secrets management
- [ ] Scaling strategies

---

## 📅 Weekly Study Plan

### **Sample Week Structure**

| Day | Activity | Time | Focus |
|-----|----------|------|-------|
| **Monday** | Learn new concept (video/article) | 1-2 hours | Theory |
| **Tuesday** | Hands-on practice with concept | 1-2 hours | Practice |
| **Wednesday** | Learn related concept | 1-2 hours | Theory |
| **Thursday** | Apply to your codebase | 1-2 hours | Application |
| **Friday** | Review & document learnings | 1 hour | Consolidation |
| **Weekend** | Build small project/feature | 2-3 hours | Project |

**Total**: 8-12 hours per week

---

## 🎯 Success Metrics

After completing this roadmap, you should be able to:

- [ ] Explain how every line of your backend works
- [ ] Debug any issue without help
- [ ] Add new features confidently
- [ ] Review others' FastAPI code
- [ ] Explain JWT authentication clearly
- [ ] Optimize database queries
- [ ] Implement proper error handling
- [ ] Write comprehensive tests
- [ ] Deploy to production safely
- [ ] Mentor others on these topics

---

## 📚 Learning Resources

### **Free Resources**

| Topic | Resource | Link |
|-------|----------|------|
| **FastAPI** | Official Tutorial | https://fastapi.tiangolo.com/tutorial/ |
| **SQLModel** | Official Docs | https://sqlmodel.tiangolo.com/ |
| **Pydantic** | Official Docs | https://docs.pydantic.dev/ |
| **Python Async** | Real Python | https://realpython.com/async-io-python/ |
| **OWASP** | Top 10 | https://owasp.org/www-project-top-ten/ |
| **Python Types** | Real Python | https://realpython.com/python-type-checking/ |
| **Decorators** | Real Python | https://realpython.com/primer-on-python-decorators/ |

### **Paid Resources** (Optional)

| Resource | Price | Worth It? |
|----------|-------|-----------|
| Book: "Architecture Patterns with Python" | ~$40 | ✅ YES |
| Book: "High Performance MySQL" | ~$50 | ✅ YES |
| Course: FastAPI on Udemy | ~$15 (on sale) | ⚠️ Optional |

### **Practice Platforms**

- **Exercism**: Python track (free)
- **LeetCode**: Python problems (free/paid)
- **Your own codebase**: Best learning tool! (free)

---

## 🚀 Immediate Next Steps

1. **Start with Phase 1, Week 1** (Type Hints & Decorators)
2. **Apply immediately** to your codebase
3. **Document questions** as you learn in a learning journal
4. **Ask for clarification** when stuck
5. **Build something new** each week to practice

---

## 📝 How to Use This Roadmap

1. **Don't rush** - Take 3-4 months to complete everything
2. **Focus on understanding** - Not just copying code
3. **Apply immediately** - Use what you learn in your project
4. **Document your journey** - Keep notes of what you learn
5. **Revisit topics** - Some concepts need multiple passes
6. **Ask questions** - When stuck, research or ask for help

---

## 🎉 Final Notes

**Remember**:
- Learning is a marathon, not a sprint
- You're already ahead by having built this much
- It's okay to not understand everything immediately
- Practice consistently (even 1 hour/day is enough)
- Build projects to reinforce learning

**Your Advantage**:
- You have a real codebase to practice on
- You can see immediate application of concepts
- You're learning in context (not abstract)

**Good luck on your learning journey!** 🚀

---

**Last Updated**: 2026-03-31  
**Current Level**: Intermediate  
**Target Level**: Advanced  
**Estimated Completion**: 12-16 weeks
