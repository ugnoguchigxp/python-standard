from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_db
from app.main import app

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

test_session_maker = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
async def init_test_db():
    """Create all tables before testing and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields a test database session transactionally isolated."""
    async with test_session_maker() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Yields an HTTP client connected to the application with overridden DB session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Using modern httpx ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
