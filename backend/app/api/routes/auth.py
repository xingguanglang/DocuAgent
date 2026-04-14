"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import LoginRequest, LoginResponse, RegisterRequest, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest) -> UserResponse:
    """Register a new user account.

    Args:
        request: Registration data including email and password.

    Returns:
        Created user information.
    """
    # TODO: Implement user registration
    raise NotImplementedError


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Authenticate user and return JWT token.

    Args:
        request: Login credentials.

    Returns:
        JWT access token.
    """
    # TODO: Implement login
    raise NotImplementedError
