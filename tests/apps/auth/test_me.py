import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_me_with_valid_token(async_client: AsyncClient):
    await async_client.post(
        "/auth/register", json={"email": "me@example.com", "password": "Password123"}
    )
    login = await async_client.post(
        "/auth/token", json={"email": "me@example.com", "password": "Password123"}
    )
    token = login.json()["access_token"]
    res = await async_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json().get("email") == "me@example.com"


@pytest.mark.anyio
async def test_me_without_token(async_client: AsyncClient):
    res = await async_client.get("/auth/me")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
