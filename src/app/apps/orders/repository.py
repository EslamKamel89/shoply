from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.apps.orders.models import Order, OrderItem


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, user_id: int) -> Order:
        order = Order(user_id=user_id)
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def add_item(
        self, *, order: Order, product_id: int, quantity: int, unit_price: Decimal
    ) -> OrderItem:
        item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        self.session.add_all([order, item])
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_for_user(self, user_id) -> Sequence[Order]:
        stmt = select(Order).where(Order.user_id == user_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()
