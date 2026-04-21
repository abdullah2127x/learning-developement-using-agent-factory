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























from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException  # Important for full control 


app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle all HTTPException (404, 400, 401, etc.) raised with raise HTTPException(...)"""
    print(f"Request is : {request.url} and  EXC: {exc} )")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "HTTPException",
                "message": exc.detail if isinstance(exc.detail, str) else exc.detail,
                "status_code": exc.status_code
            }
        }
    )

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Item ID must be positive"
        )
    if item_id == 999:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Item not found",
                "suggestion": "Try IDs between 1 and 100"
            }
        )
    return {"item_id": item_id}