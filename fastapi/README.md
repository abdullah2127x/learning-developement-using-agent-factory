# Student Management API

A production-ready FastAPI application for managing student records with PostgreSQL.

## Features

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Search and filtering by name and grade
- ✅ Pagination support
- ✅ Request validation with Pydantic
- ✅ Comprehensive error handling
- ✅ SQLModel ORM integration
- ✅ PostgreSQL database
- ✅ Pytest test suite
- ✅ Docker containerization
- ✅ Interactive API documentation (Swagger UI)

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL (or use Neon as configured)
- uv package manager (or pip)

### Local Development Setup

1. **Install dependencies:**

```bash
uv sync
```

2. **Set up environment variables:**

The `.env` file is already configured with a Neon PostgreSQL database URL. If you want to use local PostgreSQL, update `.env`:

```bash
DATABASE_URL='postgresql+psycopg://user:password@localhost/students'
DEBUG=true
```

3. **Run the application:**

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

4. **Access API documentation:**

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running Tests

```bash
pytest test_main.py -v

# With coverage
pytest test_main.py --cov=. --cov-report=html
```

## Docker Deployment

### Using Docker Compose (Recommended for Local)

```bash
docker-compose up -d
```

This starts:
- FastAPI app at `http://localhost:8000`
- PostgreSQL database at `localhost:5432`

### Using Docker Only

```bash
docker build -t student-api .
docker run -p 8000:8000 -e DATABASE_URL='postgresql://...' student-api
```

## API Endpoints

### Students

**Create Student**
```
POST /students
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "grade": 10
}
```

**List Students** (with optional filtering)
```
GET /students?offset=0&limit=100&name=john&grade=10
```

**Get Student by ID**
```
GET /students/{student_id}
```

**Update Student**
```
PUT /students/{student_id}
Content-Type: application/json

{
  "name": "Jane Doe",
  "grade": 11
}
```

**Delete Student**
```
DELETE /students/{student_id}
```

### Health

**Health Check**
```
GET /health
```

## Database Schema

### Students Table

```sql
CREATE TABLE students (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  grade INTEGER NOT NULL CHECK (grade >= 0 AND grade <= 12)
);

CREATE INDEX idx_students_name ON students(name);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_grade ON students(grade);
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid input or duplicate email
- `404 Not Found` - Student not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

Example error response:

```json
{
  "detail": "Student not found"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `DEBUG` | Enable debug mode | `false` |
| `MAX_CONNECTIONS` | Database connection pool size | `5` |
| `API_KEY` | Optional API key | `dev-key` |

## Project Structure

```
.
├── main.py              # FastAPI application and endpoints
├── test_main.py         # Pytest tests
├── pyproject.toml       # Project dependencies
├── .env                 # Environment variables
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Local development stack
└── README.md            # This file
```

## Performance Optimization

- **Connection Pooling**: Configured with `pool_pre_ping=True` to handle stale connections
- **Pagination**: Default limit of 100, max 1000 to prevent large result sets
- **Indexing**: Automatic indexes on frequently queried fields (name, email, grade)
- **Async Operations**: All endpoints use async/await for non-blocking I/O

## Security Best Practices

- ✅ Environment variables for secrets (never hardcoded)
- ✅ Input validation with Pydantic
- ✅ Response models to prevent data leaks
- ✅ Unique constraint on email
- ✅ Grade validation (0-12 range)
- ✅ HTTP status code best practices

## Troubleshooting

### Connection Issues

If you see `psycopg2.OperationalError`:

1. Verify `DATABASE_URL` in `.env` is correct
2. Test connection: `psql $DATABASE_URL`
3. For Neon: ensure your IP is whitelisted

### Duplicate Email Error

Remove the existing student first or update the email:

```bash
curl -X PUT http://localhost:8000/students/1 \
  -H "Content-Type: application/json" \
  -d '{"email": "new-email@example.com"}'
```

### Tests Failing

Clear the database and reset:

```bash
pytest test_main.py -v --tb=short
```

Tests use in-memory SQLite, so they're isolated from the main database.

## Development Notes

- The app uses SQLModel which provides both SQLAlchemy ORM and Pydantic validation
- All endpoints are async for better performance
- Error messages are user-friendly but safe (no sensitive info leaked)
- Database transactions automatically commit/rollback
- Tests cover happy paths, error cases, and edge cases

## Next Steps

- Add authentication (JWT) with `/login` endpoint
- Implement rate limiting for production
- Add database migrations with Alembic
- Set up CI/CD pipeline
- Add request/response logging
- Implement caching for GET endpoints

## License

MIT
