# Import APIRouter to define API endpoints
from fastapi import APIRouter, Depends  # Endpoint definitions and dependency injection
from sqlalchemy.ext.asyncio import AsyncSession

# Import dependencies for DB session and auth
from app.dependency import get_db, get_current_user
from app.models import User  # Import the User model
# Import user schemas
from app.schemas import UserRequest, UserResponse
# Import the users service
from app.service import users as users_service

# Router for user-related endpoints
router = APIRouter()

@router.post("/users", response_model=UserResponse)
async def create_user(payload: UserRequest, db: AsyncSession = Depends(get_db)):  # DB session via dependency injection
    # Delegate to the service to create a new user
    return await users_service.create_user(db, payload.login)  # Pass login from the request

@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):  # Current user from auth token
    # Convert SQLAlchemy model to a Pydantic response model
    return UserResponse.model_validate(current_user)
