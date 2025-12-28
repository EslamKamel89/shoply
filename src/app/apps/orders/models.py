from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from src.app.apps.auth.models import User
    from src.app.apps.products.models import Product


class Order(Base, IdMixin, TimestampMixin):
    __tablename__ = "orders"
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    user: Mapped[Optional["User"]] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base, IdMixin, TimestampMixin):
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    product: Mapped[Optional["Product"]] = relationship(
        "Product", back_populates="order_items", passive_deletes=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
