from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud, utils
from app.db import get_db
from app.models.post import PostCategory
from app.models.interaction import Comment, Like, GotIt
import shutil
import os
from datetime import datetime
from pydantic import ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])

# Helper to build absolute URL for photo
def build_absolute_photo_url(request: Request, photo_url: str) -> str:
    if photo_url.startswith('http'):  # already absolute
        return photo_url
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/{photo_url}".replace('//', '/')

# Create post with photo upload
@router.post("/", response_model=schemas.PostRead)
async def create_post(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: PostCategory = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    logger.info(f"Creating post for user: {current_user.username}")
    # Save photo
    photo_path = f"uploads/posts/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.filename}"
    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
    with open(photo_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    post_data = schemas.PostCreate(
        title=title,
        description=description,
        category=category,
        latitude=latitude,
        longitude=longitude,
        address=address,
        photo_url=photo_path
    )
    post = crud.create_post(db, post_data, current_user.id)
    # Patch photo_url to be absolute
    post.photo_url = build_absolute_photo_url(request, post.photo_url)
    return post

# Get post by ID
@router.get("/{post_id}", response_model=schemas.PostRead)
def get_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.photo_url = build_absolute_photo_url(request, post.photo_url)
    return post

# Get feed with filters
@router.get("/", response_model=List[schemas.PostRead])
def get_feed(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    category: Optional[PostCategory] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[float] = None,  # in kilometers
    following_only: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    posts = crud.get_feed(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        category=category,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        following_only=following_only
    )
    for post in posts:
        post.photo_url = build_absolute_photo_url(request, post.photo_url)
    return posts

# Update post
@router.put("/{post_id}", response_model=schemas.PostRead)
def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    db_post = crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    return crud.update_post(db, post_id, post)

# Delete a post
@router.delete("/{post_id}", response_model=schemas.PostRead)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    crud.delete_post(db, post_id)
    return post

# Like/Unlike post
@router.post("/{post_id}/like", response_model=schemas.LikeRead)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    return crud.toggle_like(db, post_id, current_user.id)

# Comment on post
@router.post("/{post_id}/comment", response_model=schemas.CommentRead)
def comment_post(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    return crud.create_comment(db, post_id, current_user.id, comment)

# Mark post as "Got it"
@router.post("/{post_id}/got-it", response_model=schemas.GotItRead)
def got_it_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    return crud.toggle_got_it(db, post_id, current_user.id)

# Get users who liked a post
@router.get("/{post_id}/likes", response_model=List[schemas.UserRead])
def get_post_likes(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return [like.user for like in post.likes]

# Get users who got it for a post
@router.get("/{post_id}/got-it", response_model=List[schemas.UserRead])
def get_post_got_it(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return [got_it.user for got_it in post.got_it]

# Get comments for a post
@router.get("/{post_id}/comments", response_model=List[schemas.CommentRead])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.comments 