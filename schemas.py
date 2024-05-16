from pydantic import BaseModel
from typing import Optional, List, Dict


class OutputSchema(BaseModel):
    result: bool


class UserAddIn(BaseModel):
    name: str


class UserAddOut(OutputSchema):
    author_id: int


class TweetAddIn(BaseModel):
    tweet_data: str
    tweet_medias_id: Optional[List[int]] = None


class TweetAddOut(OutputSchema):
    tweet_id: int


class MediasAddOut(OutputSchema):
    media_id: int


class AuthorsInfo(BaseModel):
    id: int
    name: str


class TweetInfo(BaseModel):
    id: int
    content: str
    attachments: Optional[List]
    authors: AuthorsInfo
    likes: Optional[List]


class GetAllTweetsOut(OutputSchema):
    tweets: Optional[List[TweetInfo]]


class AuthorsInfoDetail(AuthorsInfo):
    follower: Optional[List[AuthorsInfo]]
    following: Optional[List[AuthorsInfo]]


class UserProfileInfoOut(OutputSchema):
    user: AuthorsInfoDetail
