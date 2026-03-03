from core.config import settings
from sqlmodel import SQLModel, create_engine, Session

engine = create_engine(settings.database_url, echo=True)



def get_session():
    with Session(engine) as session:
        yield session