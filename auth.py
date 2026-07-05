"""
Authentication and Authorization System

JWT-based authentication with user registration, login, and token management.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from config import settings
from database import db, User


# Security
security = HTTPBearer()


# Pydantic models for requests/responses

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""
    user_id: int
    email: str
    username: str


class UserProfile(BaseModel):
    """User profile response."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    subscription_plan: str
    wallet_balance: float
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# JWT token functions

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.auth.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.secret_key,
        algorithm=settings.auth.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.auth.refresh_token_expire_days)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.secret_key,
        algorithm=settings.auth.algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.auth.secret_key,
            algorithms=[settings.auth.algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Authentication dependency

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Get user from database
    session = db.get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
        
    finally:
        session.close()


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Auth service functions

class AuthService:
    """Authentication service."""
    
    @staticmethod
    def register_user(email: str, username: str, password: str, full_name: Optional[str] = None) -> User:
        """Register a new user."""
        # Check if email already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Validate password strength
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )
        
        # Create user
        try:
            user = db.create_user(
                email=email,
                username=username,
                password=password,
                full_name=full_name
            )
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    @staticmethod
    def login_user(email: str, password: str) -> Token:
        """Authenticate user and return tokens."""
        # Get user
        user = db.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not user.verify_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        session = db.get_session()
        try:
            user.last_login = datetime.utcnow()
            session.commit()
        finally:
            session.close()
        
        # Create tokens
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.auth.access_token_expire_minutes * 60
        )
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        try:
            payload = decode_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            token_data = {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "username": payload.get("username")
            }
            
            access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)
            
            return Token(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.auth.access_token_expire_minutes * 60
            )
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    @staticmethod
    def get_user_profile(user: User) -> UserProfile:
        """Get user profile information."""
        return UserProfile(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            subscription_plan=user.subscription_plan.value,
            wallet_balance=user.wallet.balance if user.wallet else 0.0,
            is_verified=user.is_verified,
            created_at=user.created_at
        )


# Initialize auth service
auth_service = AuthService()
