import datetime
import os.path
from contextlib import asynccontextmanager
from db.models import User, Publication, Followers, Like, Attachments
from db.database import Base, async_session, engine
from fastapi import FastAPI, Depends, Body, Header, UploadFile, File, Path
import uvicorn
from sqlalchemy.future import select
from fastapi.exceptions import HTTPException
from sqlalchemy.sql import text
from settings import UPLOAD_PATH
import aiofiles


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
    new_tweet = Publication(author_id=api_key, content=tweet["tweet_data"])
    session.add(new_tweet)
    await session.commit()
    if tweet.get("tweet_medias_id", 0):
        for media_id in tweet["tweet_medias_id"]:
            attachment = await session.execute(select(Attachments).where(Attachments.id == media_id))
            attachment_model = attachment.one()[0]
            attachment_model.publication_id = new_tweet.id
            session.add(attachment_model)

    await session.commit()

    return {"result": True, "tweet_id": new_tweet.id}


@app.post("/api/medias", response_model=None)
async def add_media(
        api_key: str = Header(...),
        file: UploadFile = File(...),
        session=Depends(get_async_session),
):
    """ДЛя скачивания медиа файлов в папку upload_files"""

    if not file.filename:
        raise HTTPException(status_code=404, detail="File must have a name")

    os.makedirs(UPLOAD_PATH, exist_ok=True)
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
    file_name = now + file.filename
    save_path = os.path.join(UPLOAD_PATH, file_name)

    async with aiofiles.open(save_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    new_attachment = Attachments(link=file_name)
    session.add(new_attachment)
    await session.commit()

    return save_path, {"result": True, "media_id": new_attachment.id}


@app.delete("/api/tweets/{tweet_id}", response_model=None)
async def delete_tweet(
        api_key: str = Header(...),
        tweet_id: str = Path(...),
        session=Depends(get_async_session)
):
    """Для удаление твита автора, проверяет принадлежит ли твит автору"""
    author_id = api_key
    tweet_id = tweet_id
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
    """Для вывода ленты пользователя(выводит свои публикации и публикации подписок).ЕЩЕ НЕ СДЕЛАЛ МЕДИА ФАЙЛЫ"""
    author_id = api_key
    # Собираю ид всех подписок и самого автора
    subscriptions = await session.execute(select(Followers).where(
        Followers.follower_id == author_id)
    )
    authors_idx = [author_id]
    for subscription in subscriptions:
        authors_idx.append(subscription[0].author_id)

    # Собираю публикации всех подписок и самого автора
    tweets_by_authors = await session.execute(select(Publication).where(
        Publication.author_id.in_(authors_idx))
    )
    list_of_tweets = []
    for row in tweets_by_authors:
        tweet = row[0]
        data_tweet = {
            "id": tweet.id,
            "content": tweet.content,
            "attachments": [attachment.link for attachment in tweet.attachment],
            "authors": tweet.author.to_dict(),
            "likes": [{"user_id": like.author_id, "name": like.author.name} for like in tweet.like],
        }
        list_of_tweets.append(data_tweet)
    data_by_all_tweets = {"result": True, "tweets": list_of_tweets}
    return data_by_all_tweets


@app.get("/api/users/{user_id}")
async def get_user_profile_info(
        api_key: str = Header(...),
        user_id: str = Path(...),
        session=Depends(get_async_session)
):
    """Для вывода общей информации о профиле юзера пользователя,
    чтобы вывести информацию о себе необходимо вместо user_id написать me"""
    if user_id == "me":
        user_id = api_key
    else:
        user_id = user_id

    author = await session.execute(select(User).where(User.id == user_id))
    author_model = author.first()
    if not author_model:
        raise HTTPException(status_code=404, detail="User is not found")

    author_data = author_model[0].to_dict()
    author_data["follower"] = []
    for follower in author_model[0].follower:
        follower = {"id": follower.author_id}
        name = await session.execute(select(User).where(User.id == follower["id"]))
        follower["name"] = name.first()[0].name
        author_data["follower"].append(follower)

    author_data["following"] = []
    for following in author_model[0].following:
        following = {"id": following.author_id}
        name = await session.execute(select(User).where(User.id == following["id"]))
        following["name"] = name.first()[0].name
        author_data["following"].append(following)
    profile_data = {"result": True, "user": author_data}
    return profile_data


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
