from sqlalchemy import Column, Integer, String, exc, select
from sqlalchemy.orm import relationship

from app.db import SessionLocal
from app.errors.tag import TagNotFoundError
from app.repos.base import Base
from app.repos.snippet import snippet_tags
from app.schemas.tag import TagCreate, TagUpdate


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    snippets = relationship("Snippet", secondary=snippet_tags, back_populates="tags")

    @classmethod
    def get_by_id(cls, session: SessionLocal, id: int) -> "Tag":
        try:
            return (session.execute(select(Tag).filter(Tag.id == id))).scalar_one()
        except exc.NoResultFound:
            raise TagNotFoundError

    @classmethod
    def get_all(cls, session: SessionLocal) -> list["Tag"]:
        return (session.execute(select(Tag))).scalars().all()

    @classmethod
    def create(cls, session: SessionLocal, tag: TagCreate) -> "Tag":
        db_tag = Tag(name=tag.name)
        session.add(db_tag)
        session.commit()
        session.refresh(db_tag)
        return db_tag

    @classmethod
    def update(cls, session: SessionLocal, id: int, tag: TagUpdate) -> "Tag":
        try:
            db_tag = (session.execute(select(Tag).filter(Tag.id == id))).scalar_one()
        except exc.NoResultFound:
            raise TagNotFoundError
        db_tag.name = tag.name
        session.commit()
        session.refresh(db_tag)
        return db_tag

    @classmethod
    def delete(cls, session: SessionLocal, id: int) -> "Tag":
        try:
            db_tag = (session.execute(select(Tag).filter(Tag.id == id))).scalar_one()
        except exc.NoResultFound:
            raise TagNotFoundError
        session.delete(db_tag)
        session.commit()
        return db_tag
