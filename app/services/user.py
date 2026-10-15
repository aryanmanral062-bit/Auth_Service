from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """Fetch a user from the database by email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """
    Hashes the user's password and saves the new user to the database.
    """
    hashed_password = get_password_hash(user.password)
    
    # Create the SQLAlchemy model instance
    db_user = User(
        email=user.email,
        hashed_password=hashed_password
    )
    
    # Add to session, commit to DB, and refresh to get the generated ID
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user by verifying their email and password.
    Returns the user object if successful, or None if authentication fails.
    """
    from app.core.security import verify_password
    
    user = get_user_by_email(db, email)
    if not user:
        return None
        
    if not verify_password(password, user.hashed_password):
        return None
        
    return user


