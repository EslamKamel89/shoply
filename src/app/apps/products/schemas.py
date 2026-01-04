from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    price: Decimal = Field(gt=0)
    category_ids: list[int] = []


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    price: Decimal | None = Field(default=None, gt=0)
    category_ids: list[int] | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_encoders={Decimal: lambda v: str(v)}
    )
    id: int
    name: str
    price: Decimal
    categories: list[CategoryResponse]
    created_at: datetime
    updated_at: datetime


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total: int
    page: int
    limit: int
    items: list[T]
