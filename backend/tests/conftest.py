import asyncio
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.infrastructure.database import Base, DATABASE_URL
from src.infrastructure.auth.models import UserORM
from src.infrastructure.workspace.models import WorkspaceORM, WorkspaceMemberORM

# Use a test database URL
database_name = "wiselab_test"
if "wiselab_test" not in DATABASE_URL:
    TEST_DATABASE_URL = DATABASE_URL.replace("wiselab", database_name)
else:
    TEST_DATABASE_URL = DATABASE_URL

base_url = TEST_DATABASE_URL.rsplit("/", 1)[0]
ADMIN_DATABASE_URL = f"{base_url}/postgres"

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    engine = create_async_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'"))
        if not result.scalar():
            await conn.execute(text(f"CREATE DATABASE {database_name}"))
    await engine.dispose()

from src.infrastructure.budget.models.category import CategoryORM
import uuid

@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
        # Seed default categories for tests
        default_categories = [
            {"id": uuid.uuid4(), "name": "Housing", "is_default": True},
            {"id": uuid.uuid4(), "name": "Food", "is_default": True},
            {"id": uuid.uuid4(), "name": "Transportation", "is_default": True},
            {"id": uuid.uuid4(), "name": "Entertainment", "is_default": True},
            {"id": uuid.uuid4(), "name": "Utilities", "is_default": True},
        ]
        await conn.execute(CategoryORM.__table__.insert(), default_categories)
    
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
