import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError

# These should ideally come from environment variables / config file
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-for-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh tokens live much longer

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a new JWT access token containing the provided payload data.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    # Embed the expiration time and a specific type claim
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> Optional[dict]:
    """
    Verify the JWT token and return the decoded payload if valid.
    Returns None if the token is invalid, expired, or not an access token.
    """
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_data.get("type") != "access":
            return None
        return decoded_data
    except JWTError:
        return None

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a new JWT refresh token containing the provided payload data.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
    # Differentiate this from an access token via the type claim
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str) -> Optional[dict]:
    """
    Verify the JWT refresh token and return the decoded payload if valid.
    Returns None if the token is invalid, expired, or not a refresh token.
    """
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_data.get("type") != "refresh":
            return None
        return decoded_data
    except JWTError:
        return None


