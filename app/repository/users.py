from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User

# Find a user by login
async def get_user(db: AsyncSession, login: str) -> User | None:
    stmt = select(User).where(User.login == login)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# Create a new user
async def create_user(db: AsyncSession, login: str) -> User:
    # Create a new User instance
    user = User(login=login)
    # Add user to the DB session
    db.add(user)
    # Flush changes (without committing)
    await db.flush()
    # Return created user
    return user
