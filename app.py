"""
Flask Tag Management System - Simplified Version
Only two endpoints: /add_tag and /update_tag/<uuid>
"""

import os
import uuid
from datetime import datetime
from pathlib import Path

# Flask imports
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Environment configuration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Validate DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in your .env file. "
        "Format: postgresql://username:password@host:port/database_name"
    )

# Database configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False)
    mac_address = Column(String(17), unique=True, index=True, nullable=False)
    image_path = Column(String(500), nullable=True)
    image_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create database tables
Base.metadata.create_all(bind=engine)

# Flask application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# CORS middleware
CORS(app)

# Create uploads directory
UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Utility functions
def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())

def get_tag_by_uuid(db: Session, tag_uuid: str):
    """Retrieve a tag by UUID"""
    return db.query(Tag).filter(Tag.uuid == tag_uuid).first()

def get_tag_by_mac(db: Session, mac_address: str):
    """Retrieve a tag by MAC address"""
    return db.query(Tag).filter(Tag.mac_address == mac_address).first()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise

# API Endpoints

@app.route('/add_tag', methods=['POST'])
def add_tag():
    """
    Add a new tag to the system.
    
    Takes a MAC address and generates a UUID for the tag.
    """
    try:
        data = request.get_json()
        if not data or 'tag_mac_address' not in data:
            return jsonify({
                'error': 'tag_mac_address is required'
            }), 400
        
        tag_mac_address = data['tag_mac_address']
        
        db = get_db()
        
        # Check if MAC address already exists
        existing_tag = get_tag_by_mac(db, tag_mac_address)
        if existing_tag:
            db.close()
            return jsonify({
                'error': f'Tag with MAC address {tag_mac_address} already exists'
            }), 400
        
        # Generate new UUID
        new_uuid = generate_uuid()
        
        # Create new tag
        tag = Tag(
            uuid=new_uuid,
            mac_address=tag_mac_address
        )
        
        db.add(tag)
        db.commit()
        db.refresh(tag)
        
        db.close()
        
        return jsonify({
            'tag_mac_address': tag.mac_address,
            'tag_uuid': tag.uuid
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/update_tag/<tag_uuid>', methods=['POST'])
def update_tag(tag_uuid):
    """
    Update a tag with an image.
    
    Accepts a JPG image file and validates its size.
    """
    try:
        db = get_db()
        
        # Check if tag exists
        tag = get_tag_by_uuid(db, tag_uuid)
        if not tag:
            db.close()
            return jsonify({
                'error': 'Tag not found'
            }), 404
        
        # Check if file is present
        if 'image' not in request.files:
            db.close()
            return jsonify({
                'status': 'fail',
                'message': 'No image file provided'
            }), 400
        
        image_file = request.files['image']
        
        # Check if file is selected
        if image_file.filename == '':
            db.close()
            return jsonify({
                'status': 'fail',
                'message': 'No image file selected'
            }), 400
        
        # Validate file type
        if not image_file.content_type or not image_file.content_type.startswith('image/jpeg'):
            db.close()
            return jsonify({
                'status': 'fail',
                'message': 'Only JPG images are allowed'
            }), 400
        
        # Read image data
        image_data = image_file.read()
        image_size = len(image_data)
        
        # Validate image size (max 5MB)
        MAX_SIZE = 5 * 1024 * 1024  # 5MB
        if image_size > MAX_SIZE:
            db.close()
            return jsonify({
                'status': 'fail',
                'message': 'Inappropriate image size'
            }), 400
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{tag_uuid}_{timestamp}.jpg"
        file_path = UPLOAD_DIR / filename
        
        # Save image file
        try:
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            # Update tag in database
            tag.image_path = str(file_path)
            tag.image_size = image_size
            tag.updated_at = datetime.utcnow()
            
            db.commit()
            db.close()
            
            return jsonify({
                'status': 'success'
            }), 200
            
        except Exception as e:
            db.close()
            return jsonify({
                'status': 'fail',
                'message': f'Failed to save image: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

if __name__ == "__main__":
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8000)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true'
    )
