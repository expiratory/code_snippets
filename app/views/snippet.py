from fastapi import APIRouter, Depends

from app.db import SessionLocal, get_db
from app.repos.snippet import Snippet
from app.schemas.snippet import SnippetCreate, SnippetRead, SnippetUpdate

router = APIRouter(prefix="/snippets", tags=["snippets"])


@router.get("", response_model=list[SnippetRead])
def get_snippets(session: SessionLocal = Depends(get_db)):
    snippets = Snippet.get_all(session)
    return snippets


@router.get(
    "/{id}",
    response_model=SnippetRead,
    responses={404: {"description": "Snippet not found"}},
)
def get_snippet(id: int, session: SessionLocal = Depends(get_db)):
    snippet = Snippet.get_by_id(session, id)
    return snippet


@router.post("", response_model=SnippetRead)
def create_snippet(snippet: SnippetCreate, session: SessionLocal = Depends(get_db)):
    snippet = Snippet.create(session, snippet)
    return snippet


@router.put(
    "/{id}",
    response_model=SnippetRead,
    responses={404: {"description": "Snippet not found"}},
)
def update_snippet(
    id: int, snippet: SnippetUpdate, session: SessionLocal = Depends(get_db)
):
    snippet = Snippet.update(session, id, snippet)
    return snippet


@router.delete("/{id}", responses={404: {"description": "Snippet not found"}})
def delete_snippet(id: int, session: SessionLocal = Depends(get_db)):
    Snippet.delete(session, id)
    return {"message": "Snippet deleted successfully"}
