from sqlalchemy import Column, ForeignKey, Integer, String, Table, exc, select
from sqlalchemy.orm import relationship, selectinload

from app.db import SessionLocal
from app.repos.base import Base
from app.schemas.snippet import SnippetCreate, SnippetUpdate
from app.errors.snippet import SnippetNotFoundError

snippet_tags = Table(
    "snippet_tags",
    Base.metadata,
    Column("snippet_id", Integer, ForeignKey("snippets.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Snippet(Base):
    __tablename__ = "snippets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    code = Column(String)
    language = Column(String)
    tags = relationship("Tag", secondary=snippet_tags, back_populates="snippets")

    @classmethod
    def get_by_id(cls, session: SessionLocal, id: int) -> "Snippet":
        try:
            return (
                session.execute(
                    select(Snippet)
                    .filter(Snippet.id == id)
                    .options(selectinload(Snippet.tags))
                )
            ).scalar_one()
        except exc.NoResultFound:
            raise SnippetNotFoundError

    @classmethod
    def get_all(cls, session: SessionLocal) -> list["Snippet"]:
        return (
            (session.execute(select(Snippet).options(selectinload(Snippet.tags))))
            .scalars()
            .all()
        )

    @classmethod
    def create(cls, session: SessionLocal, snippet: SnippetCreate) -> "Snippet":
        db_snippet = Snippet(
            title=snippet.title, code=snippet.code, language=snippet.language
        )
        session.add(db_snippet)
        session.commit()
        session.refresh(db_snippet)
        return db_snippet

    @classmethod
    def update(
        cls, session: SessionLocal, id: int, snippet: SnippetUpdate
    ) -> "Snippet":
        try:
            db_snippet = (
                session.execute(
                    select(Snippet)
                    .filter(Snippet.id == id)
                    .options(selectinload(Snippet.tags))
                )
            ).scalar_one()
        except exc.NoResultFound:
            raise SnippetNotFoundError
        db_snippet.title = snippet.title
        db_snippet.code = snippet.code
        db_snippet.language = snippet.language
        session.commit()
        session.refresh(db_snippet)
        return db_snippet

    @classmethod
    def delete(cls, session: SessionLocal, id: int) -> "Snippet":
        try:
            db_snippet = (
                session.execute(
                    select(Snippet)
                    .filter(Snippet.id == id)
                    .options(selectinload(Snippet.tags))
                )
            ).scalar_one()
        except exc.NoResultFound:
            raise SnippetNotFoundError
        session.delete(db_snippet)
        session.commit()
        return db_snippet
