import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_refresh_token_rotation(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={"email": "refresh@example.com", "password": "Password123"},
    )

    login = await async_client.post(
        "/auth/token",
        json={"email": "refresh@example.com", "password": "Password123"},
    )
    old_refresh = login.json()["refresh_token"]
    res = await async_client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["refresh_token"] != old_refresh
    assert "access_token" in data


@pytest.mark.anyio
async def test_refresh_token_reuse_fails(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={"email": "reuse@example.com", "password": "Password123"},
    )

    login = await async_client.post(
        "/auth/token",
        json={"email": "reuse@example.com", "password": "Password123"},
    )
    refresh = login.json()["refresh_token"]

    await async_client.post("/auth/refresh", json={"refresh_token": refresh})
    res = await async_client.post("/auth/refresh", json={"refresh_token": refresh})

    assert res.status_code == 401
