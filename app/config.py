from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/freebies_app")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Email settings for password reset
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "your-app-password")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "your-email@gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_TLS: bool = os.getenv("MAIL_TLS", "True").lower() == "true"
    MAIL_SSL: bool = os.getenv("MAIL_SSL", "False").lower() == "true"
    
    # Frontend URL for password reset
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8081")

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 