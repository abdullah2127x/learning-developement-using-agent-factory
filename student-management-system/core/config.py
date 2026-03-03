# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     DATABASE_URL: str = "sqlite:///./student.db"

#     class Config:
#         env_file = ".env"


# settings = Settings()


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    database_url: str = ""
    api_key: str = ""
    debug: bool = False
    max_connections: int = 10
    
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
    