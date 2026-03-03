from pydantic_settings import BaseSettings 

class Settings(BaseSettings): 

    database_url: str = 'xxx'  # will be read from `my_prefix_auth_key`
    
    class Config:
        env_file = ".env"

    
settings = Settings() 