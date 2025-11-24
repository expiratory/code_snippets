import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_language(async_client: AsyncClient):
    payload = {"name": "Python"}
    response = await async_client.post("/languages", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Python"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_languages(async_client: AsyncClient):
    # Create a language first
    payload = {"name": "JavaScript"}
    await async_client.post("/languages", json=payload)

    response = await async_client.get("/languages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    names = [lang["name"] for lang in data]
    assert "JavaScript" in names
