import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == payload["email"]
    assert "token" in data
    assert "access_token" in data["token"]


@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    # Register first
    payload = {
        "email": "login@example.com",
        "username": "loginuser",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    await async_client.post("/auth/register", json=payload)

    # Login
    login_payload = {"email": "login@example.com", "password": "Password123!"}
    response = await async_client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_token(async_client: AsyncClient):
    # Register
    payload = {
        "email": "refresh@example.com",
        "username": "refreshuser",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    reg_response = await async_client.post("/auth/register", json=payload)
    refresh_token = reg_response.json()["token"]["refresh_token"]

    # Refresh
    response = await async_client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient):
    # Register
    payload = {
        "email": "me@example.com",
        "username": "meuser",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    reg_response = await async_client.post("/auth/register", json=payload)
    access_token = reg_response.json()["token"]["access_token"]

    # Get Me
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]


@pytest.mark.asyncio
async def test_change_password(async_client: AsyncClient):
    # Register
    payload = {
        "email": "changepass@example.com",
        "username": "changepassuser",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    reg_response = await async_client.post("/auth/register", json=payload)
    access_token = reg_response.json()["token"]["access_token"]

    # Change Password
    headers = {"Authorization": f"Bearer {access_token}"}
    change_payload = {
        "old_password": "Password123!",
        "new_password": "NewPassword123!",
        "confirm_new_password": "NewPassword123!",
    }
    response = await async_client.post(
        "/auth/change-password", json=change_payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    # Login with new password
    login_payload = {"email": "changepass@example.com", "password": "NewPassword123!"}
    login_response = await async_client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_register_user_duplicate(async_client: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "username": "duplicate",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    # First registration
    await async_client.post("/auth/register", json=payload)

    # Second registration
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    payload = {"email": "nonexistent@example.com", "password": "Password123!"}
    response = await async_client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_change_password_mismatch(async_client: AsyncClient):
    # Register
    payload = {
        "email": "mismatch@example.com",
        "username": "mismatch",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    reg_response = await async_client.post("/auth/register", json=payload)
    access_token = reg_response.json()["token"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "old_password": "Password123!",
        "new_password": "NewPassword123!",
        "confirm_new_password": "WrongPassword!",
    }
    response = await async_client.post(
        "/auth/change-password", json=payload, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_change_password_wrong_old(async_client: AsyncClient):
    # Register
    payload = {
        "email": "wrong_old@example.com",
        "username": "wrong_old",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    reg_response = await async_client.post("/auth/register", json=payload)
    access_token = reg_response.json()["token"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "old_password": "WrongPassword!",
        "new_password": "NewPassword123!",
        "confirm_new_password": "NewPassword123!",
    }
    response = await async_client.post(
        "/auth/change-password", json=payload, headers=headers
    )
    assert response.status_code == 400
    assert "Invalid old password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_change_password_same(async_client: AsyncClient):
    # Register
    payload = {
        "email": "same@example.com",
        "username": "same",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    reg_response = await async_client.post("/auth/register", json=payload)
    access_token = reg_response.json()["token"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "old_password": "Password123!",
        "new_password": "Password123!",
        "confirm_new_password": "Password123!",
    }
    response = await async_client.post(
        "/auth/change-password", json=payload, headers=headers
    )
    assert response.status_code == 400
    assert "must be different" in response.json()["detail"]
