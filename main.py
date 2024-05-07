from contextlib import asynccontextmanager
from db.models import User, Publication, Following, Followers, Like
from db.database import Base, async_session, engine
from fastapi import FastAPI, Depends, Body, Header, UploadFile, File, Path
import uvicorn


async def get_async_session():
    async with async_session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_session.close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


@app.post('/api/user', response_model=None)
async def add_new_useer(user: dict = Body(...), session=Depends(get_async_session)):
    """для добавления юзера, потом переделаю"""
    new_user = User(**user)
    session.add(new_user)
    await session.commit()
    return "f", 200


@app.post("/api/tweets", response_model=None)
async def add_tweet(
        api_key: str = Header(...),
        tweet: dict = Body(...),
        session=Depends(get_async_session),
):
    """Для добавления публикации"""
    publication_data = dict()
    publication_data["author_id"] = api_key
    publication_data["content"] = tweet["tweet_data"]
    new_tweet = Publication(**publication_data)
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


@app.delete("api/tweets/{id}", response_model=None)
async def delete_tweet(
        api_key: str = Header(...),
        id: str = Path(...),
        session=Depends(get_async_session)
):
    author_id = api_key
    tweet_id = id
    pass


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
