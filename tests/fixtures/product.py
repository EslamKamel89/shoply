from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.apps.auth.models import User
from src.app.apps.products.repository import ProductRepository
from src.app.core.security import Security


@pytest.fixture
async def product(session: AsyncSession):
    product_repo = ProductRepository(session)
    product = await product_repo.create(name="test", price=Decimal(9.99))
    session.add(product)
    await session.flush()
    return product
