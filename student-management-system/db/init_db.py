from sqlmodel import SQLModel

from .engine import engine



def create_tables():
    SQLModel.metadata.create_all(engine)
