from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.config import settings
from app.core.database import create_db_and_tables
from app.utils.rate_limit import setup_rate_limiter

# Import all models so metadata.create_all picks them up
from app.models import Course, Enrollment, Student, User  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
setup_rate_limiter(app)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
