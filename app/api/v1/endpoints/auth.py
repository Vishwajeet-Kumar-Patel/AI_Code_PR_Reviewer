"""
Authentication and authorization endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import httpx

from app.models.auth import (
    UserCreate, UserLogin, UserResponse, Token, TokenRefresh,
    ApiKeyCreate, ApiKeyResponse, ApiKeyList, ChangePassword,
    OAuth2Callback, GithubUserInfo
)
from app.core.deps import get_db, get_current_user, get_current_active_user
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token,
    security_service
)
from app.db.models import User, ApiKey, AuditLog
from app.core.config import settings
from app.core.logging import logger


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.github_username == user_data.github_username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    db_user = User(
        email=user_data.email,
        github_username=user_data.github_username,
        hashed_password=get_password_hash(user_data.password) if user_data.password else None,
        avatar_url=user_data.avatar_url,
        full_name=user_data.full_name,
        role="user",
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log audit
    audit = AuditLog(
        user_id=db_user.id,
        action="create",
        resource_type="user",
        resource_id=str(db_user.id)
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"New user registered: {db_user.email}")
    return db_user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email/username and password"""
    # Find user
    user = db.query(User).filter(
        (User.email == login_data.email) | (User.github_username == login_data.github_username)
    ).first()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Create tokens
    token_data = {"sub": str(user.id), "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Log audit
    audit = AuditLog(
        user_id=user.id,
        action="login",
        resource_type="session",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(token_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        token_data = {"sub": str(user.id), "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password authentication not enabled for this account"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="update",
        resource_type="user",
        resource_id=str(current_user.id),
        metadata={"action_detail": "password_change"}
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    return {"message": "Password changed successfully"}


# API Key Management
@router.post("/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    # Generate API key
    key_token = security_service.create_api_key(current_user.id, key_data.name)
    
    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Store API key
    api_key = ApiKey(
        user_id=current_user.id,
        name=key_data.name,
        key=key_token,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="create",
        resource_type="api_key",
        resource_id=str(api_key.id)
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"API key created for user: {current_user.email}")
    return api_key


@router.get("/api-keys", response_model=list[ApiKeyList])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all API keys for current user"""
    api_keys = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id
    ).order_by(ApiKey.created_at.desc()).all()
    
    return api_keys


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="delete",
        resource_type="api_key",
        resource_id=str(key_id)
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"API key deleted: {key_id}")


# OAuth2 - GitHub
@router.get("/github/login")
async def github_login():
    """Redirect to GitHub OAuth"""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured"
        )
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.OAUTH_REDIRECT_URI}"
        f"&scope=user:email,read:org"
    )
    
    return RedirectResponse(url=github_auth_url)


@router.post("/github/callback", response_model=Token)
async def github_callback(
    callback_data: OAuth2Callback,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured"
        )
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": callback_data.code,
            },
            headers={"Accept": "application/json"}
        )
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with GitHub"
            )
        
        # Get user info from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )
        
        github_user = user_response.json()
    
    # Find or create user
    user = db.query(User).filter(User.github_id == str(github_user["id"])).first()
    
    if not user:
        user = User(
            github_id=str(github_user["id"]),
            github_username=github_user["login"],
            email=github_user.get("email"),
            avatar_url=github_user.get("avatar_url"),
            full_name=github_user.get("name"),
            oauth_provider="github",
            role="user",
            is_active=True,
            is_verified=True
        )
        db.add(user)
    else:
        # Update existing user
        user.avatar_url = github_user.get("avatar_url")
        user.full_name = github_user.get("name")
        user.last_login_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Log audit
    audit = AuditLog(
        user_id=user.id,
        action="login",
        resource_type="session",
        ip_address=request.client.host if request.client else None,
        metadata={"provider": "github"}
    )
    db.add(audit)
    db.commit()
    
    # Create tokens
    token_data = {"sub": str(user.id), "role": user.role}
    jwt_access_token = create_access_token(token_data)
    jwt_refresh_token = create_refresh_token(token_data)
    
    logger.info(f"User logged in via GitHub: {user.email}")
    
    return {
        "access_token": jwt_access_token,
        "refresh_token": jwt_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user (client should discard tokens)"""
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="logout",
        resource_type="session"
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out successfully"}
