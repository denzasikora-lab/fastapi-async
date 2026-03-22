from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException  # Dependency injection and error handling
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # Bearer token auth helpers
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.models import User  # Import the User model
from app.repository import users as users_repository  # Import user repository


# Security scheme for HTTP Bearer tokens (token is passed via the Authorization header)
security = HTTPBearer()


# Dependency that provides a database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db: AsyncSession = SessionLocal()
    try:
        # Yield the session (FastAPI will close it after request handling)
        yield db
    finally:
        # Always close the session (even if an error occurs)
        await db.close()


# Dependency that resolves the current user from the auth token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    # Extract login from the auth token (passed via the Authorization header)
    login = credentials.credentials
    # Look up the user by login
    user = await users_repository.get_user(db, login)
    # If user not found, return 401 (unauthorized)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Return the resolved user
    return user