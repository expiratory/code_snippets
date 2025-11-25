from typing import AsyncGenerator

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from app.config import settings
from app.db import get_db
from app.limiter import limiter
from app.main import app
from app.repos.base import Base

# Disable rate limiting for tests
limiter.enabled = False

TEST_DB_NAME = "test_db"


def get_test_db_url(url: str, db_name: str) -> str:
    u = make_url(url)
    u = u.set(database=db_name)
    return u.render_as_string(hide_password=False)


def get_admin_db_url(url: str) -> str:
    u = make_url(url)
    u = u.set(drivername="postgresql", database="postgres")
    return u.render_as_string(hide_password=False)


TEST_DB_URL = get_test_db_url(settings.DB_URL, TEST_DB_NAME)
ADMIN_DB_URL = get_admin_db_url(settings.DB_URL)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Creates a fresh test database and runs migrations.
    """
    engine = create_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")

    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    original_url = settings.DB_URL
    settings.DB_URL = TEST_DB_URL

    try:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
        command.upgrade(alembic_cfg, "head")
        yield
    finally:
        settings.DB_URL = original_url
        with engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Create engine per test to avoid loop issues with asyncpg
    engine = create_async_engine(TEST_DB_URL, pool_pre_ping=True)
    TestingSessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with TestingSessionLocal() as session:
        # Clean up database before each test
        tables = [t.name for t in Base.metadata.sorted_tables]
        if tables:
            stmt = f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE"
            await session.execute(text(stmt))
            await session.commit()

        yield session

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
