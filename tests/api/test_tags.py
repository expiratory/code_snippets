import pytest
from httpx import AsyncClient


async def get_auth_headers(async_client: AsyncClient, email="taguser@example.com"):
    # Register
    payload = {
        "email": email,
        "username": "taguser",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    response = await async_client.post("/auth/register", json=payload)
    if response.status_code == 201:
        token = response.json()["token"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # If already exists, login
    login_payload = {"email": email, "password": "Password123!"}
    response = await async_client.post("/auth/login", json=login_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_tag(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "create_tag@example.com")
    payload = {"name": "Test Tag"}
    response = await async_client.post("/tags", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Tag"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_tags(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "get_tags@example.com")
    # Create tag
    await async_client.post("/tags", json={"name": "Tag 1"}, headers=headers)
    await async_client.post("/tags", json={"name": "Tag 2"}, headers=headers)

    response = await async_client.get("/tags", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [t["name"] for t in data]
    assert "Tag 1" in names
    assert "Tag 2" in names


@pytest.mark.asyncio
async def test_update_tag(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "update_tag@example.com")
    # Create tag
    create_res = await async_client.post(
        "/tags", json={"name": "Old Name"}, headers=headers
    )
    tag_id = create_res.json()["id"]

    # Update
    response = await async_client.put(
        f"/tags/{tag_id}", json={"name": "New Name"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_tag(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "delete_tag@example.com")
    # Create tag
    create_res = await async_client.post(
        "/tags", json={"name": "Delete Me"}, headers=headers
    )
    tag_id = create_res.json()["id"]

    # Delete
    response = await async_client.delete(f"/tags/{tag_id}", headers=headers)
    assert response.status_code == 200

    # Verify deleted
    get_res = await async_client.get(f"/tags/{tag_id}", headers=headers)
    assert get_res.status_code == 404
