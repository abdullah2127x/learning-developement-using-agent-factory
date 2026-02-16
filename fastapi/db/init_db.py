from sqlmodel import SQLModel
from db.engine import engine

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
