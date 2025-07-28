#!/usr/bin/env python3
"""
Database setup script for PostgreSQL
Run this script to create all database tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import engine, Base
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    print("Setting up PostgreSQL database...")
    try:
        # Import all models to ensure they're registered
        from app.models.user import User
        from app.models.post import Post
        from app.models.follow import Follow
        from app.models.interaction import Like, GotIt, Comment
        from app.models.message import Message
        from app.models.password_reset import PasswordReset
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    setup_database() 