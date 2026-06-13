import sys
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

# Stub workers and asgi before importing main app
sys.modules["workers"] = MagicMock()
sys.modules["asgi"] = MagicMock()

from app.main import app  # noqa: E402


@pytest.mark.asyncio
async def test_liveness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
