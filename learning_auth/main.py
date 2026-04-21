from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.database import create_db_and_tables
from routers import auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-nextjs-app.vercel.app"],
    allow_credentials=True,      # required for httpOnly cookies later
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/test")
async def health_check(req:Request):
    print("Headers:", req.headers)
    return {"message": "Health check passed!"}
