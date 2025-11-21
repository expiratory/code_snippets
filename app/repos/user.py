from sqlalchemy import Boolean, Column, DateTime, Integer, String, exc, select
from sqlalchemy.sql import func

from app.db import SessionLocal
from app.errors.auth import UserAlreadyExistsError, UserNotFoundError
from app.repos.base import Base
from app.schemas.user import UserCreate


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    @classmethod
    async def get_by_email(cls, session: SessionLocal, email: str) -> "User":
        try:
            result = await session.execute(select(User).filter(User.email == email))
            return result.scalar_one()
        except exc.NoResultFound:
            return None

    @classmethod
    async def get_by_id(cls, session: SessionLocal, id: int) -> "User":
        try:
            result = await session.execute(select(User).filter(User.id == id))
            return result.scalar_one()
        except exc.NoResultFound:
            raise UserNotFoundError

    @classmethod
    async def create(
        cls, session: SessionLocal, user: UserCreate, hashed_password: str
    ) -> "User":
        if await cls.get_by_email(session, user.email):
            raise UserAlreadyExistsError(f"Email {user.email} already registered")

        db_user = User(
            email=user.email, username=user.username, hashed_password=hashed_password
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    @classmethod
    async def update_password(
        cls, session: SessionLocal, user_id: int, hashed_password: str
    ) -> "User":
        user = await cls.get_by_id(session, user_id)
        user.hashed_password = hashed_password
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
