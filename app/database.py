# Import SQLAlchemy database helpers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database connection URL
DATABASE_URL = "sqlite:///./finance.db"

# Create database engine.
# check_same_thread=False allows SQLite to be used in a multithreaded environment.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory.
# autocommit=False means changes must be committed explicitly via commit().
# autoflush=False means changes are not flushed automatically on queries.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for all database models
Base = declarative_base()

