import asyncio
from db.models import User, Publication, Followers, Like, Attachments
from db.database import Base, async_session, engine


async def make_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:

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
        like3 = Like(publication_id=publication3.id, author_id=user3.id, is_liked=True)
        session.add_all([like1, like2, like3])
        await session.commit()

        # создаем вложения
        attachment1 = Attachments(link='link1', publication_id=publication1.id)
        attachment2 = Attachments(link='link2', publication_id=publication2.id)
        attachment3 = Attachments(link='link3', publication_id=publication3.id)
        session.add_all([attachment1, attachment2, attachment3])
        await session.commit()


if __name__ == '__main__':
    asyncio.run(make_db())