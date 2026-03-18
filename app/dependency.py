# Import Generator for database session generator typing
from typing import Generator

from fastapi import Depends, HTTPException  # Dependency injection and error handling
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # Bearer token auth helpers
# Import Session for database access
from sqlalchemy.orm import Session

# Import the session factory
from app.database import SessionLocal
from app.models import User  # Import the User model
from app.repository import users as users_repository  # Import user repository


# Security scheme for HTTP Bearer tokens (token is passed via the Authorization header)
security = HTTPBearer()


# Dependency that provides a database session
def get_db() -> Generator[Session, None, None]:
    # Create a new DB session
    db = SessionLocal()
    try:
        # Yield the session (FastAPI will close it after request handling)
        yield db
    finally:
        # Always close the session (even if an error occurs)
        db.close()


# Dependency that resolves the current user from the auth token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                     db: Session = Depends(get_db)) -> User:
    # Extract login from the auth token (passed via the Authorization header)
    login = credentials.credentials
    # Look up the user by login
    user = users_repository.get_user(db, login)
    # If user not found, return 401 (unauthorized)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Return the resolved user
    return user