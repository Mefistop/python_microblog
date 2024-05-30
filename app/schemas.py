from typing import List, Optional

from pydantic import BaseModel


class OutputSchema(BaseModel):
    """
    Базовая схема для ответов приложения.
    """

    result: bool


class UserAddIn(BaseModel):
    """
    Схема для данных, отправляемых при создании нового пользователя.
    """

    name: str


class UserAddOut(OutputSchema):
    """
    Схема для ответа приложения при успешном создании нового пользователя.
    """

    author_id: int


class TweetAddIn(BaseModel):
    """
    Схема для данных, отправляемых при создании нового твита.
    """

    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None


class TweetAddOut(OutputSchema):
    """
    Схема для ответа приложения при успешном создании нового твита.
    """

    tweet_id: int


class MediasAddOut(OutputSchema):
    """
    Схема для ответа приложения при успешном добавлении нового медиафайла.
    """

    media_id: int


class AuthorsInfo(BaseModel):
    """
    Схема для информации о пользователе.
    """

    id: int
    name: str


class TweetInfo(BaseModel):
    """
    Схема для информации о твите.
    """

    id: int
    content: str
    attachments: Optional[List]
    author: AuthorsInfo
    likes: Optional[List]


class GetAllTweetsOut(OutputSchema):
    """
    Схема для ответа приложения при успешном получении списка всех твитов.
    """

    tweets: Optional[List[TweetInfo]]


class AuthorsInfoDetail(AuthorsInfo):
    """
    Схема для детальной информации о пользователе.
    """

    follower: Optional[List[AuthorsInfo]]
    following: Optional[List[AuthorsInfo]]


class UserProfileInfoOut(OutputSchema):
    """
    Схема для ответа приложения при успешном получении информации
    о пользователе.
    """

    user: AuthorsInfoDetail


class ErrorResponses(BaseModel):
    """
    Схема для ответа приложения при возникновении ошибки.
    """

    result: bool = False
    error_type: str
    error_message: str
