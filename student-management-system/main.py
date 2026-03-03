from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI

from db.engine import get_session
from db.init_db import create_tables
from models.course_model import Course
from models.student_model import Student, StudentCreate
from routers.auth_router import router as auth_router
from routers.course_router import router as course_router
from routers.student_router import public_router as student_public_router
from routers.student_router import router as student_router
from services import auth_service


@asynccontextmanager
async def get_connection(app: FastAPI):
    print("Application Startup: Initialization complete.")
    create_tables()
    yield


# app = FastAPI()
app = FastAPI(lifespan=get_connection)

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(student_public_router)
app.include_router(course_router)


# @app.middleware("http")
# async def middleware(request, call_next):
#     # student = login_service.login_user(login_data, session)
#     # return student
#     print(f"Request headers:{request.headers}")

# @app.middleware("http")
# async def middleware(request, call_next):
#     api_key = request.headers.get("api-keY")
#     if not api_key:
#         return JSONResponse(status_code=401, content={"detail": "Api key not provided"})
#     elif not api_key == "secret":
#         return JSONResponse(status_code=403, content={"detail": "Invalid API key"})
#     response = await call_next(request)
#     return response 
import asyncio

async def send_mail():
    print("Sending Mail...")
    await asyncio.sleep(12)
    print("Mail Sent!")

@app.get("/")
async def root(task: BackgroundTasks):
    task.add_task(send_mail)
    return {"message": "Hello World"}
