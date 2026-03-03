# Docker Deployment for FastAPI

Complete Docker deployment guide with Uvicorn, docker-compose, production configurations, and best practices.

## Basic Dockerfile

### Single-Stage Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app /app

# Run with Uvicorn
CMD ["fastapi", "run", "main.py", "--port", "80"]
```

### Build and Run

```bash
# Build image
docker build -t myapi .

# Run container
docker run -d -p 8000:80 --name myapi-container myapi

# View logs
docker logs myapi-container

# Stop container
docker stop myapi-container
```

---

## Multi-Stage Dockerfile (Production)

Reduces image size by separating build and runtime stages.

```dockerfile
# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser /app

# Copy installed dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application
COPY --chown=appuser:appuser ./app /app

# Set PATH for user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:80/health')" || exit 1

# Run application
CMD ["fastapi", "run", "main.py", "--port", "80", "--workers", "4"]
```

---

## Docker Compose

### Basic docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:80"
    environment:
      - DATABASE_URL=postgresql+psycopg://user:password@db:5432/mydb
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
```

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:80"
    environment:
      - DATABASE_URL=postgresql+psycopg://user:password@db:5432/mydb
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=info
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=mydb
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

### Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Remove volumes (careful!)
docker-compose down -v
```

---

## Environment Configuration

### .env File

```bash
# .env (DO NOT COMMIT)
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mydb
SECRET_KEY=use-openssl-rand-hex-32-to-generate-this
ENVIRONMENT=development
LOG_LEVEL=debug
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Production
# DATABASE_URL=postgresql+psycopg://user:password@db:5432/mydb
# ENVIRONMENT=production
# LOG_LEVEL=info
# ALLOWED_ORIGINS=https://example.com
```

### .env.example

```bash
# .env.example (COMMIT THIS)
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mydb
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
LOG_LEVEL=debug
ALLOWED_ORIGINS=http://localhost:3000
```

### Load .env in Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    env_file:
      - .env
    # Or reference specific variables
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
```

---

## Uvicorn Configuration

### Production Workers

```dockerfile
# Multiple workers (CPU-bound tasks)
CMD ["fastapi", "run", "main.py", "--port", "80", "--workers", "4"]

# Calculate workers: (2 x CPU cores) + 1
# For 2 CPUs: --workers 5
```

### Uvicorn with Custom Settings

```python
# run.py (alternative to fastapi command)
import uvicorn
from app.main import app
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=settings.workers,
        log_level=settings.log_level,
        reload=settings.environment == "development",
        access_log=True
    )
```

```dockerfile
CMD ["python", "run.py"]
```

---

