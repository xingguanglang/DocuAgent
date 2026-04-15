"""Tests for authentication endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    """Registering a new user returns user info."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "securepass123", "name": "New User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["name"] == "New User"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Registering with an existing email returns 409."""
    payload = {"email": "dup@example.com", "password": "securepass123", "name": "User"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """Logging in with correct credentials returns a token."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "securepass123", "name": "User"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    """Logging in with wrong password returns 401."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "password": "securepass123", "name": "User"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
