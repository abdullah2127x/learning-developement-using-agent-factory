# core/database.py
from sqlmodel import Session, SQLModel, create_engine

from core.config import settings

engine = create_engine(settings.database_url)


def create_db_and_tables():
    """Create all tables based on SQLModel models."""
    SQLModel.metadata.create_all(engine)


def get_db():
    """FastAPI dependency to get a database session."""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
