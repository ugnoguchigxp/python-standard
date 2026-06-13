import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_documents_flow(client: AsyncClient):
    # 1. Register and login
    await client.post("/api/auth/register", json={"email": "pgv@example.com", "password": "password123"})
    login = await client.post("/api/auth/login", data={"username": "pgv@example.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # 2. Add document
    res_add = await client.post("/api/documents/?content=FastAPI+Vector+Store", headers=headers)
    assert res_add.status_code == 201
    assert res_add.json()["content"] == "FastAPI Vector Store"

    # 3. Search
    res_search = await client.get("/api/documents/search?query=FastAPI", headers=headers)
    assert res_search.status_code == 200
    assert len(res_search.json()) > 0
    assert res_search.json()[0]["content"] == "FastAPI Vector Store"
