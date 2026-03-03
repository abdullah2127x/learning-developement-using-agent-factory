# database.py

from sqlmodel import create_engine
from .config import settings

# Replace with your real Neon database URL
DATABASE_URL = settings.database_url

# Engine = connection to the database
engine = create_engine(DATABASE_URL, echo=True)

