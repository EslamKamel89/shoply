import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_logout_revokes_refresh_token(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={"email": "logout@example.com", "password": "Password123"},
    )

    login = await async_client.post(
        "/auth/token",
        json={"email": "logout@example.com", "password": "Password123"},
    )
    refresh = login.json()["refresh_token"]

    await async_client.post("/auth/logout", json={"refresh_token": refresh})

    res = await async_client.post(
        "/auth/refresh",
        json={"refresh_token": refresh},
    )

    assert res.status_code == 401
