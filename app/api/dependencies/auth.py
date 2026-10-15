from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.jwt_utility import verify_access_token
from app.api.dependencies.database import get_db
from app.models.user import User

# This scheme expects the token in the "Authorization" header formatted as: "Bearer <token>"
# The tokenUrl helps FastAPI's auto-generated Swagger UI know where to authenticate
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency that extracts the JWT token from the Authorization header,
    verifies its signature/expiration, and returns the corresponding User object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Verify the access token (math checks, expiration, type)
    payload = verify_access_token(token)
    if not payload:
        raise credentials_exception
        
    # 2. Extract the user ID (subject) from the payload
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
        
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception
        
    # 3. Retrieve the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    # 4. Enforce that only active users can authenticate
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
        
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    Dependency that enforces the current user has administrative privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

