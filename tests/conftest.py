from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.database import Base
from app.dependency import get_db
from main import app

# SQLite test database connection URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create engine for the test database.
# connect_args={"check_same_thread": False} allows one connection across threads (required for SQLite).
test_engine = create_engine(TEST_DATABASE_URL,
                            connect_args={"check_same_thread": False})

# Create a session factory for the test database.
# autocommit=False: changes are not saved automatically; commit() is required.
# autoflush=False: changes are not flushed automatically on queries.
TestSessionLocal = sessionmaker(bind=test_engine,
                                autocommit=False,
                                autoflush=False)

# Dependency that provides a test database session
def get_test_db() -> Generator[Session, None, None]:
    # Create a new DB session
    db = TestSessionLocal()
    try:
        # Yield the session (FastAPI will close it after request handling)
        yield db
    finally:
        # Always close the session (even if an error occurs)
        db.close()

# Override get_db dependency for all tests
app.dependency_overrides[get_db] = get_test_db

@pytest.fixture()
def client():
    # Provide a FastAPI TestClient for HTTP requests in tests
    yield TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Recreate all tables before each test
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after each test (cleanup)
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session()-> Generator[Session, None, None]:
    # Create a new DB session
    db = TestSessionLocal()
    try:
        # Yield the session (FastAPI will close it after request handling)
        yield db
    finally:
        # Always close the session (even if an error occurs)
        db.close()

