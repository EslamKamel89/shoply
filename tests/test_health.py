import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_endpoint(async_client: AsyncClient) -> None:
    res = await async_client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
