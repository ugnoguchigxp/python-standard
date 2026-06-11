import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

USER1_EMAIL = "user1@example.com"
USER2_EMAIL = "user2@example.com"
PASSWORD = "password123"


async def test_item_crud_and_access_control(client: AsyncClient):
    # 1. Register two users
    res1 = await client.post(
        "/api/auth/register", json={"email": USER1_EMAIL, "password": PASSWORD}
    )
    res2 = await client.post(
        "/api/auth/register", json={"email": USER2_EMAIL, "password": PASSWORD}
    )
    assert res1.status_code == 201
    assert res2.status_code == 201
    user1_id = res1.json()["id"]

    # 2. Login User 1
    log1 = await client.post(
        "/api/auth/login", data={"username": USER1_EMAIL, "password": PASSWORD}
    )
    token1 = log1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 3. Login User 2
    log2 = await client.post(
        "/api/auth/login", data={"username": USER2_EMAIL, "password": PASSWORD}
    )
    token2 = log2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 4. User 1 creates an item
    create_res = await client.post(
        "/api/items/",
        json={"title": "Item 1", "description": "User 1 Item"},
        headers=headers1,
    )
    # Ah! Let's check path in main.py:
    # app.include_router(items.router, prefix=f"{settings.API_V1_STR}/items", tags=["items"])
    # Yes, prefix is /api/items. So path is /api/items/.
    assert create_res.status_code == 201
    item = create_res.json()
    item_id = item["id"]
    assert item["title"] == "Item 1"
    assert item["owner_id"] == user1_id

    # 5. User 1 lists items (should see Item 1)
    list_res1 = await client.get("/api/items/", headers=headers1)
    assert list_res1.status_code == 200
    assert len(list_res1.json()) == 1
    assert list_res1.json()[0]["id"] == item_id

    # 6. User 2 lists items (should NOT see Item 1, since User 2 has no items)
    list_res2 = await client.get("/api/items/", headers=headers2)
    assert list_res2.status_code == 200
    assert len(list_res2.json()) == 0

    # 7. User 2 tries to fetch User 1's item (should fail with 403)
    get_res2 = await client.get(f"/api/items/{item_id}", headers=headers2)
    assert get_res2.status_code == 403

    # 8. User 2 tries to update User 1's item (should fail with 403)
    put_res2 = await client.put(
        f"/api/items/{item_id}", json={"title": "Hacked"}, headers=headers2
    )
    assert put_res2.status_code == 403

    # 9. User 1 updates their own item
    put_res1 = await client.put(
        f"/api/items/{item_id}", json={"title": "Updated Item 1"}, headers=headers1
    )
    assert put_res1.status_code == 200
    assert put_res1.json()["title"] == "Updated Item 1"

    # 10. User 2 tries to delete User 1's item (should fail with 403)
    del_res2 = await client.delete(f"/api/items/{item_id}", headers=headers2)
    assert del_res2.status_code == 403

    # 11. User 1 deletes their own item
    del_res1 = await client.delete(f"/api/items/{item_id}", headers=headers1)
    assert del_res1.status_code == 200

    # 12. Try to get deleted item (should fail with 404)
    get_del = await client.get(f"/api/items/{item_id}", headers=headers1)
    assert get_del.status_code == 404
