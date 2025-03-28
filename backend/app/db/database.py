# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import re
import pathlib

# Get database URL from environment or use SQLite default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Connection pool settings
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # 30 minutes

# Create SQLAlchemy engine with appropriate arguments based on database type
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# For SQLite, check if we should reset the database
if DATABASE_URL.startswith("sqlite"):
    # Extract the database path
    match = re.search(r'sqlite:///(.+)', DATABASE_URL)
    if match:
        db_path = match.group(1)
        if db_path.startswith('./'):
            db_path = db_path[2:]  # Remove leading ./ if present
        # Check if the database file exists and remove it if RESET_DB=true
        if os.getenv("RESET_DB", "false").lower() == "true":
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
                    print(f"Database file {db_path} removed for reset")
            except Exception as e:
                print(f"Error removing database file: {e}")

# Configure pooling for all database types except SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT,
        pool_recycle=POOL_RECYCLE,
        echo=os.getenv("DB_ECHO", "false").lower() == "true"
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
