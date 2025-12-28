from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from src.app.apps.orders.models import OrderItem


class Category(Base, IdMixin, TimestampMixin):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(
        String(255), index=True, unique=True, nullable=False
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="categories", secondary="product_category"
    )


class Product(Base, IdMixin, TimestampMixin):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(
        String(255), index=True, unique=True, nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    categories: Mapped[list["Category"]] = relationship(
        "Category", back_populates="products", secondary="product_category"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product", passive_deletes=True
    )


class ProductCategory(Base, TimestampMixin):
    __tablename__ = "product_category"
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )
