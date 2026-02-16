from sqlmodel import create_engine, Session
from core.config import settings

# Database setup
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)


def get_session():
    with Session(engine) as session:
        yield session





# # Database setup
# engine = create_async_engine(
#     settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
#     echo=settings.debug,
#     max_overflow=settings.max_connections,
# )

# async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# async def get_session() -> AsyncGenerator[AsyncSession, None]:
#     """Dependency for getting database session."""
#     async with async_session() as session:
#         yield session
