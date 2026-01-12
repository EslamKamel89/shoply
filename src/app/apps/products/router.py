from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.apps.products.helpers import log_after_response
from src.app.apps.products.repository import ProductRepository
from src.app.apps.products.schemas import (
    Page,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from src.app.core.deps import CurrentUser, admin_required, get_db_session

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/demo/background")
async def demo_background_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(log_after_response, "Hello from the background task")
    return {"status": "response send"}


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


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(admin_required),
):
    repo = ProductRepository(session)
    async with session.begin():
        product = await repo.create_with_categories(
            name=payload.name, price=payload.price, category_ids=payload.category_ids
        )
        return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(admin_required),
):
    repo = ProductRepository(session)
    async with session.begin():
        product = await repo.get_by_id(product_id)
        if product is None:
            raise HTTPException(
                detail="Product not found", status_code=status.HTTP_404_NOT_FOUND
            )
        product = await repo.update_with_categories(
            product=product,
            name=payload.name,
            price=payload.price,
            category_ids=payload.category_ids,
        )
        return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse)
async def product_details(
    product_id: int, session: AsyncSession = Depends(get_db_session)
):
    repo = ProductRepository(session)
    product = await repo.get_details_by_id(product_id)
    if product is None:
        raise HTTPException(
            detail="Product not found", status_code=status.HTTP_404_NOT_FOUND
        )
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(admin_required),
):
    repo = ProductRepository(session)
    async with session.begin():
        product = await repo.get_by_id(product_id)
        if product is None:
            raise HTTPException(
                detail="Product not found", status_code=status.HTTP_404_NOT_FOUND
            )
        await repo.delete(product=product)
        return None
