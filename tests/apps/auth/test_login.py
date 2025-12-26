import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_login_success(async_client: AsyncClient):
    data = {"email": "user1@example.com", "password": "password123"}
    await async_client.post("/auth/register", json=data)
    res = await async_client.post("/auth/token", json=data)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_invalid_password(async_client: AsyncClient):
    data = {"email": "user1@example.com", "password": "password123"}
    await async_client.post("/auth/register", json=data)
    res = await async_client.post(
        "/auth/token", json={"email": data["email"], "password": "wrong_password123"}
    )
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
