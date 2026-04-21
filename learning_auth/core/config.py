# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str                    # Neon connection string
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    argon2_memory_cost: int = 102400     # we tune these later
    argon2_time_cost: int = 2
    bcrypt_rounds: int = 12
    password_hasher: str = "argon2"      # default hasher
    # 
    cookie_secure: bool = False          # Set True in production (HTTPS)
    cookie_http_only: bool = True
    cookie_max_age: int = 60 * 60 * 24 * 7   # 7 days for refresh
    cookie_same_site: str = "lax"        # "strict" or "lax"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()