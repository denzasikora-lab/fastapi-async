import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.dependency import get_db
from main import app

# SQLite test database connection URL (async)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)

TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

async def get_test_db():
    async with TestSessionLocal() as db:
        yield db

# Override get_db dependency for all tests
app.dependency_overrides[get_db] = get_test_db

@pytest_asyncio.fixture()
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestSessionLocal() as db:
        yield db

