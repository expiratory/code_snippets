from fastapi import APIRouter, Depends

from app.db import SessionLocal, get_db
from app.repos.tag import Tag
from app.schemas.tag import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def get_tags(session: SessionLocal = Depends(get_db)):
    tags = Tag.get_all(session)
    return tags


@router.get(
    "/{id}", response_model=TagRead, responses={404: {"description": "Tag not found"}}
)
def get_tag(id: int, session: SessionLocal = Depends(get_db)):
    tag = Tag.get_by_id(session, id)
    return tag


@router.post("", response_model=TagRead)
def create_tag(tag: TagCreate, session: SessionLocal = Depends(get_db)):
    tag = Tag.create(session, tag)
    return tag


@router.put(
    "/{id}", response_model=TagRead, responses={404: {"description": "Tag not found"}}
)
def update_tag(id: int, tag: TagUpdate, session: SessionLocal = Depends(get_db)):
    tag = Tag.update(session, id, tag)
    return tag


@router.delete("/{id}", responses={404: {"description": "Tag not found"}})
def delete_tag(id: int, session: SessionLocal = Depends(get_db)):
    Tag.delete(session, id)
    return {"message": "Tag deleted successfully"}
