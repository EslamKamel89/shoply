from __future__ import annotations

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

import src.app.apps.auth.models
import src.app.apps.orders.models
import src.app.apps.products.models
from src.app.core.deps import get_db_session
from src.app.db.base import Base
from src.app.db.session import Database
from src.app.main import create_app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    test_db = Database("sqlite+aiosqlite:///:memory:")
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app = create_app()

    async def _get_test_db_session():
        async for session in test_db.get_session():
            yield session

    app.dependency_overrides[get_db_session] = _get_test_db_session
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
        await test_db.dispose()


@pytest.fixture
async def session():
    test_db = Database("sqlite+aiosqlite:///:memory:")
    async with test_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async for session in test_db.get_session():
        yield session
    await test_db.dispose()


pytest_plugins = [
    "tests.fixtures.user",
    "tests.fixtures.product",
]
