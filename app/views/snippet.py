import json
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, status
from redis.asyncio import Redis as RedisClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.limiter import limiter
from app.redis import get_redis
from app.repos.snippet import Snippet
from app.repos.user import User
from app.schemas.snippet import SnippetCreate, SnippetRead, SnippetUpdate
from app.services.search import SearchService

router = APIRouter(prefix="/snippets", tags=["Snippets"])


@router.get("", response_model=List[SnippetRead])
async def get_snippets(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    language_id: Optional[int] = None,
    offset: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all snippets, optionally filtered by tag and search query."""
    return await Snippet.get_all(
        session,
        user_id=current_user.id,
        tag_name=tag,
        query_text=q,
        language_id=language_id,
        offset=offset,
        limit=limit,
    )


@router.get("/search", response_model=list[SnippetRead])
async def search_snippets(q: str, session: AsyncSession = Depends(get_db)):
    search_service = SearchService()
    try:
        snippet_ids = await search_service.search_snippets(q)
        if not snippet_ids:
            return []
        snippets = await Snippet.get_by_ids(session, snippet_ids)
        return snippets
    finally:
        await search_service.close()


@router.get(
    "/{id}",
    response_model=SnippetRead,
    responses={404: {"description": "Snippet not found"}},
)
async def get_snippet(
    id: int,
    session: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    cached = await redis.get(f"snippet:{id}:{current_user.id}")
    if cached:
        return json.loads(cached)

    snippet = await Snippet.get_by_id(session, id, current_user.id)
    snippet_data = SnippetRead.model_validate(snippet).model_dump_json()
    await redis.set(f"snippet:{id}:{current_user.id}", snippet_data, ex=300)

    return snippet


@router.post("", response_model=SnippetRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def create_snippet(
    request: Request,
    snippet: SnippetCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snippet = await Snippet.create(session, snippet, current_user.id)
    return snippet


@router.put(
    "/{id}",
    response_model=SnippetRead,
    responses={404: {"description": "Snippet not found"}},
)
@limiter.limit("3/minute")
async def update_snippet(
    request: Request,
    id: int,
    snippet: SnippetUpdate,
    session: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    snippet = await Snippet.update(session, id, snippet, current_user.id)
    await redis.delete(f"snippet:{id}:{current_user.id}")
    return snippet


@router.delete("/{id}", responses={404: {"description": "Snippet not found"}})
async def delete_snippet(
    id: int,
    session: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    await Snippet.delete(session, id, current_user.id)
    await redis.delete(f"snippet:{id}:{current_user.id}")
    return {"message": "Snippet deleted successfully"}
