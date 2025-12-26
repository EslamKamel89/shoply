from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_user_success(async_client: AsyncClient):
    payload: dict[str, Any] = {"email": "user1@example.com", "password": "password123"}
    res = await async_client.post("/auth/register", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "user"
    assert data["is_active"] == True
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_duplicate_emails_fails(async_client: AsyncClient):
    payload: dict[str, Any] = {"email": "user2@example.com", "password": "password123"}
    res1 = await async_client.post("/auth/register", json=payload)
    res2 = await async_client.post("/auth/register", json=payload)
    assert res2.status_code == status.HTTP_409_CONFLICT
