"""Shared pytest fixtures for fahimni test suite."""

from collections.abc import AsyncGenerator

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fahimni.db.base import Base
from fahimni.db.session import get_db
from fahimni.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://fahimni:fahimni@localhost:5433/fahimni_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


def _quote_ident(identifier: str) -> str:
    """Quote a PostgreSQL identifier safely for DDL statements."""
    return '"' + identifier.replace('"', '""') + '"'


async def _ensure_test_database_exists(database_url: str) -> None:
    """Create the configured test database if it is missing."""
    url = make_url(database_url)
    db_name = url.database
    if not db_name:
        raise ValueError("TEST_DATABASE_URL must include a database name")

    admin_url = url.set(drivername="postgresql", database="postgres")
    conn = await asyncpg.connect(str(admin_url))
    try:
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)
        if not exists:
            await conn.execute(f"CREATE DATABASE {_quote_ident(db_name)}")
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    await _ensure_test_database_exists(TEST_DATABASE_URL)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db_session(setup_database: None) -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def client_with_db(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()