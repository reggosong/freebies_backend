from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    bio = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)

    posts = relationship("Post", back_populates="owner")
    followers = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following"
    )
    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower"
    )
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")
    got_it = relationship("GotIt", back_populates="user")

    @property
    def stats(self):
        return {
            "posts": len(self.posts),
            "got_it": len(self.got_it),
            "gave": sum(1 for post in self.posts if len(post.got_it) > 0)
        } 