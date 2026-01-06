from decimal import Decimal
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import delete, func, inspect, select
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

    async def get_by_id_or_fail(self, product_id: int) -> Product:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.categories))
        )
        res = await self.session.execute(stmt)
        product = res.scalar_one_or_none()
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        return product

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

    async def list_with_filters(
        self,
        *,
        page: int,
        limit: int,
        q: str | None = None,
        category_id: int | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort: str | None = None,
    ) -> tuple[int, Sequence[Product]]:
        stmt = select(Product).options(selectinload(Product.categories))
        if q:
            q = q.strip()
            if q:
                stmt = stmt.where(Product.name.ilike(f"%{q}%"))
        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)
        if category_id is not None:
            # stmt = stmt.join(Product.categories).where(Category.id == category_id)
            stmt = stmt.where(Product.categories.any(Category.id == category_id))
        if sort == "price":
            stmt = stmt.order_by(Product.price.asc(), Product.id.asc())
        elif sort == "-price":
            stmt = stmt.order_by(Product.price.desc(), Product.id.asc())
        else:
            stmt = stmt.order_by(Product.created_at.desc())
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = (await self.session.execute(count_stmt)).scalar_one()
        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        items = res.scalars().all()
        return (total, items)

    async def create_with_categories(
        self,
        *,
        name: str,
        price: Decimal,
        category_ids: list[int] | None = None,
    ) -> Product:
        product = Product(name=name, price=price)
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        if category_ids is not None:
            categories_stmt = select(Category).where(Category.id.in_(category_ids))
            categories_res = await self.session.execute(categories_stmt)
            categories = categories_res.scalars().all()
            if len(categories) != len(category_ids):
                raise HTTPException(
                    detail="at least one id in categories ids is not valid",
                    status_code=status.HTTP_409_CONFLICT,
                )
        else:
            categories = []
        await self.sync_categories(product=product, categories=categories)
        await self.session.refresh(product)
        return await self.get_by_id_or_fail(product.id)

    async def update_with_categories(
        self,
        *,
        product: Product,
        name: str | None = None,
        price: Decimal | None = None,
        category_ids: list[int] | None = None,
    ) -> Product:
        assert inspect(product).persistent
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if category_ids is not None:
            categories_stmt = select(Category).where(Category.id.in_(category_ids))
            categories_res = await self.session.execute(categories_stmt)
            categories = categories_res.scalars().all()
            if len(categories) != len(category_ids):
                raise HTTPException(
                    detail="at least one id in categories ids is not valid",
                    status_code=status.HTTP_409_CONFLICT,
                )
            await self.sync_categories(product=product, categories=categories)
        await self.session.flush()
        await self.session.refresh(product)
        return await self.get_by_id_or_fail(product.id)

    async def delete(self, *, product: Product) -> None:
        assert inspect(product).persistent
        await self.session.delete(product)
