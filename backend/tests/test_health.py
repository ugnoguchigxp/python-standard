import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_liveness(client: AsyncClient):
    response = await client.get("/api/health/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


async def test_readiness(client: AsyncClient):
    response = await client.get("/api/health/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert "timestamp" in data
