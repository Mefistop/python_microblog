from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY, Boolean
from sqlalchemy.orm import relationship
from db.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    tweet = relationship('Publication', back_populates='author', cascade='all, delete', lazy='select', )
    follower = relationship(
        'Followers',
        foreign_keys="Followers.author_id",
        back_populates='author',
        cascade='all, delete',
        lazy='select',
    )
    following = relationship(
        'Followers',
        foreign_keys="Followers.follower_id",
        back_populates='follower_author',
        cascade='all, delete',
        lazy='select',
    )


class Publication(Base):
    __tablename__ = "publication"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))

    author = relationship("User", back_populates="tweet", lazy="select")
    like = relationship("Like", back_populates="tweet", lazy="select", cascade="all, delete", )


class Followers(Base):
    __tablename__ = "followers"
    author_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    follower_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)

    author = relationship(
        "User",
        foreign_keys="Followers.author_id",
        back_populates="follower",
        lazy="select",
    )
    follower_author = relationship(
        "User",
        foreign_keys="Followers.follower_id",
        back_populates="",
        lazy="select",
    )


# class Following(Base):
#     __tablename__ = "following"
#     author_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
#     following_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
#
#     author = relationship(
#         "User",
#         foreign_keys="Following.author_id",
#         back_populates="following",
#         lazy="select",
#         cascade="all, delete",
#     )


class Like(Base):
    __tablename__ = "like"
    publication_id = Column(Integer, ForeignKey("publication.id", ondelete="CASCADE"), primary_key=True)
    author_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    is_liked = Column(Boolean, default=False)

    tweet = relationship("Publication", back_populates="like", lazy="select")


class Attachments(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    publication_id = Column(Integer, ForeignKey("publication.id", ondelete="CASCADE"))
    link = Column(String)

