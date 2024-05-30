from httpx import AsyncClient


async def test_add_user(async_client: AsyncClient):
    request_data = {"name": "Test"}
    response = await async_client.post("/api/user", json=request_data)
    assert response.status_code == 200
    assert "result" in response.json()


async def test_add_tweet(async_client: AsyncClient):
    request_data = {"tweet_data": "Test and test"}
    headers = {"api-key": "test"}
    response = await async_client.post(
        "/api/tweets", json=request_data, headers=headers
    )
    assert response.status_code == 200
    assert "result" in response.json()


async def test_delete_tweet(async_client: AsyncClient):
    headers = {"api-key": "test"}
    response = await async_client.delete("/api/tweets/1", headers=headers)
    assert response.status_code == 200
    assert "result" in response.json()


async def test_add_like_to_tweet(async_client: AsyncClient):
    headers = {"api-key": "test"}
    response = await async_client.post("/api/tweets/3/likes", headers=headers)
    assert response.status_code == 200
    assert "result" in response.json()


async def test_delete_tweet_like(async_client: AsyncClient):
    headers = {"api-key": "test"}
    response = await async_client.delete(
        "/api/tweets/3/likes",
        headers=headers,
    )
    assert response.status_code == 200
    assert "result" in response.json()


async def test_add_follower(async_client: AsyncClient):
    headers = {"api-key": "test2"}
    response = await async_client.post("/api/users/3/follow", headers=headers)
    assert response.status_code == 200
    assert "result" in response.json()


async def test_delete_follower(async_client: AsyncClient):
    headers = {"api-key": "test3"}
    response = await async_client.delete(
        "/api/users/1/follow",
        headers=headers,
    )
    assert response.status_code == 200
    assert "result" in response.json()


async def test_get_all_tweets(async_client: AsyncClient):
    headers = {"api-key": "test"}
    response = await async_client.get("/api/tweets", headers=headers)
    assert response.status_code == 200
    assert "result" in response.json()


async def test_get_yourself_profile_info(async_client: AsyncClient):
    headers = {"api-key": "test"}
    response = await async_client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    assert "result" in response.json()


async def test_get_user_profile_info(async_client: AsyncClient):
    headers = {"api-key": "test"}
    response = await async_client.get("/api/users/2", headers=headers)
    assert response.status_code == 200
    assert "result" in response.json()
