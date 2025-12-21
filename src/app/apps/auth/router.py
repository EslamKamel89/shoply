from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])
