import pytest
from httpx import AsyncClient


async def get_auth_headers(async_client: AsyncClient, email="snippetuser@example.com"):
    # Register
    payload = {
        "email": email,
        "username": "snippetuser",
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
async def test_create_snippet(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "create_snippet@example.com")

    # Create Language
    lang_res = await async_client.post("/languages", json={"name": "Python"})
    lang_id = lang_res.json()["id"]

    payload = {
        "title": "Hello World",
        "code": "print('Hello World')",
        "language_id": lang_id,
        "tags": ["test"],
    }
    response = await async_client.post("/snippets", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hello World"
    assert data["language"]["id"] == lang_id
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "test"


@pytest.mark.asyncio
async def test_get_snippets(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "get_snippets@example.com")

    # Create Language
    lang_res = await async_client.post("/languages", json={"name": "Go"})
    lang_id = lang_res.json()["id"]

    # Create Snippet
    payload = {"title": "Go Routine", "code": "go func() {}", "language_id": lang_id}
    await async_client.post("/snippets", json=payload, headers=headers)

    response = await async_client.get("/snippets", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    titles = [s["title"] for s in data]
    assert "Go Routine" in titles


@pytest.mark.asyncio
async def test_update_snippet(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "update_snippet@example.com")

    # Create Language
    lang_res = await async_client.post("/languages", json={"name": "Rust"})
    lang_id = lang_res.json()["id"]

    # Create Snippet
    payload = {"title": "Rust Ownership", "code": "let x = 5;", "language_id": lang_id}
    create_res = await async_client.post("/snippets", json=payload, headers=headers)
    snippet_id = create_res.json()["id"]

    # Update
    update_payload = {"title": "Rust Borrowing", "code": "let x = 5;"}
    response = await async_client.put(
        f"/snippets/{snippet_id}", json=update_payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Rust Borrowing"


@pytest.mark.asyncio
async def test_delete_snippet(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "delete_snippet@example.com")

    # Create Language
    lang_res = await async_client.post("/languages", json={"name": "Java"})
    lang_id = lang_res.json()["id"]

    # Create Snippet
    payload = {
        "title": "Java Class",
        "code": "public class Main {}",
        "language_id": lang_id,
    }
    create_res = await async_client.post("/snippets", json=payload, headers=headers)
    snippet_id = create_res.json()["id"]

    # Delete
    response = await async_client.delete(f"/snippets/{snippet_id}", headers=headers)
    assert response.status_code == 200

    # Verify deleted
    get_res = await async_client.get(f"/snippets/{snippet_id}", headers=headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_search_snippets(async_client: AsyncClient, monkeypatch):
    headers = await get_auth_headers(async_client, "search_snippet@example.com")

    # Mock SearchService
    from unittest.mock import AsyncMock

    mock_search = AsyncMock()
    mock_search.search_snippets.return_value = [1]

    import app.services.search

    monkeypatch.setattr(app.services.search, "SearchService", lambda: mock_search)

    # Create Language
    lang_res = await async_client.post("/languages", json={"name": "SearchLang"})
    lang_id = lang_res.json()["id"]

    # Create a snippet to be found
    payload = {"title": "Search Me", "code": "find me", "language_id": lang_id}
    create_res = await async_client.post("/snippets", json=payload, headers=headers)
    snippet_id = create_res.json()["id"]

    mock_search.search_snippets.return_value = [snippet_id]

    response = await async_client.get("/snippets?query=find", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == snippet_id


@pytest.mark.asyncio
async def test_filter_snippets(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "filter_snippet@example.com")

    # Create Language
    lang_res = await async_client.post("/languages", json={"name": "FilterLang"})
    lang_id = lang_res.json()["id"]

    # Create Snippet with Tag
    payload = {
        "title": "Filter Me",
        "code": "filter me",
        "language_id": lang_id,
        "tags": ["filter_tag"],
    }
    await async_client.post("/snippets", json=payload, headers=headers)

    # Filter by Tag
    response = await async_client.get("/snippets?tag=filter_tag", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["tags"][0]["name"] == "filter_tag"

    # Filter by Language
    response = await async_client.get(
        f"/snippets?language_id={lang_id}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["language"]["id"] == lang_id


@pytest.mark.asyncio
async def test_pagination(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "pagination@example.com")

    # Create Language
    lang_res = await async_client.post("/languages", json={"name": "PageLang"})
    lang_id = lang_res.json()["id"]

    # Create 3 Snippets
    for i in range(3):
        payload = {"title": f"Page {i}", "code": f"code {i}", "language_id": lang_id}
        await async_client.post("/snippets", json=payload, headers=headers)

    # Get Page 1 (limit 2)
    response = await async_client.get("/snippets?limit=2&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Get Page 2 (limit 2, offset 2)
    response = await async_client.get("/snippets?limit=2&offset=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
