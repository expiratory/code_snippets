from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis as RedisClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.limiter import limiter
from app.redis import get_redis
from app.repos.tag import Tag
from app.repos.user import User
from app.schemas.tag import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead] | list[dict])
async def get_tags(
    limit: int = 100,
    with_stats: bool = False,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if with_stats:
        return await Tag.get_with_stats(session, current_user.id)

    tags = await Tag.get_all(session, current_user.id, limit=limit)
    return tags


@router.get(
    "/{id}", response_model=TagRead, responses={404: {"description": "Tag not found"}}
)
async def get_tag(
    id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = await Tag.get_by_id(session, id, current_user.id)
    return tag


@router.post("", response_model=TagRead)
@limiter.limit("3/minute")
async def create_tag(
    request: Request,
    tag: TagCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = await Tag.create(session, tag, current_user.id)
    return tag


@router.put(
    "/{id}", response_model=TagRead, responses={404: {"description": "Tag not found"}}
)
@limiter.limit("3/minute")
async def update_tag(
    request: Request,
    id: int,
    tag: TagUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = await Tag.update(session, id, tag, current_user.id)
    return tag


@router.delete("/{id}", responses={404: {"description": "Tag not found"}})
async def delete_tag(
    id: int,
    session: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    tag = await Tag.delete(session, id, current_user.id)
    for snippet in tag.snippets:
        await redis.delete(f"snippet:{snippet.id}:{current_user.id}")
    return {"message": "Tag deleted successfully"}
