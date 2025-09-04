"""
Script to recreate database tables for Flask Tag Management System
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import the Tag model from app.py
from app import Base, Tag

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine
engine = create_engine(DATABASE_URL)

def recreate_tables():
    """Drop and recreate all tables"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables()
