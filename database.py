from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_screener_v2.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get a DB session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Creates all database tables defined in models.py."""
    print("Initializing database and creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    print("Database tables are ready.")