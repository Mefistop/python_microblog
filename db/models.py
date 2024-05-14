from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY, Boolean
from sqlalchemy.orm import relationship
from db.database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    tweet = relationship('Publication', back_populates='author', cascade='all, delete', lazy='selectin', )
    follower = relationship(
        'Followers',
        foreign_keys="Followers.author_id",
        back_populates='author',
        cascade='all, delete',
        lazy='selectin',
    )
    following = relationship(
        'Followers',
        foreign_keys="Followers.follower_id",
        back_populates='follower_author',
        cascade='all, delete',
        lazy='selectin',
    )
    like = relationship("Like", back_populates="author", cascade="all, delete", lazy="selectin")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Publication(Base):
    __tablename__ = "publication"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))

    author = relationship("User", back_populates="tweet", lazy="selectin")
    like = relationship("Like", back_populates="tweet", lazy="selectin", cascade="all, delete", )
    attachment = relationship("Attachments", back_populates="tweet", lazy="selectin", cascade="all, delete", )

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "author_id": self.author_id,
        }


class Followers(Base):
    __tablename__ = "followers"
    author_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    follower_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)

    author = relationship(
        "User",
        foreign_keys="Followers.author_id",
        back_populates="follower",
        lazy="selectin",
    )
    follower_author = relationship(
        "User",
        foreign_keys="Followers.follower_id",
        back_populates="",
        lazy="selectin",
    )

    def to_dict(self):
        return {
            "author_id": self.author_id,
            "follower_id": self.follower_id,
        }


class Like(Base):
    __tablename__ = "like"
    publication_id = Column(Integer, ForeignKey("publication.id", ondelete="CASCADE"), primary_key=True)
    author_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    is_liked = Column(Boolean, default=False)

    tweet = relationship("Publication", back_populates="like", lazy="selectin")
    author = relationship("User", back_populates="like", lazy="selectin")

    def to_dict(self):
        return {
            "publication_id": self.publication_id,
            "author_id": self.author_id,
            "is_liked": self.is_liked,
        }


class Attachments(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    publication_id = Column(Integer, ForeignKey("publication.id", ondelete="CASCADE"), nullable=True)
    link = Column(String)

    tweet = relationship("Publication", back_populates="attachment", lazy="selectin")

