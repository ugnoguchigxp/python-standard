import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpassword123"


async def test_auth_flow(client: AsyncClient):
    # 1. Register a new user
    reg_response = await client.post(
        "/api/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["email"] == TEST_EMAIL
    assert "id" in reg_data
    assert reg_data["is_active"] is True
    assert "hashed_password" not in reg_data  # Ensure sensitive data is not leaked

    # 2. Login
    login_response = await client.post(
        "/api/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    token = login_data["access_token"]

    # 3. Retrieve profile /me (unauthorized)
    me_unauth = await client.get("/api/auth/me")
    assert me_unauth.status_code == 401

    # 4. Retrieve profile /me (authorized)
    headers = {"Authorization": f"Bearer {token}"}
    me_auth = await client.get("/api/auth/me", headers=headers)
    assert me_auth.status_code == 200
    me_data = me_auth.json()
    assert me_data["email"] == TEST_EMAIL

    # 5. Refresh token
    refresh_response = await client.post("/api/auth/refresh", headers=headers)
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert refresh_data["access_token"] != token
