import datetime
import os.path

import aiofiles
from fastapi import APIRouter, Depends, FastAPI, File, Header, Path, UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.database import get_async_session
from db.models import Attachments, Followers, Like, Publication, User
from settings import API_KEY, ERROR_RESPONSES, STATIC_PATH

from schemas import (  # isort:skip
    GetAllTweetsOut,
    MediasAddOut,
    OutputSchema,
    TweetAddIn,
    TweetAddOut,
    TweetInfo,
    UserAddIn,
    UserAddOut,
    UserProfileInfoOut,
)

app = FastAPI()
router = APIRouter(prefix="/api", responses=ERROR_RESPONSES)  # type: ignore


@router.post("/user", response_model=UserAddOut)
async def add_new_useer(
    user: UserAddIn,
    session: AsyncSession = Depends(get_async_session),
) -> UserAddOut:
    """Создание нового пользователя в приложение"""
    new_user = User(name=user.name)
    session.add(new_user)
    await session.commit()
    return UserAddOut(result=True, author_id=int(new_user.id))


@router.post("/tweets", response_model=TweetAddOut)
async def add_tweet(
    tweet: TweetAddIn,
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_async_session),
) -> TweetAddOut:
    """Добавление новой публикации, проверяет наличие media id"""
    author_id = API_KEY.get(api_key, 0)
    if not author_id:
        raise HTTPException(status_code=404, detail="User is not registered")
    new_tweet = Publication(
        author_id=author_id,
        content=tweet.tweet_data,
    )
    session.add(new_tweet)
    await session.commit()
    if tweet.tweet_media_ids:
        for media_id in tweet.tweet_media_ids:
            attachment = await session.execute(
                select(Attachments).where(Attachments.id == media_id)
            )
            attachment_model = attachment.one()[0]
            attachment_model.publication_id = new_tweet.id
            session.add(attachment_model)

    await session.commit()

    return TweetAddOut(result=True, tweet_id=int(new_tweet.id))