## Nginx Reverse Proxy

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:80;
    }

    server {
        listen 80;
        server_name example.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name example.com;

        # SSL certificates
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options "nosniff";
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Proxy settings
        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://api/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Static files (if any)
        location /static {
            alias /app/static;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

---

## Health Checks

### Health Check Endpoint

```python
# app/routers/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, text
from app.database import get_session

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/health/db")
async def health_check_db(session: Session = Depends(get_session)):
    try:
        # Test database connection
        session.exec(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
```

### Docker Healthcheck

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1
```

---

## Database Migrations in Docker

### Run Migrations on Startup

```dockerfile
# Option 1: In Dockerfile
CMD alembic upgrade head && fastapi run main.py --port 80
```

```bash
# Option 2: In docker-compose with init service
services:
  migration:
    build: .
    command: alembic upgrade head
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      db:
        condition: service_healthy

  api:
    build: .
    depends_on:
      migration:
        condition: service_completed_successfully
```

### Migration Script

```bash
#!/bin/bash
# entrypoint.sh

# Wait for database
echo "Waiting for database..."
while ! pg_isready -h db -p 5432 -U user; do
  sleep 1
done

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Start application
echo "Starting application..."
exec fastapi run main.py --port 80 --workers 4
```

```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

---

## Secrets Management

### Docker Secrets (Swarm)

```yaml
version: '3.8'

services:
  api:
    image: myapi:latest
    secrets:
      - db_password
      - secret_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - SECRET_KEY_FILE=/run/secrets/secret_key

secrets:
  db_password:
    external: true
  secret_key:
    external: true
```

### Load Secrets in Application

```python
# app/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    secret_key: str

    def __init__(self, **kwargs):
        # Load from file if specified
        if secret_file := kwargs.get("SECRET_KEY_FILE"):
            kwargs["secret_key"] = Path(secret_file).read_text().strip()
        super().__init__(**kwargs)
```

---

## Logging Configuration

Uses **structlog** for structured, context-rich logging with JSON output in production and human-readable console output in development. All logging logic lives in `app/core/logging.py`.

**Install**: `pip install structlog` (or add `structlog>=24.1.0` to dependencies)

### Core Module (`app/core/logging.py`)

```python
# app/core/logging.py
import logging
import sys

import structlog
from app.config import settings


def setup_logging() -> None:
    """Configure structlog + stdlib logging.

    - Development: colored, human-readable console output.
    - Production:  JSON lines for log aggregation (ELK, Datadog, etc.).
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Shared processors used by both structlog and stdlib loggers
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,          # request-scoped context
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.debug:
        # Dev: colored key=value output
        renderer = structlog.dev.ConsoleRenderer()
    else:
        # Prod: JSON lines
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # Quiet noisy third-party loggers
    for name in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a named structlog logger. Use this instead of logging.getLogger()."""
    return structlog.get_logger(name)
```

### Request Logging Middleware (`app/middleware.py`)

Adds a unique `request_id` to every request so all logs within a request are correlated.

```python
# app/middleware.py  (add to existing middleware file)
import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger("api.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Bind request_id, method, path to structlog context for every request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        start = time.perf_counter()
        logger.info("request_started")

        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_failed")
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        response.headers["X-Request-ID"] = request_id
        return response
```

### Registration in `app/main.py`

```python
# app/main.py
from app.core.logging import setup_logging
from app.middleware import RequestLoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()               # ← initialize logging first
    create_db_and_tables()
    yield

# After app creation:
app.add_middleware(RequestLoggingMiddleware)
```

### Using Loggers in Services / Repositories

```python
# app/services/user_service.py
import structlog

logger = structlog.get_logger(__name__)

class UserService:
    def create_user(self, user_in):
        logger.info("creating_user", username=user_in.username)
        # ... business logic ...
        logger.info("user_created", user_id=user.id)
        return user
```

All logs from within a request automatically include `request_id`, `method`, `path`, and `client_ip` — no manual passing required.

### Config Settings

```python
# app/config.py  (add these fields)
class Settings(BaseSettings):
    log_level: str = "info"        # critical | error | warning | info | debug
    debug: bool = False            # True → console output, False → JSON output
```

### Environment Variables

```bash
# .env (development)
LOG_LEVEL=debug
DEBUG=true

# .env (production)
LOG_LEVEL=info
# DEBUG defaults to false → JSON output
```

### Sample Output

**Development** (`DEBUG=true`):
```
2026-03-04T10:30:00.000Z [info     ] request_started   [api.access] client_ip=127.0.0.1 method=GET path=/api/v1/users request_id=a1b2c3d4
2026-03-04T10:30:00.012Z [info     ] fetching_users     [app.services.user_service] request_id=a1b2c3d4
2026-03-04T10:30:00.045Z [info     ] request_completed  [api.access] duration_ms=45.12 status_code=200 request_id=a1b2c3d4
```

**Production** (`DEBUG=false`):
```json
{"event":"request_started","logger":"api.access","level":"info","timestamp":"2026-03-04T10:30:00.000Z","request_id":"a1b2c3d4","method":"GET","path":"/api/v1/users","client_ip":"10.0.1.5"}
{"event":"request_completed","logger":"api.access","level":"info","timestamp":"2026-03-04T10:30:00.045Z","request_id":"a1b2c3d4","status_code":200,"duration_ms":45.12}
```

---

## Production Checklist

### Security
- [ ] HTTPS enabled (SSL certificates)
- [ ] Secrets in environment variables or secrets manager
- [ ] CORS configured with explicit origins
- [ ] Security headers configured (X-Frame-Options, etc.)
- [ ] Rate limiting enabled via `utils/rate_limit.py` (Redis backend for multi-worker)
- [ ] Input validation and sanitization

### Performance
- [ ] Uvicorn workers configured (2x CPU + 1)
- [ ] Database connection pooling configured
- [ ] Static files served with caching
- [ ] Nginx reverse proxy configured
- [ ] Response compression enabled

### Reliability
- [ ] Health check endpoint implemented
- [ ] Docker healthcheck configured
- [ ] Database migrations automated
- [ ] Graceful shutdown handling
- [ ] Resource limits set (CPU, memory)
- [ ] Restart policy configured

### Observability
- [ ] Structured logging via `structlog` in `app/core/logging.py` (JSON output in prod)
- [ ] `RequestLoggingMiddleware` for request_id correlation across all logs
- [ ] Log aggregation configured (ELK, Datadog, CloudWatch, etc.)
- [ ] Metrics endpoint added
- [ ] Error tracking configured
- [ ] Performance monitoring enabled

### Deployment
- [ ] Multi-stage Dockerfile for smaller images
- [ ] Non-root user in container
- [ ] .env.example provided
- [ ] README with setup instructions
- [ ] CI/CD pipeline configured

---

## Quick Commands Reference

```bash
# Build and run
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Execute commands in container
docker-compose exec api bash
docker-compose exec db psql -U user -d mydb

# Restart services
docker-compose restart api

# Stop and remove
docker-compose down

# Scale services
docker-compose up -d --scale api=3

# Clean up
docker-compose down -v --rmi all
```
