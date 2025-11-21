from sqlalchemy import Column, ForeignKey, Integer, String, Table, exc, select
from sqlalchemy.orm import relationship, selectinload

from app.db import SessionLocal
from app.errors.snippet import SnippetNotFoundError
from app.mq import publish_event
from app.repos.base import Base
from app.schemas.snippet import SnippetCreate, SnippetUpdate

snippet_tags = Table(
    "snippet_tags",
    Base.metadata,
    Column("snippet_id", Integer, ForeignKey("snippets.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Snippet(Base):
    __tablename__ = "snippets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    code = Column(String)

    language_id = Column(Integer, ForeignKey("languages.id"), nullable=True)
    language = relationship("Language", back_populates="snippets")
    tags = relationship("Tag", secondary=snippet_tags, back_populates="snippets")

    @classmethod
    async def get_by_id(cls, session: SessionLocal, id: int, user_id: int) -> "Snippet":
        try:
            result = await session.execute(
                select(Snippet)
                .filter(Snippet.id == id, Snippet.user_id == user_id)
                .options(selectinload(Snippet.tags), selectinload(Snippet.language))
            )
            return result.scalar_one()
        except exc.NoResultFound:
            raise SnippetNotFoundError

    @classmethod
    async def get_all(
        cls,
        session: SessionLocal,
        user_id: int,
        tag_name: str = None,
        query_text: str = None,
        language_id: int = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list["Snippet"]:
        snippet_ids = None
        if query_text:
            from app.services.search import SearchService

            search_service = SearchService()
            try:
                snippet_ids = await search_service.search_snippets(query_text)
                if not snippet_ids:
                    return []
            finally:
                await search_service.close()

        query = select(Snippet).filter(Snippet.user_id == user_id)

        if snippet_ids is not None:
            query = query.filter(Snippet.id.in_(snippet_ids))

        if tag_name:
            from app.repos.tag import Tag

            query = query.join(Snippet.tags).filter(Tag.name == tag_name)

        if language_id:
            query = query.filter(Snippet.language_id == language_id)

        query = (
            query.offset(offset)
            .limit(limit)
            .options(selectinload(Snippet.tags), selectinload(Snippet.language))
        )

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_ids(cls, session: SessionLocal, ids: list[int]) -> list["Snippet"]:
        result = await session.execute(
            select(Snippet)
            .filter(Snippet.id.in_(ids))
            .options(selectinload(Snippet.tags), selectinload(Snippet.language))
        )
        return result.scalars().all()

    @classmethod
    async def create(
        cls, session: SessionLocal, snippet: SnippetCreate, user_id: int
    ) -> "Snippet":
        db_snippet = Snippet(
            user_id=user_id,
            title=snippet.title,
            code=snippet.code,
            language_id=snippet.language_id,
        )

        if snippet.tags:
            from app.repos.tag import Tag

            for tag_name in snippet.tags:
                result = await session.execute(
                    select(Tag).filter(Tag.name == tag_name, Tag.user_id == user_id)
                )
                db_tag = result.scalar_one_or_none()

                if not db_tag:
                    db_tag = Tag(name=tag_name, user_id=user_id)
                    session.add(db_tag)

                db_snippet.tags.append(db_tag)

        session.add(db_snippet)
        await session.commit()

        result = await session.execute(
            select(Snippet)
            .filter(Snippet.id == db_snippet.id)
            .options(selectinload(Snippet.tags), selectinload(Snippet.language))
        )
        db_snippet = result.scalar_one()

        await publish_event(
            "snippet_events",
            "snippet.created",
            {
                "id": db_snippet.id,
                "title": db_snippet.title,
                "code": db_snippet.code,
                "language": db_snippet.language.name if db_snippet.language else None,
            },
        )

        return db_snippet

    @classmethod
    async def update(
        cls, session: SessionLocal, id: int, snippet: SnippetUpdate, user_id: int
    ) -> "Snippet":
        try:
            result = await session.execute(
                select(Snippet)
                .filter(Snippet.id == id, Snippet.user_id == user_id)
                .options(selectinload(Snippet.tags), selectinload(Snippet.language))
            )
            db_snippet = result.scalar_one()
        except exc.NoResultFound:
            raise SnippetNotFoundError

        if snippet.title is not None:
            db_snippet.title = snippet.title
        if snippet.code is not None:
            db_snippet.code = snippet.code
        if snippet.language_id is not None:
            db_snippet.language_id = snippet.language_id

        if snippet.tags is not None:
            from app.repos.tag import Tag

            db_snippet.tags = []

            for tag_name in snippet.tags:
                result = await session.execute(
                    select(Tag).filter(Tag.name == tag_name, Tag.user_id == user_id)
                )
                db_tag = result.scalar_one_or_none()

                if not db_tag:
                    db_tag = Tag(name=tag_name, user_id=user_id)
                    session.add(db_tag)

                db_snippet.tags.append(db_tag)

        await session.commit()
        await session.refresh(db_snippet)

        await publish_event(
            "snippet_events",
            "snippet.updated",
            {
                "id": db_snippet.id,
                "title": db_snippet.title,
                "code": db_snippet.code,
                "language": db_snippet.language.name if db_snippet.language else None,
            },
        )

        return db_snippet

    @classmethod
    async def delete(cls, session: SessionLocal, id: int, user_id: int) -> "Snippet":
        try:
            result = await session.execute(
                select(Snippet)
                .filter(Snippet.id == id, Snippet.user_id == user_id)
                .options(selectinload(Snippet.tags), selectinload(Snippet.language))
            )
            db_snippet = result.scalar_one()
        except exc.NoResultFound:
            raise SnippetNotFoundError
        await session.delete(db_snippet)
        await session.commit()

        await publish_event(
            "snippet_events",
            "snippet.deleted",
            {"id": id},
        )

        return db_snippet
