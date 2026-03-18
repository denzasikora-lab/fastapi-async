# Import Session for database access
from sqlalchemy.orm import Session

from app.models import User

# Find a user by login
def get_user(db: Session, login: str) -> User | None:
    # Query users table by login
    # scalar() returns a single value or None if not found
    return db.query(User).filter(User.login == login).scalar()


# Create a new user
def create_user(db: Session, login: str) -> User:
    # Create a new User instance
    user = User(login=login)
    # Add user to the DB session
    db.add(user)
    # Flush changes (without committing)
    db.flush()
    # Return created user
    return user
