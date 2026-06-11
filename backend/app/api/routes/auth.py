from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
    """Register a new user."""
    # Check if user email already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    hashed_password = security.get_password_hash(user_in.password)
    # Check if this is the first user, make them superuser
    first_user_check = await db.execute(select(User).limit(1))
    is_first = first_user_check.scalars().first() is None
    
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_superuser=is_first,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """OAuth2 compatible token login, retrieve access token."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout() -> Any:
    """Logout endpoint stub (client-side handles removing token)."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserRead)
async def read_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """Get current user details."""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)) -> Any:
    """Refresh JWT access token for current active user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            current_user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


# OAuth stubs for template showcase compatibility
@router.get("/oauth/login")
async def oauth_login() -> Any:
    """Stub to initiate OAuth login flow."""
    return {"authorize_url": "/api/auth/oauth/callback?code=mock_code"}


@router.get("/oauth/callback")
async def oauth_callback(code: str) -> Any:
    """Stub to handle OAuth authentication callback."""
    # Dummy user logic or redirect
    return {
        "access_token": security.create_access_token("oauth_user@example.com"),
        "token_type": "bearer",
        "email": "oauth_user@example.com"
    }
