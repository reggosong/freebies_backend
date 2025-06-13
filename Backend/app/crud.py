from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from app import models, schemas, utils
from typing import List, Optional
from datetime import datetime
import math
from app.models.post import PostCategory
from app.models.message import MessageType

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, update_data: dict):
    db_user = get_user(db, user_id)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

# Post operations
def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_user_posts(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(models.Post).filter(models.Post.owner_id == user_id).offset(skip).limit(limit).all()

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_post(db: Session, post_id: int, post: schemas.PostUpdate):
    db_post = get_post(db, post_id)
    update_data = post.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    db.delete(db_post)
    db.commit()

def get_feed(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    category: Optional[PostCategory] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[float] = None,
    following_only: bool = False
):
    query = db.query(models.Post)
    
    if following_only:
        following_ids = [f.following_id for f in db.query(models.Follow).filter(models.Follow.follower_id == user_id).all()]
        query = query.filter(models.Post.owner_id.in_(following_ids))
    
    if category:
        query = query.filter(models.Post.category == category)
    
    if latitude and longitude and radius:
        # Haversine formula for distance calculation
        query = query.filter(
            func.acos(
                func.sin(func.radians(latitude)) * func.sin(func.radians(models.Post.latitude)) +
                func.cos(func.radians(latitude)) * func.cos(func.radians(models.Post.latitude)) *
                func.cos(func.radians(longitude - models.Post.longitude))
            ) * 6371 <= radius  # 6371 is Earth's radius in kilometers
        )
    
    return query.order_by(desc(models.Post.created_at)).offset(skip).limit(limit).all()

# Interaction operations
def toggle_like(db: Session, post_id: int, user_id: int):
    existing_like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == user_id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        db.commit()
        return None
    
    db_like = models.Like(post_id=post_id, user_id=user_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like

def create_comment(db: Session, post_id: int, user_id: int, comment: schemas.CommentCreate):
    db_comment = models.Comment(**comment.dict(), post_id=post_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def toggle_got_it(db: Session, post_id: int, user_id: int):
    existing_got_it = db.query(models.GotIt).filter(
        models.GotIt.post_id == post_id,
        models.GotIt.user_id == user_id
    ).first()
    
    if existing_got_it:
        db.delete(existing_got_it)
        db.commit()
        return None
    
    db_got_it = models.GotIt(post_id=post_id, user_id=user_id)
    db.add(db_got_it)
    db.commit()
    db.refresh(db_got_it)
    return db_got_it

# Follow operations
def toggle_follow(db: Session, follower_id: int, following_id: int):
    existing_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.following_id == following_id
    ).first()
    
    if existing_follow:
        db.delete(existing_follow)
        db.commit()
        return None
    
    db_follow = models.Follow(follower_id=follower_id, following_id=following_id)
    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    return db_follow

def get_user_followers(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(models.User).join(
        models.Follow, models.Follow.follower_id == models.User.id
    ).filter(
        models.Follow.following_id == user_id
    ).offset(skip).limit(limit).all()

def get_user_following(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(models.User).join(
        models.Follow, models.Follow.following_id == models.User.id
    ).filter(
        models.Follow.follower_id == user_id
    ).offset(skip).limit(limit).all()

# Message operations
def get_message(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.id == message_id).first()

def get_user_messages(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    message_type: Optional[MessageType] = None,
    unread_only: bool = False
):
    query = db.query(models.Message).filter(models.Message.receiver_id == user_id)
    
    if message_type:
        query = query.filter(models.Message.type == message_type)
    
    if unread_only:
        query = query.filter(models.Message.read == False)
    
    return query.order_by(desc(models.Message.created_at)).offset(skip).limit(limit).all()

def mark_message_read(db: Session, message_id: int):
    message = get_message(db, message_id)
    message.read = True
    db.commit()
    db.refresh(message)
    return message

def mark_all_messages_read(db: Session, user_id: int):
    messages = db.query(models.Message).filter(
        models.Message.receiver_id == user_id,
        models.Message.read == False
    ).all()
    
    for message in messages:
        message.read = True
    
    db.commit()
    return messages

def delete_message(db: Session, message_id: int):
    message = get_message(db, message_id)
    db.delete(message)
    db.commit()

def get_unread_message_count(db: Session, user_id: int):
    total = db.query(func.count(models.Message.id)).filter(
        models.Message.receiver_id == user_id,
        models.Message.read == False
    ).scalar()
    
    by_type = {}
    for message_type in MessageType:
        count = db.query(func.count(models.Message.id)).filter(
            models.Message.receiver_id == user_id,
            models.Message.read == False,
            models.Message.type == message_type
        ).scalar()
        by_type[message_type.value] = count
    
    return {"total": total, "by_type": by_type}

# Authentication
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not utils.verify_password(password, user.hashed_password):
        return False
    return user 