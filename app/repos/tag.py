from sqlalchemy import Column, ForeignKey, Integer, String, exc, select
from sqlalchemy.orm import relationship, selectinload

from app.db import SessionLocal
from app.errors.tag import TagNotFoundError
from app.repos.base import Base
from app.repos.snippet import snippet_tags
from app.schemas.tag import TagCreate, TagUpdate


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String)
    snippets = relationship("Snippet", secondary=snippet_tags, back_populates="tags")

    @classmethod
    async def get_by_id(cls, session: SessionLocal, id: int, user_id: int) -> "Tag":
        try:
            result = await session.execute(
                select(Tag).filter(Tag.id == id, Tag.user_id == user_id)
            )
            return result.scalar_one()
        except exc.NoResultFound:
            raise TagNotFoundError

    @classmethod
    async def get_all(
        cls, session: SessionLocal, user_id: int, limit: int = 100
    ) -> list["Tag"]:
        query = (
            select(Tag)
            .filter(Tag.user_id == user_id)
            .order_by(Tag.id.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_with_stats(cls, session: SessionLocal, user_id: int) -> list[dict]:
        from sqlalchemy import func

        from app.repos.snippet import snippet_tags

        query = (
            select(Tag, func.count(snippet_tags.c.snippet_id).label("count"))
            .outerjoin(snippet_tags, Tag.id == snippet_tags.c.tag_id)
            .filter(Tag.user_id == user_id)
            .group_by(Tag.id)
            .order_by(Tag.name)
        )

        result = await session.execute(query)
        tags_with_stats = []
        for tag, count in result:
            tags_with_stats.append(
                {
                    "id": tag.id,
                    "name": tag.name,
                    "user_id": tag.user_id,
                    "snippet_count": count,
                }
            )
        return tags_with_stats

    @classmethod
    async def create(cls, session: SessionLocal, tag: TagCreate, user_id: int) -> "Tag":
        db_tag = Tag(name=tag.name, user_id=user_id)
        session.add(db_tag)
        await session.commit()
        await session.refresh(db_tag)
        return db_tag

    @classmethod
    async def update(
        cls, session: SessionLocal, id: int, tag: TagUpdate, user_id: int
    ) -> "Tag":
        try:
            result = await session.execute(
                select(Tag).filter(Tag.id == id, Tag.user_id == user_id)
            )
            db_tag = result.scalar_one()
        except exc.NoResultFound:
            raise TagNotFoundError
        db_tag.name = tag.name
        await session.commit()
        await session.refresh(db_tag)
        return db_tag

    @classmethod
    async def delete(cls, session: SessionLocal, id: int, user_id: int) -> "Tag":
        try:
            result = await session.execute(
                select(Tag)
                .filter(Tag.id == id, Tag.user_id == user_id)
                .options(selectinload(Tag.snippets))
            )
            db_tag = result.scalar_one()
        except exc.NoResultFound:
            raise TagNotFoundError

        await session.execute(
            snippet_tags.delete().where(snippet_tags.c.tag_id == db_tag.id)
        )

        await session.delete(db_tag)
        await session.commit()
        return db_tag
