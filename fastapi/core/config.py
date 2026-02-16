
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

# Settings
class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    database_url: str
    debug: bool = False

settings = Settings()
