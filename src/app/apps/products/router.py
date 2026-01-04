from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.apps.products.repository import ProductRepository
from src.app.apps.products.schemas import Page, ProductResponse
from src.app.core.deps import get_db_session

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=Page[ProductResponse])
async def list_products(
    q: str | None = None,
    category_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = ProductRepository(session)

    total, products = await repo.list_with_filters(
        q=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        limit=limit,
    )
    items = [ProductResponse.model_validate(p) for p in products]
    return Page(total=total, page=page, limit=limit, items=items)
