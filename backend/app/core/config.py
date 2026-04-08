from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shared Flat Ledger API"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./ledger.db"
    # CORS is critical! This tells the backend to accept requests from your SvelteKit frontend
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:4173"]

    class Config:
        case_sensitive = True

settings = Settings()