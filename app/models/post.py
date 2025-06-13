from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db import Base

class PostCategory(enum.Enum):
    LEFTOVERS = "leftovers"
    NEW = "new"
    RESTAURANT = "restaurant"
    HOME_MADE = "home_made"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    photo_url = Column(String)
    category = Column(Enum(PostCategory))
    latitude = Column(Float)
    longitude = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    got_it = relationship("GotIt", back_populates="post", cascade="all, delete-orphan") 