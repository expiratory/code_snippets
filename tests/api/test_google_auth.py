from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.views.auth import oauth


@pytest.mark.asyncio
async def test_google_login(async_client: AsyncClient, monkeypatch):
    from fastapi.responses import RedirectResponse

    mock_authorize_redirect = AsyncMock(
        return_value=RedirectResponse("http://google.com/auth")
    )
    monkeypatch.setattr(oauth.google, "authorize_redirect", mock_authorize_redirect)

    response = await async_client.get("/auth/google/login")
    assert response.status_code == 307
    assert response.headers["location"] == "http://google.com/auth"


@pytest.mark.asyncio
async def test_google_callback_register(async_client: AsyncClient, monkeypatch):
    # Mock oauth.google.authorize_access_token
    mock_token = {"userinfo": {"email": "google@example.com", "name": "Google User"}}
    mock_authorize_access_token = AsyncMock(return_value=mock_token)
    monkeypatch.setattr(
        oauth.google, "authorize_access_token", mock_authorize_access_token
    )

    response = await async_client.get("/auth/google/callback")
    assert response.status_code == 307
    assert "google-register" in response.headers["location"]
    assert "email=google@example.com" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_login(async_client: AsyncClient, monkeypatch):
    # Register user first
    payload = {
        "email": "google_login@example.com",
        "username": "googleuser",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    await async_client.post("/auth/register", json=payload)

    # Mock oauth.google.authorize_access_token
    mock_token = {
        "userinfo": {"email": "google_login@example.com", "name": "Google User"}
    }
    mock_authorize_access_token = AsyncMock(return_value=mock_token)
    monkeypatch.setattr(
        oauth.google, "authorize_access_token", mock_authorize_access_token
    )

    response = await async_client.get("/auth/google/callback")
    assert response.status_code == 307
    assert "callback" in response.headers["location"]
    assert "token=" in response.headers["location"]


@pytest.mark.asyncio
async def test_complete_google_register(async_client: AsyncClient):
    # Get registration token
    from app.auth import create_registration_token

    token = create_registration_token(
        {"sub": "new_google@example.com", "name": "New Google User"}
    )

    payload = {
        "password": "Password123!",
        "confirm_password": "Password123!",
        "registration_token": token,
    }
    response = await async_client.post("/auth/google/complete-register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
