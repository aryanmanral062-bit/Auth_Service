from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse
from app.services import user as user_service
from app.api.dependencies.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # 1. Check if the user already exists
    existing_user = user_service.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Hash the password and save the user
    new_user = user_service.create_user(db=db, user=user)
    
    # 3. Return the created user object (FastAPI filters out the password via UserResponse)
    return new_user

from app.schemas.user import UserLogin, TokenResponse
from app.core.jwt_utility import create_access_token, create_refresh_token

@router.post("/login", response_model=TokenResponse)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access & refresh tokens.
    """
    # 1. Authenticate user
    user = user_service.authenticate_user(db, email=user_credentials.email, password=user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 2. Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    # 3. Generate tokens
    # We embed the user's ID as the "sub" (subject) in the JWT
    token_payload = {"sub": str(user.id)}
    
    access_token = create_access_token(data=token_payload)
    refresh_token = create_refresh_token(data=token_payload)
    
    # 4. Save session to the database
    from app.services.session import create_user_session
    # Ideally, we would extract IP and User-Agent from a Request object here
    create_user_session(db=db, user_id=user.id, refresh_token=refresh_token)
    
    # 5. Return tokens to the user
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

from app.schemas.user import TokenRefresh
from app.core.jwt_utility import verify_refresh_token
from app.services.session import get_active_session_by_token, update_session_last_used
from datetime import datetime, timezone

@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Generate a new access token using a valid refresh token.
    """
    # 1. Verify the JWT signature and expiration
    payload = verify_refresh_token(token_data.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
        
    # 2. Check if the session exists and is active in the database
    session = get_active_session_by_token(db, token_data.refresh_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session revoked or invalid",
        )
        
    # 3. Check hard database expiration (fallback)
    # The session.expires_at is timezone aware if created correctly.
    # Convert now to utc to safely compare.
    if session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )
        
    # 4. Generate a new Access Token
    user_id = payload.get("sub")
    new_access_token = create_access_token(data={"sub": user_id})
    
    # 5. Update session last used timestamp
    update_session_last_used(db, session)
    
    # 6. Return new access token (and the same refresh token, or a new one)
    return {
        "access_token": new_access_token,
        "refresh_token": token_data.refresh_token,
        "token_type": "bearer"
    }

from app.services.session import revoke_session

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Log out a user by invalidating their refresh token session.
    """
    # 1. Find the active session matching the refresh token hash
    session = get_active_session_by_token(db, token_data.refresh_token)
    
    # 2. If no active session is found, we can silently ignore or throw an error.
    # A 400 or silently returning 200 are both common. Let's return 400 for strictness.
    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already revoked session",
        )
        
    # 3. Mark the session as inactive
    revoke_session(db, session)
    
    return {"detail": "Successfully logged out"}

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.session import revoke_all_user_sessions

@router.post("/logout-all", status_code=status.HTTP_200_OK)
def logout_all_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Log out the user from all devices by invalidating all their active sessions.
    Requires an active access token.
    """
    revoke_all_user_sessions(db, current_user.id)
    return {"detail": "Successfully logged out from all devices"}

