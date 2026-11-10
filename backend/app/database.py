"""SQLAlchemy engine and session utilities.

All ORM models should inherit from the `Base` declared here.
The SQLite file lives in the project root (`backend/app/app.db`).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Create engine – echo disabled for production, enable for debugging if needed
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

