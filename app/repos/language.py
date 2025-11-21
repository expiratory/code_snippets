from sqlalchemy import Column, Integer, String, exc, select
from sqlalchemy.orm import relationship

from app.db import SessionLocal
from app.errors.language import LanguageNotFoundError
from app.repos.base import Base
from app.schemas.language import LanguageCreate


class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)

    snippets = relationship("Snippet", back_populates="language")

    @classmethod
    async def get_all(
        cls, session: SessionLocal, query: str = None, limit: int = 100
    ) -> list["Language"]:
        stmt = select(Language)
        if query:
            stmt = stmt.filter(Language.name.ilike(f"%{query}%"))
        stmt = stmt.order_by(Language.name).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get_by_name(cls, session: SessionLocal, name: str) -> "Language | None":
        stmt = select(Language).filter(Language.name == name)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, session: SessionLocal, id: int) -> "Language":
        stmt = select(Language).filter(Language.id == id)

        try:
            result = await session.execute(stmt)
            return result.scalar_one()
        except exc.NoResultFound:
            raise LanguageNotFoundError

    @classmethod
    async def create(
        cls, session: SessionLocal, language: LanguageCreate
    ) -> "Language":
        db_language = Language(
            name=language.name,
            slug=language.name.lower().replace(" ", "-"),
        )
        session.add(db_language)
        await session.commit()
        await session.refresh(db_language)
        return db_language