@router.post("/medias", response_model=MediasAddOut)
async def add_media(
    api_key: str = Header(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
) -> MediasAddOut:
    """Загрузка медиа файлов"""

    if not file.filename:
        raise HTTPException(status_code=404, detail="File must have a name")

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
    file_name = now + file.filename
    link_file = os.path.join("images", file_name)
    save_path = os.path.join(STATIC_PATH, link_file)

    async with aiofiles.open(save_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    new_attachment = Attachments(link=link_file)
    session.add(new_attachment)
    await session.commit()

    return MediasAddOut(result=True, media_id=int(new_attachment.id))


@router.delete("/tweets/{tweet_id}", response_model=OutputSchema)
async def delete_tweet(
    api_key: str = Header(...),
    tweet_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> OutputSchema:
    """Удаление публикации автора, проводится проверка
    принадлежности публикации автору"""
    author_id = API_KEY.get(api_key, 0)
    tweet_id = tweet_id
    tweet_by_author_id_tweet_id = await session.execute(
        select(Publication).where(
            Publication.author_id == author_id, Publication.id == tweet_id
        )
    )
    tweet_to_delete = tweet_by_author_id_tweet_id.scalar()
    if tweet_to_delete:
        await session.delete(tweet_to_delete)
        await session.commit()
        return OutputSchema(result=True)
    else:
        raise HTTPException(status_code=404, detail="Tweet not found")


@router.post("/tweets/{tweet_id}/likes", response_model=OutputSchema)
async def add_like_to_tweet(
    api_key: str = Header(...),
    tweet_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> OutputSchema:
    """Добавление записи 'нравиться' публикации, проверка существует ли
    на самом деле публикация, отсутствует ли запись "нравиться" поставленная
    нами раннее"""
    author_id = API_KEY.get(api_key, 0)
    if not author_id:
        raise HTTPException(status_code=404, detail="User is not registered")

    tweet_id = tweet_id
    tweet = await session.get(Publication, tweet_id)
    if tweet:
        like_tweet = await session.execute(
            select(Like).where(
                Like.publication_id == tweet_id, Like.author_id == author_id
            )
        )
        if not like_tweet.scalar():
            new_like_tweet = Like(
                author_id=author_id,
                publication_id=tweet_id,
                is_liked=True,
            )
            session.add(new_like_tweet)
            await session.commit()
            return OutputSchema(result=True)

        raise HTTPException(status_code=404, detail="Tweet already like")

    raise HTTPException(status_code=404, detail="Tweet not found")


@router.delete("/tweets/{tweet_id}/likes", response_model=OutputSchema)
async def delete_like_to_tweet(
    api_key: str = Header(...),
    tweet_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> OutputSchema:
    """Удаление записи 'нравиться' публикации, проверка существует ли
    на самом деле публикация существует ли запись 'нравиться'"""
    author_id = API_KEY.get(api_key, 0)
    tweet_id = tweet_id
    like_model = await session.execute(
        select(Like).where(
            Like.publication_id == tweet_id,
            Like.author_id == author_id,
        )
    )
    like_tweet = like_model.scalar()
    if like_tweet:
        await session.delete(like_tweet)
        await session.commit()
        return OutputSchema(result=True)
    raise HTTPException(status_code=404, detail="Tweet by like not found")


@router.post("/users/{user_id}/follow", response_model=OutputSchema)
async def follow_on_user(
    api_key: str = Header(...),
    user_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> OutputSchema:
    """Подписка на других авторов, проверка существует ли автор,
    не подписаны ли мы уже на него, не пытаемся ли мы подписаться
    на самого себя"""
    author_id = API_KEY.get(api_key, 0)
    if not author_id:
        raise HTTPException(status_code=404, detail="User is not registered")
    follow_author = user_id
    if author_id == follow_author:
        raise HTTPException(
            status_code=404,
            detail="You can't subscribe to yourself",
        )
    subscibe_modul = await session.execute(
        select(Followers).where(
            Followers.author_id == follow_author,
            Followers.follower_id == author_id,
        ),
    )
    subscibe = subscibe_modul.scalar()
    if not subscibe:
        author = await session.get(User, follow_author)
        if author:
            new_subscribe = Followers(
                author_id=follow_author,
                follower_id=author_id,
            )
            session.add(new_subscribe)
            await session.commit()
            return OutputSchema(result=True)

        raise HTTPException(status_code=404, detail="Author not exist")

    raise HTTPException(status_code=404, detail="Subscribe already exist")


@router.delete("/users/{user_id}/follow", response_model=OutputSchema)
async def delete_follow(
    api_key: str = Header(...),
    user_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> OutputSchema:
    """Удаление подписки на других авторов, проверка существует ли
    подписка на автора"""
    author_id = API_KEY.get(api_key, 0)
    follow_author = user_id
    subscibe_moodel = await session.execute(
        select(Followers).where(
            Followers.author_id == follow_author,
            Followers.follower_id == author_id,
        ),
    )
    subscibe = subscibe_moodel.scalar()
    if subscibe:
        await session.delete(subscibe)
        await session.commit()
        return OutputSchema(result=True)
    raise HTTPException(status_code=404, detail="Subscribe not exist")


@router.get("/tweets", response_model=GetAllTweetsOut)
async def get_all_tweets(
    api_key: str = Header(...),
    session: AsyncSession = Depends(get_async_session),
) -> GetAllTweetsOut:
    """Вывода ленты пользователя(выводит свои публикации и
    публикации подписок)"""
    author_id = API_KEY.get(api_key, 0)
    if not author_id:
        raise HTTPException(status_code=404, detail="User is not registered")

    subscriptions = await session.execute(
        select(Followers).where(Followers.follower_id == author_id)
    )
    authors_idx = [author_id]
    for subscription in subscriptions:
        authors_idx.append(subscription[0].author_id)

    tweets_by_authors = await session.execute(
        select(Publication).where(Publication.author_id.in_(authors_idx))
    )
    list_of_tweets = []
    for row in tweets_by_authors:
        tweet = row[0]

        data_tweet = {
            "id": tweet.id,
            "content": tweet.content,
            "attachments": [attachm.link for attachm in tweet.attachment],
            "author": tweet.author.to_dict(),
            "likes": [
                {"user_id": like.author_id, "name": like.author.name}
                for like in tweet.like
            ],
        }
        list_of_tweets.append(data_tweet)
    tweets_data = [TweetInfo(**tweet) for tweet in list_of_tweets]
    return GetAllTweetsOut(result=True, tweets=tweets_data)


@router.get("/users/{user_id}", response_model=UserProfileInfoOut)
async def get_user_profile_info(
    api_key: str = Header(...),
    user_id: str = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> UserProfileInfoOut:
    """Вывод общей информации о профиле юзера пользователя,
    либо о себе (вместо user_id прописать 'me')"""

    if user_id == "me":
        actual_user_id = API_KEY.get(api_key, 0)
        if not actual_user_id:
            raise HTTPException(status_code=404, detail="User is not registered")
    else:
        actual_user_id = int(user_id)

    author = await session.execute(
        select(User).where(User.id == actual_user_id),
    )
    author_model = author.scalar_one_or_none()
    if not author_model:
        raise HTTPException(status_code=404, detail="User is not found")

    author_data = author_model.to_dict()
    author_data["follower"] = []

    for follower in author_model.follower:
        follower = {"id": follower.follower_id}
        name_row = await session.execute(
            select(User).where(User.id == follower["id"]),
        )
        user_model = name_row.scalar_one_or_none()
        if user_model:
            follower["name"] = user_model.name
        author_data["follower"].append(follower)
    author_data["following"] = []

    for following in author_model.following:
        following = {"id": following.author_id}
        name_row = await session.execute(
            select(User).where(User.id == following["id"]),
        )
        user_model = name_row.scalar_one_or_none()
        if user_model:
            following["name"] = user_model.name
        author_data["following"].append(following)
    profile_data = {"result": True, "user": author_data}
    return UserProfileInfoOut(**profile_data)
