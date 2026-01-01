from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.apps.auth.models import User
from src.app.apps.orders.repository import OrderRepository
from src.app.apps.products.models import Product
from src.app.apps.products.repository import ProductRepository
from src.app.core.security import Security


@pytest.mark.anyio
async def test_create_order_and_add_item(
    session: AsyncSession, user: User, product: Product
):
    order_repo = OrderRepository(session)

    order = await order_repo.create(user_id=user.id)
    item = await order_repo.add_item(
        order=order, product_id=product.id, quantity=1, unit_price=product.price
    )
    assert order.id is not None
    assert item.id is not None
    assert item.quantity == 1
    assert item.unit_price == Decimal("9.99")


# @pytest.mark.anyio
# async def test_list_order_for_user(session:AsyncSession) :
