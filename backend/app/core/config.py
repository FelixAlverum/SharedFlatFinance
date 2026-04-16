from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shared Flat Ledger API"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./ledger.db"
    BACKEND_CORS_ORIGINS=["http://wilhelm-teiler-2.local:8555", "http://localhost:8555", "http://192.168.178.50:8555, http://localhost:8000"]

    SECRET_KEY: str = "KurtKoerberSchluesselInDieKassenbuecherDerWG"
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