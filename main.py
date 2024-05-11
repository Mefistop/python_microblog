from contextlib import asynccontextmanager
from db.models import User, Publication, Followers, Like
from db.database import Base, async_session, engine
from fastapi import FastAPI, Depends, Body, Header, UploadFile, File, Path
import uvicorn
from sqlalchemy.future import select
from fastapi.exceptions import HTTPException
from sqlalchemy.sql import text
from sqlalchemy.orm import joinedload



async def get_async_session():
    async with async_session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(
            text("PRAGMA foreign_keys = ON;"),
            execution_options={"isolation_level": "AUTONOMOUS"}
        )
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_session.close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


@app.post('/api/user', response_model=None)
async def add_new_useer(user: dict = Body(...), session=Depends(get_async_session)):
    """Для добавления юзера, потом переделаю"""
    new_user = User(**user)
    session.add(new_user)
    await session.commit()
    return {"result": True, "author_id": new_user.id}


@app.post("/api/tweets", response_model=None)
async def add_tweet(
        api_key: str = Header(...),
        tweet: dict = Body(...),
        session=Depends(get_async_session),
):
    """Для добавления публикации"""
    new_tweet = Publication(**{"author_id": api_key, "content": tweet["tweet_data"]})
    session.add(new_tweet)
    await session.commit()
    return {"result": True, "tweet_id": new_tweet.id}


@app.post("api/medias", response_model=None)
async def add_media(
        api_key: str = Header(...),
        file: UploadFile = File(...),
        session=Depends(get_async_session),
):
    pass


@app.delete("/api/tweets/{id}", response_model=None)
async def delete_tweet(
        api_key: str = Header(...),
        id: str = Path(...),
        session=Depends(get_async_session)
):
    """Для удаление твита автора, проверяет принадлежит ли твит автору"""
    author_id = api_key
    tweet_id = id
    tweet_by_author_id_tweet_id = await session.execute(select(Publication).where(
        Publication.author_id == author_id,
        Publication.id == tweet_id)
    )
    tweet_to_delete = tweet_by_author_id_tweet_id.scalar()
    if tweet_to_delete:
        await session.delete(tweet_to_delete)
        await session.commit()
        return {"result": True}
    else:
        raise HTTPException(status_code=404, detail="Tweet not found")


@app.post("/api/tweets/{tweet_id}/likes", response_model=None)
async def add_like_to_tweet(
        api_key: str = Header(...),
        tweet_id: str = Path(...),
        session=Depends(get_async_session),
):
    """Для добавления like твиту, проверка существует ли на самом деле твит,
    не пытаемся ли лайкнуть уже залайканный нами твит"""
    author_id = api_key
    tweet_id = tweet_id
    tweet = await session.get(Publication, tweet_id)
    if tweet:
        like_tweet = await session.execute(select(Like).where(
            Like.publication_id == tweet_id,
            Like.author_id == author_id)
        )
        if not like_tweet.scalar():
            new_like_tweet = Like(**{"author_id": author_id, "publication_id": tweet_id, "is_liked": True})
            session.add(new_like_tweet)
            await session.commit()
            return {"result": True}
        raise HTTPException(status_code=404, detail="Tweet already like")
    raise HTTPException(status_code=404, detail="Tweet not found")


@app.delete("/api/tweets/{tweet_id}/likes", response_model=None)
async def delete_like_to_tweet(
        api_key: str = Header(...),
        tweet_id: str = Path(...),
        session=Depends(get_async_session),
):
    """Для удаления like твиту, проверка существует ли на самом деле твит и лайкал ли его автор"""
    author_id = api_key
    tweet_id = tweet_id
    like_tweet = await session.execute(select(Like).where(
        Like.publication_id == tweet_id,
        Like.author_id == author_id)
    )
    like_tweet = like_tweet.scalar()
    if like_tweet:
        await session.delete(like_tweet)
        await session.commit()
        return {"result": True}
    raise HTTPException(status_code=404, detail="Tweet by like not found")


@app.post("/api/users/{user_id}/follow", response_model=None)
async def follow_on_user(
        api_key: str = Header(...),
        user_id: str = Path(...),
        session=Depends(get_async_session),
):
    """Для доабвления подписки на других авторовб проверка существует ли автор, не подписаны ли мы уже,
    не пытаемся ли мы подписаться на самого себя"""
    author_id = api_key
    follow_author = user_id
    if author_id == follow_author:
        raise HTTPException(status_code=404, detail="You can't subscribe to yourself")
    subscibe = await session.execute(select(Followers).where(
        Followers.author_id == follow_author,
        Followers.follower_id == author_id),
    )
    subscibe = subscibe.scalar()
    if not subscibe:
        author = await session.get(User, follow_author)
        if author:
            new_subscribe = Followers(author_id=follow_author, follower_id=author_id)
            session.add(new_subscribe)
            await session.commit()
            return {"result": True}
        raise HTTPException(status_code=404, detail="Author not exist")
    raise HTTPException(status_code=404, detail="Subscribe already exist")


@app.delete("/api/users/{user_id}/follow", response_model=None)
async def delete_follow(
        api_key: str = Header(...),
        user_id: str = Path(...),
        session=Depends(get_async_session),
):
    """Для удаления подписки на других авторов, проверка существует ли автор, не подписаны ли мы уже,
    не пытаемся ли мы подписаться на самого себя"""
    author_id = api_key
    follow_author = user_id
    subscibe = await session.execute(select(Followers).where(
        Followers.author_id == follow_author,
        Followers.follower_id == author_id),
    )
    subscibe = subscibe.scalar()
    if subscibe:
        await session.delete(subscibe)
        await session.commit()
        return {"result": True}
    raise HTTPException(status_code=404, detail="Subscribe not exist")


@app.get("/api/tweets", response_model=None)
async def get_all_tweets(
        api_key: str = Header(...),
        session=Depends(get_async_session),
):

    author_id = api_key
    author_by_tweet = await session.get(User, author_id)
    subscriptions = await session.execute(select(Followers).where(Followers.follower_id == author_id))
    authors_idx = [author_id]
    for subscription in subscriptions:
        authors_idx.append(subscription[0].author_id)
    print(authors_idx)
    tweets_by_author = await session.execute(select(Publication).where(Publication.author_id.in_(authors_idx)))
    list_of_tweets = []
    for row in tweets_by_author:
        tweet = row[0]
        data_author = await session.execute(select(User).where(User.id == tweet.author_id))

        # data_authors = tweet.author.to_dict()
        data_tweet = {"id": tweet.id, "content": tweet.content, "attachments": [],
                      "likes": [], "authors": data_author.first()[0].to_dict()}
        # print(data_tweet)
        # print(data_authors)
        tweets_by_like = await session.execute(select(Like).where(Like.publication_id == tweet.id))
        # print(tweets_by_like)
        for row in tweets_by_like:
            like = row[0]
            data_tweet["likes"].append({"user_id": like.author_id, "name": like.author.name})
        # print(data_tweet)
        list_of_tweets.append(data_tweet)
    data_by_all_tweets = {"result": True, "tweets": list_of_tweets}
    return data_by_all_tweets


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
