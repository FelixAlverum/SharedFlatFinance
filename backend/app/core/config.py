from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shared Flat Ledger API"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./ledger.db"
    BACKEND_CORS_ORIGINS: list[str]=["http://5.75.148.191:3055","http://localhost:3000","http://127.0.0.1:3000"]

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Ignoriert andere Variablen in der .env, die hier nicht definiert sind
    )

settings = Settings()