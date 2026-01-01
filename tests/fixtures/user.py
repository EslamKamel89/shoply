import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.apps.auth.models import User
from src.app.core.security import Security


@pytest.fixture
async def user(session: AsyncSession):
    user = User(
        email="test@example.com", password_hash=Security.hash_password("password")
    )
    session.add(user)
    await session.flush()
    return user
