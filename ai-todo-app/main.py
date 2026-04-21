from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.session import create_db_and_tables
from app.routers.todo import router as todo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="AI Todo App",
    description="A structured layered CRUD Todo API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(todo_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "healthy"}
