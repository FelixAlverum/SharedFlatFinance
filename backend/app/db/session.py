from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# The connect_args are specific to SQLite to allow multiple threads to access it
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the base class all our future database models will inherit from
Base = declarative_base()

# A helper function to yield database sessions to our API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()