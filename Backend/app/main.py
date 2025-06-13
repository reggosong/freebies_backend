from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth
from app.db import engine
from app.models import user, post, follow

# Create database tables
user.Base.metadata.create_all(bind=engine)
post.Base.metadata.create_all(bind=engine)
follow.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Freebies API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Freebies API"} 