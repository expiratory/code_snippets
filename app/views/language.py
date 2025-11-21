from fastapi import APIRouter, Depends, status

from app.db import SessionLocal, get_db
from app.repos.language import Language
from app.schemas.language import LanguageCreate, LanguageRead

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("", response_model=list[LanguageRead])
async def get_languages(
    query: str = None,
    limit: int = 100,
    session: SessionLocal = Depends(get_db),
):
    return await Language.get_all(session, query=query, limit=limit)


@router.post("", response_model=LanguageRead, status_code=status.HTTP_201_CREATED)
async def create_language(
    language: LanguageCreate,
    session: SessionLocal = Depends(get_db),
):
    existing = await Language.get_by_name(session, language.name)
    if existing:
        return existing
    return await Language.create(session, language)
