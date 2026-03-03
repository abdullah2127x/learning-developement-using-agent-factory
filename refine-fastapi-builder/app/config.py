from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    log_level: str = "info"
    debug: bool = False
    project_name: str = "Student Course Management API"
    api_v1_prefix: str = "/api/v1"


settings = Settings()
