from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, object_session
from app.db import Base
from app.models.post import Post
from app.models.interaction import GotIt

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    display_name = Column(String, nullable=True)
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
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates=None)

    @property
    def stats(self):
        session = object_session(self)
        if not session:
            # If the object is not attached to a session, we can't query.
            # This might happen in tests or other contexts.
            return {"posts": 0, "got_it": 0, "gave": 0}

        posts_count = session.query(Post).filter(Post.owner_id == self.id).count()
        
        got_it_count = session.query(GotIt).filter(GotIt.user_id == self.id).count()
        
        # Efficiently count posts by this user that have at least one 'got_it'
        gave_count = session.query(Post.id).filter(
            Post.owner_id == self.id,
            Post.got_it.any()
        ).count()

        return {
            "posts": posts_count,
            "got_it": got_it_count,
            "gave": gave_count
        } 