# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# # from models.student import Student
# from core.config import settings
# from db.init_db import create_db_and_tables
# from routers.students import router as students_router


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Manage application lifecycle - create tables on startup."""
#     create_db_and_tables()
#     yield


# app = FastAPI(
#     title="Student Management API",
#     description="Manage student data with FastAPI and PostgreSQL",
#     version="0.1.0",
#     lifespan=lifespan,
# )

# app.include_router(students_router)


# @app.get("/health")
# def health_check():
#     """Health check endpoint."""
#     return {"status": "healthy", "debug": settings.debug}


