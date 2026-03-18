# Import HTTPException for HTTP error handling
from fastapi import HTTPException
# Import Session for database access
from sqlalchemy.orm import Session
# Import user repository
from app.repository import users as users_repository
# Import response schema
from app.schemas import UserResponse


def create_user(db: Session, login: str) -> UserResponse:
    """
    Create a new user, checking for duplicates.
    
    Args:
        db: Database session
        login: New user's login
        
    Returns:
        Information about the created user
        
    Raises:
        HTTPException: If a user with the same login already exists
    """
    # Ensure a user with this login does not already exist
    if users_repository.get_user(db, login):
        raise HTTPException(status_code=400, detail="User already exists")  # Duplicate user -> 400

    # Create a new user via the repository
    user = users_repository.create_user(db, login)
    # Persist changes
    db.commit()
    # Convert SQLAlchemy model to a Pydantic response model
    return UserResponse.model_validate(user)