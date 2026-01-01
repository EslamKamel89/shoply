from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.apps.products.models import Category
from src.app.apps.products.repository import ProductRepository


@pytest.mark.anyio
async def test_create_product(session: AsyncSession):
    repo = ProductRepository(session)
    product = await repo.create(
        name="MacBook Pro",
        price=Decimal("2499.99"),
    )
    await session.commit()
    assert product.id is not None
    assert product.name == "MacBook Pro"
    assert product.price == Decimal("2499.99")


@pytest.mark.anyio
async def test_product_category_test(session: AsyncSession):
    repo = ProductRepository(session)
    product = await repo.create(
        name="iPhone",
        price=Decimal("999.00"),
    )
    cat1 = Category(name="Phones")
    cat2 = Category(name="Electronics")
    await repo.sync_categories(product=product, categories=[cat1, cat2])
    refreshed = await repo.get_by_id(product.id)
    assert refreshed is not None
    assert len(refreshed.categories) == 2
