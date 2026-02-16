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

from typing import get_type_hints

def foo(a: int, b: str):
    return a + b

print(get_type_hints(foo))

# from fastapi import FastAPI, Query

# app = FastAPI()


# @app.get("/items")
# def read_items(limit: int = Query(ge=1, le=100)):
#     return {"limit": limit}


# @app.get("/healthy")
# def health_check():
#     """Health check endpoint."""
#     return {"status": "healthy"}

# @app.get("/search")
# def search(query: str = Query("rewrewqddx",min_length=3, max_length=100)):
#     return {"query": query}
