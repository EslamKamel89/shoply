from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.apps.products.models import Category, Product, ProductCategory


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.categories))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Product]:
        stmt = (
            select(Product)
            .where(Product.name == name)
            .options(selectinload(Product.categories))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_all(self) -> Sequence[Product]:
        stmt = select(Product).options(selectinload(Product.categories))
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def create(self, *, name: str, price: Decimal) -> Product:
        product = Product(name=name, price=price)
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def sync_categories(
        self, *, product: Product, categories: Sequence[Category]
    ):
        self.session.add_all([product, *categories])
        await self.session.flush()
        await self.session.execute(
            delete(ProductCategory).where(ProductCategory.product_id == product.id)
        )
        for category in categories:
            self.session.add(
                ProductCategory(product_id=product.id, category_id=category.id)
            )
        await self.session.flush()
