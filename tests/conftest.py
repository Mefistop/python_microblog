from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from db.database import get_async_session
from main import Base, app
import asyncio
from db.models import User, Publication, Followers, Like, Attachments

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(DATABASE_URL)
test_async_session = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)
Base.metadata.bind = test_engine


async def override_get_async_session():
    async with test_async_session() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="session", autouse=True)
async def setup_database(async_session):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    user1 = User(name='user1')
    user2 = User(name='user2')
    user3 = User(name='user3')
    async_session.add_all([user1, user2, user3])
    await async_session.commit()

    publication1 = Publication(content='Publication 1', author_id=user1.id)
    publication2 = Publication(content='Publication 2', author_id=user2.id)
    publication3 = Publication(content='Publication 3', author_id=user3.id)
    async_session.add_all([publication1, publication2, publication3])
    await async_session.commit()

    follower1 = Followers(author_id=user1.id, follower_id=user2.id)
    follower2 = Followers(author_id=user1.id, follower_id=user3.id)
    async_session.add_all([follower1, follower2])
    await async_session.commit()

    # создаем лайки
    like1 = Like(publication_id=publication1.id, author_id=user1.id, is_liked=True)
    like2 = Like(publication_id=publication2.id, author_id=user2.id, is_liked=True)
    async_session.add_all([like1, like2])
    await async_session.commit()

    # создаем вложения
    attachment1 = Attachments(link='link1', publication_id=publication1.id)
    attachment2 = Attachments(link='link2', publication_id=publication2.id)
    attachment3 = Attachments(link='link3', publication_id=publication3.id)
    async_session.add_all([attachment1, attachment2, attachment3])
    await async_session.commit()
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="session")
async def async_session():
    async with test_async_session() as session:
        yield session
