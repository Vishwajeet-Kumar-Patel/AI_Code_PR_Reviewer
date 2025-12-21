"""
Authentication models
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: Optional[EmailStr] = None
    github_username: str
    avatar_url: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: Optional[str] = Field(None, min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if v:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters')
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain lowercase letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain digit')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: Optional[EmailStr] = None
    github_username: Optional[str] = None
    password: str
    
    @validator('github_username', always=True)
    def check_email_or_username(cls, v, values):
        if not v and not values.get('email'):
            raise ValueError('Either email or github_username must be provided')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class ApiKeyCreate(BaseModel):
    """API key creation schema"""
    name: str = Field(..., min_length=1, max_length=100)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class ApiKeyResponse(BaseModel):
    """API key response schema"""
    id: int
    name: str
    key: str  # Only returned on creation
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class ApiKeyList(BaseModel):
    """API key list item (without key)"""
    id: int
    name: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePassword(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        if v == values.get('current_password'):
            raise ValueError('New password must be different from current password')
        return v


class OAuth2Callback(BaseModel):
    """OAuth2 callback data"""
    code: str
    state: Optional[str] = None


class GithubUserInfo(BaseModel):
    """GitHub user information"""
    login: str
    id: int
    avatar_url: str
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
