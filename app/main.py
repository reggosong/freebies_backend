from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import all models to ensure they're registered with SQLAlchemy
from app.models.user import User
from app.models.post import Post
from app.models.follow import Follow
from app.models.interaction import Like, GotIt, Comment
from app.models.message import Message
from app.models.password_reset import PasswordReset

from app.routes import auth, posts, users, messages, password_reset

# Create necessary directories
os.makedirs("uploads/posts", exist_ok=True)
os.makedirs("uploads/profiles", exist_ok=True)

app = FastAPI(title="Freebies API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(password_reset.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Freebies API"} 