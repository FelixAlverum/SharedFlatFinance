from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
from app.core.config import settings

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# --- ENGINE SETUP ---
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.SQLALCHEMY_DATABASE_URI else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """
    Die neue Basisklasse für alle Modelle. 
    Ersetzt das veraltete 'declarative_base()'.
    """
    pass

def get_db() -> Generator:
    """
    Helper für FastAPI 'Depends'. 
    Stellt sicher, dass die Session nach dem Request geschlossen wird.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()