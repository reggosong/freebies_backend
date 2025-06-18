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
    title = Column(String)
    description = Column(String)
    category = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String, nullable=True)
    photo_url = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    got_it = relationship("GotIt", back_populates="post", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="post", cascade="all, delete-orphan")

    @property
    def likes_count(self):
        return len(self.likes) if self.likes else 0

    @property
    def comments_count(self):
        return len(self.comments) if self.comments else 0

    @property
    def got_it_count(self):
        return len(self.got_it) if self.got_it else 0

    @property
    def city(self):
        if not self.address:
            return None
        # Try to extract city from the address string (Nominatim format: ...city, state, country)
        parts = self.address.split(',')
        if len(parts) >= 3:
            return parts[-4].strip() if len(parts) >= 4 else parts[-3].strip()
        return parts[-2].strip() if len(parts) >= 2 else self.address.strip() 