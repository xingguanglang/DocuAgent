"""Authentication endpoints."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import APIRouter, HTTPException, status
from jose import jwt
from sqlalchemy import select

from app.config import settings
from app.models.database import User, async_session
from app.models.schemas import LoginRequest, LoginResponse, RegisterRequest, UserResponse

router = APIRouter()


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password.

    Returns:
        Bcrypt hashed password string.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash.

    Args:
        password: Plain text password to verify.
        hashed: Bcrypt hashed password to check against.

    Returns:
        True if password matches, False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def _create_access_token(user_id: str, email: str) -> str:
    """Create a JWT access token.

    Args:
        user_id: User's unique identifier.
        email: User's email address.

    Returns:
        Encoded JWT token string.
    """
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest) -> UserResponse:
    """Register a new user account.

    Args:
        request: Registration data including email and password.

    Returns:
        Created user information.
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user = User(
            email=request.email,
            name=request.name,
            hashed_password=_hash_password(request.password),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Authenticate user and return JWT token.

    Args:
        request: Login credentials.

    Returns:
        JWT access token.
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()

        if not user or not _verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = _create_access_token(user.id, user.email)
        return LoginResponse(access_token=token)
