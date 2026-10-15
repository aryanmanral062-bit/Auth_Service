from sqlalchemy.orm import Session
from app.models.session import Session as SessionModel
from app.core.security import get_token_hash
from datetime import datetime, timedelta, timezone
from app.core.jwt_utility import REFRESH_TOKEN_EXPIRE_DAYS

def create_user_session(db: Session, user_id: int, refresh_token: str, ip_address: str = None, user_agent: str = None):
    """
    Hashes the refresh token and stores the session record in the database.
    """
    hashed_token = get_token_hash(refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_session = SessionModel(
        user_id=user_id,
        refresh_token=hashed_token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session

def get_active_session_by_token(db: Session, refresh_token: str):
    """
    Finds an active session using the hashed refresh token.
    """
    hashed_token = get_token_hash(refresh_token)
    return db.query(SessionModel).filter(
        SessionModel.refresh_token == hashed_token,
        SessionModel.is_active == True
    ).first()

def update_session_last_used(db: Session, session: SessionModel):
    """
    Updates the last_used_at timestamp of a session.
    """
    session.last_used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session

def revoke_session(db: Session, session: SessionModel):
    """
    Marks a specific session as inactive (used for logout).
    """
    session.is_active = False
    db.commit()
    db.refresh(session)
    return session

def revoke_all_user_sessions(db: Session, user_id: int):
    """
    Marks all active sessions for a specific user as inactive (used for logout all).
    """
    db.query(SessionModel).filter(
        SessionModel.user_id == user_id,
        SessionModel.is_active == True
    ).update({"is_active": False}, synchronize_session=False)
    
    db.commit()

def get_user_sessions(db: Session, user_id: int):
    """
    Returns all sessions belonging to a specific user.
    """
    return db.query(SessionModel).filter(SessionModel.user_id == user_id).all()

