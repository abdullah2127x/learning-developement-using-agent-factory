
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./todo.db"
    debug: bool = False

    # Agent (OpenRouter)
    # openrouter_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""


settings = Settings()


