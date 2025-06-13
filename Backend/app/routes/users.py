from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, utils
from app.db import get_db
import shutil
import os
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

# Get current user profile
@router.get("/me", response_model=schemas.UserProfile)
def get_current_user_profile(
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    return current_user

# Update current user profile
@router.put("/me", response_model=schemas.UserProfile)
async def update_current_user_profile(
    bio: str = None,
    latitude: float = None,
    longitude: float = None,
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    update_data = {}
    if bio is not None:
        update_data["bio"] = bio
    if latitude is not None:
        update_data["latitude"] = latitude
    if longitude is not None:
        update_data["longitude"] = longitude
    
    if profile_picture:
        # Save profile picture
        photo_path = f"uploads/profiles/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{profile_picture.filename}"
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        
        with open(photo_path, "wb") as buffer:
            shutil.copyfileobj(profile_picture.file, buffer)
        
        update_data["profile_picture_url"] = photo_path
    
    return crud.update_user(db, current_user.id, update_data)

# Get user profile by ID
@router.get("/{user_id}", response_model=schemas.UserProfile)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Follow/Unfollow user
@router.post("/{user_id}/follow", response_model=schemas.FollowRead)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(utils.get_current_user)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    return crud.toggle_follow(db, current_user.id, user_id)

# Get user's followers
@router.get("/{user_id}/followers", response_model=List[schemas.UserRead])
def get_user_followers(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return crud.get_user_followers(db, user_id, skip=skip, limit=limit)

# Get user's following
@router.get("/{user_id}/following", response_model=List[schemas.UserRead])
def get_user_following(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return crud.get_user_following(db, user_id, skip=skip, limit=limit)

# Get user's posts
@router.get("/{user_id}/posts", response_model=List[schemas.PostRead])
def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return crud.get_user_posts(db, user_id, skip=skip, limit=limit)

# Get user's stats
@router.get("/{user_id}/stats", response_model=schemas.UserStats)
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.stats 