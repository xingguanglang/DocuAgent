"""Shared test fixtures."""

from __future__ import annotations

import os

# Set test env vars BEFORE any app imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["DEBUG"] = "false"
os.environ["UPLOAD_DIR"] = os.path.join(os.path.dirname(__file__), ".tmp_uploads")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.database import Base, engine


@pytest_asyncio.fixture(autouse=True)
async def _setup_db():
    """Create and tear down test database for each test."""
    import shutil

    upload_dir = os.environ.get("UPLOAD_DIR", ".tmp_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)


@pytest_asyncio.fixture
async def client():
    """Provide an async HTTP test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient):
    """Provide an authenticated test client with a registered user."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpass123", "name": "Test User"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_res.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
