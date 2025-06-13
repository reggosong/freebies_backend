from sqlalchemy.orm import Session
from app import models, schemas, utils

# Users

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = utils.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not utils.verify_password(password, user.hashed_password):
        return False
    return user

# Posts

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Post).offset(skip).limit(limit).all()

# Follows

def follow_user(db: Session, follower_id: int, following_id: int):
    db_follow = models.Follow(follower_id=follower_id, following_id=following_id)
    db.add(db_follow)
    db.commit()
    return db_follow


def unfollow_user(db: Session, follower_id: int, following_id: int):
    db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.following_id == following_id
    ).delete()
    db.commit() 