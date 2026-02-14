# FastAPI Builder Skill

Production-grade FastAPI skill for building APIs from hello world to enterprise scale.

## What This Skill Provides

- **Complete FastAPI knowledge** from official documentation (Context7)
- **Progressive complexity** - Hello world → Enterprise architecture
- **Tech stack focus**:
  - Database: PostgreSQL + SQLModel
  - Auth: JWT with OAuth2
  - Deployment: Docker + docker-compose
  - Testing: pytest + TestClient

## Coverage

### Core Features
- ✅ REST API endpoints (GET, POST, PUT, PATCH, DELETE)
- ✅ Request/response validation with Pydantic
- ✅ Dependency injection system
- ✅ Automatic OpenAPI docs generation
- ✅ Async-first patterns with sync fallback

### Database Integration
- ✅ PostgreSQL connection and pooling
- ✅ SQLModel ORM (table + API models)
- ✅ CRUD operations with pagination
- ✅ Database migrations with Alembic
- ✅ Async database support

### Authentication & Security
- ✅ JWT token generation and validation
- ✅ Password hashing (bcrypt/argon2)
- ✅ OAuth2 with password flow
- ✅ Scope-based authorization
- ✅ Refresh tokens
- ✅ CORS configuration
- ✅ Security best practices

### Testing
- ✅ pytest configuration
- ✅ TestClient for endpoint testing
- ✅ Database fixtures and isolation
- ✅ Authentication testing
- ✅ Coverage reporting

### Production
- ✅ Docker deployment
- ✅ docker-compose with PostgreSQL
- ✅ Multi-stage Dockerfile
- ✅ Uvicorn worker configuration
- ✅ Health checks
- ✅ Logging and monitoring
- ✅ Nginx reverse proxy

### Best Practices
- ✅ Anti-patterns to avoid
- ✅ Performance optimization
- ✅ Code organization patterns
- ✅ Security guidelines

## Usage

### Invoke the Skill

```
Use fastapi-builder skill to create a FastAPI app with user authentication
```

or

```
/fastapi-builder - create a REST API with CRUD operations
```

### What the Skill Does

1. **Gathers Context**
   - Checks existing codebase
   - Asks about project scale (hello world / small / medium / large)
   - Clarifies specific requirements

2. **Creates Project**
   - Sets up appropriate structure
   - Implements requested features
   - Adds authentication if needed
   - Configures database
   - Writes tests
   - Creates Docker deployment

3. **Ensures Quality**
   - Follows async-first patterns
   - Implements security best practices
   - Avoids documented anti-patterns
   - Includes comprehensive tests
   - Provides production-ready configuration

## Reference Files

All knowledge is embedded in the skill:

| File | Content |
|------|---------|
| `project-structure.md` | Project structures for all scales |
| `authentication.md` | Complete JWT auth implementation |
| `database.md` | PostgreSQL + SQLModel patterns |
| `testing.md` | pytest patterns and fixtures |
| `deployment.md` | Docker and production deployment |
| `anti-patterns.md` | Common mistakes to avoid |
| `performance.md` | Optimization strategies |
| `examples/` | Complete working examples |

## Examples

### Hello World

See `references/examples/hello-world.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Run:
```bash
fastapi dev hello-world.py
```

### Medium Project

See `references/examples/medium-api/` for a complete modular API with:
- User authentication (JWT)
- Database integration (SQLModel)
- CRUD operations
- Tests
- Docker deployment

### Enterprise Project

See `references/examples/enterprise-api/` for a layered architecture with:
- API versioning
- Service layer
- Repository pattern
- Comprehensive testing
- Production deployment

## Key Principles

1. **Async-first** - Use `async def` for I/O-bound operations
2. **Security by default** - JWT auth, password hashing, input validation
3. **Type safety** - Pydantic models for all inputs/outputs
4. **Test coverage** - pytest for all critical paths
5. **Production-ready** - Docker, health checks, logging

## Development Workflow

```
1. Define project scale
   ↓
2. Create structure
   ↓
3. Implement models (SQLModel)
   ↓
4. Create endpoints
   ↓
5. Add authentication
   ↓
6. Write tests
   ↓
7. Configure Docker
   ↓
8. Deploy
```

## Anti-Patterns Avoided

- ❌ No hardcoded secrets
- ❌ No blocking I/O in async functions
- ❌ No missing pagination
- ❌ No exposed sensitive data
- ❌ No SQL injection vulnerabilities
- ❌ No unvalidated inputs

See `references/anti-patterns.md` for complete list.

## Performance Optimizations

- ✅ Connection pooling
- ✅ Eager loading (no N+1 queries)
- ✅ Response caching
- ✅ Background tasks
- ✅ Uvicorn workers
- ✅ Pagination
- ✅ Async HTTP clients

See `references/performance.md` for complete guide.

## Sources

All knowledge gathered from official FastAPI documentation via Context7 MCP:
- Library ID: `/websites/fastapi_tiangolo`
- Benchmark Score: 96.8
- Code Snippets: 12,277
- Source Reputation: High

No assumed knowledge - everything verified against official docs.

## Skill Metadata

- **Name**: fastapi-builder
- **Type**: Builder
- **Domain**: FastAPI web framework
- **Tech Stack**: FastAPI, PostgreSQL, SQLModel, JWT, Docker
- **Coverage**: Hello World → Enterprise
- **Documentation**: Comprehensive references embedded
- **Testing**: pytest-based
- **Production**: Docker-ready

## Version

Created: 2026-02-08
Based on: FastAPI official documentation (2026)
Python: 3.9+ (3.10+ for `|` union syntax)
