from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    """Base schema with common attributes."""
    email: EmailStr

class UserCreate(UserBase):
    """Schema for user registration request payload."""
    password: str = Field(
        min_length=8, 
        description="Password must be at least 8 characters long."
    )

class UserLogin(UserBase):
    """Schema for user login request payload."""
    password: str = Field(description="The user's password")

class UserResponse(UserBase):
    """Schema for returning user data in responses."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # This configuration tells Pydantic to read data even if it is not a dict, 
    # but an ORM model (like our SQLAlchemy User model).
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    """Schema for returning JWT tokens after successful login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    """Schema for the refresh token request payload."""
    refresh_token: str

class SessionResponse(BaseModel):
    """Schema for returning user session information."""
    id: int
    user_agent: str | None = None
    is_active: bool
    created_at: datetime
    last_used_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


