import pytest
from httpx import AsyncClient
from main import Base, app, get_async_session
import asyncio
from db.models import User, Publication, Followers, Like, Attachments

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(DATABASE_URL)
test_async_session = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
Base.metadata.bind = test_engine


async def override_get_async_session():
    async with test_async_session() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


async def make_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session() as session:

        # создаем пользователей
        user1 = User(name='user1')
        user2 = User(name='user2')
        user3 = User(name='user3')
        session.add_all([user1, user2, user3])
        await session.commit()

        # создаем публикации
        publication1 = Publication(content='Publication 1', author_id=user1.id)
        publication2 = Publication(content='Publication 2', author_id=user2.id)
        publication3 = Publication(content='Publication 3', author_id=user3.id)
        session.add_all([publication1, publication2, publication3])
        await session.commit()

        # создаем подписки
        follower1 = Followers(author_id=user1.id, follower_id=user2.id)
        follower2 = Followers(author_id=user1.id, follower_id=user3.id)
        session.add_all([follower1, follower2])
        await session.commit()

        # создаем лайки
        like1 = Like(publication_id=publication1.id, author_id=user1.id, is_liked=True)
        like2 = Like(publication_id=publication2.id, author_id=user2.id, is_liked=True)
        session.add_all([like1, like2])
        await session.commit()

        # создаем вложения
        attachment1 = Attachments(link='link1', publication_id=publication1.id)
        attachment2 = Attachments(link='link2', publication_id=publication2.id)
        attachment3 = Attachments(link='link3', publication_id=publication3.id)
        session.add_all([attachment1, attachment2, attachment3])
        await session.commit()


asyncio.run(make_db())


@pytest.mark.asyncio
async def test_add_user():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    request_data = {"name": "Test"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/user", json=request_data)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_add_tweet():
    request_data = {"tweet_data": "Test and test"}
    headers = {"api-key": "1"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/tweets", json=request_data, headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_delete_tweet():
    headers = {"api-key": "1"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/tweets/1", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_add_like_to_tweet():
    headers = {"api-key": "1"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/tweets/3/likes", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_delete_tweet():
    headers = {"api-key": "1"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/tweets/1/likes", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_add_follower():
    headers = {"api-key": "2"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/users/3/follow", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_delete_follower():
    headers = {"api-key": "3"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/users/1/follow", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_delete_follower():
    headers = {"api-key": "3"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/users/1/follow", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_get_all_tweets():
    headers = {"api-key": "1"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/tweets", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_get_yourself_profile_info():
    headers = {"api-key": "1"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()


@pytest.mark.asyncio
async def test_get_user_profile_info():
    headers = {"api-key": "1"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/users/2", headers=headers)
        assert response.status_code == 200
        assert "result" in response.json()

