from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, UniqueConstraint, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base
import enum

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_like'),)

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

class GotIt(Base):
    __tablename__ = "got_it"
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_got_it'),)

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="got_it")
    user = relationship("User", back_populates="got_it")

# Notification type enum
class NotificationType(enum.Enum):
    LIKE = "like"
    GOT_IT = "got_it"
    COMMENT = "comment"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # recipient
    post_id = Column(Integer, ForeignKey("posts.id"))
    actor_id = Column(Integer, ForeignKey("users.id"))  # who triggered
    type = Column(SqlEnum(NotificationType))
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="notifications")
    actor = relationship("User", foreign_keys=[actor_id]) 