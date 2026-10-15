from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.models.user import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    # The get_current_user dependency has already handled all token extraction,
    # verification, database lookups, and security checks.
    # We simply return the User object, and FastAPI will automatically 
    # serialize it into JSON using the UserResponse schema (filtering out the password).
    return current_user

from app.api.dependencies.auth import get_current_admin_user

@router.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(get_current_admin_user)):
    """
    Protected endpoint only accessible to users with the is_superuser flag set to True.
    """
    return {
        "message": f"Welcome Admin! You are authenticated as {current_user.email}.",
        "status": "All systems operational"
    }

from typing import List
from app.schemas.user import SessionResponse
from app.services.session import get_user_sessions
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db

@router.get("/me/sessions", response_model=List[SessionResponse])
def get_my_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns all sessions (active and inactive) belonging to the currently authenticated user.
    """
    sessions = get_user_sessions(db, current_user.id)
    return sessions

