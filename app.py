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
from flask_restx import Api, Resource, fields, Namespace
from werkzeug.utils import secure_filename

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

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

# Create database tables with retry mechanism
def create_tables_with_retry():
    """Create database tables with retry mechanism"""
    import time
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully!")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database connection attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f" Failed to create database tables after {max_retries} attempts: {e}")
                raise

# Initialize database
create_tables_with_retry()

# Flask application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# CORS middleware
CORS(app)

# Initialize Flask-RESTX API
api = Api(
    app,
    version='1.0',
    title='Tag Management API',
    description='A simple Flask API for managing tags with image upload functionality',
    doc='/swagger/',  # Swagger UI will be available at /swagger/
    prefix='/api'
)

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

# Swagger Models
add_tag_model = api.model('AddTagRequest', {
    'tag_mac_address': fields.String(required=True, description='MAC address of the tag', example='AA:BB:CC:DD:EE:FF')
})

add_tag_response_model = api.model('AddTagResponse', {
    'tag_mac_address': fields.String(description='MAC address of the tag', example='AA:BB:CC:DD:EE:FF'),
    'tag_uuid': fields.String(description='Generated UUID for the tag', example='550e8400-e29b-41d4-a716-446655440000')
})

update_tag_response_model = api.model('UpdateTagResponse', {
    'status': fields.String(description='Status of the operation', example='success'),
    'message': fields.String(description='Error message if failed', example='Inappropriate image size')
})

error_model = api.model('ErrorResponse', {
    'error': fields.String(description='Error message', example='Tag not found')
})

health_response_model = api.model('HealthResponse', {
    'status': fields.String(description='Health status', example='healthy'),
    'timestamp': fields.String(description='Current timestamp', example='2024-01-01T12:00:00')
})

# Create namespaces
tags_ns = api.namespace('tags', description='Tag management operations')
health_ns = api.namespace('health', description='Health check operations')

# API Endpoints

@tags_ns.route('/add_tag')
class AddTag(Resource):
    @api.expect(add_tag_model, validate=True)
    @api.marshal_with(add_tag_response_model, code=201)
    @api.marshal_with(error_model, code=400)
    @api.marshal_with(error_model, code=500)
    def post(self):
        """
        Add a new tag to the system.
        
        Takes a MAC address and generates a UUID for the tag.
        """
        try:
            # Get data from Flask-RESTX parsed request
            data = api.payload
            if not data or 'tag_mac_address' not in data:
                return {'error': 'tag_mac_address is required'}, 400
            
            tag_mac_address = data['tag_mac_address']
            
            db = get_db()
            
            # Check if MAC address already exists
            existing_tag = get_tag_by_mac(db, tag_mac_address)
            if existing_tag:
                db.close()
                return {'error': f'Tag with MAC address {tag_mac_address} already exists'}, 400
            
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
            
            return {
                'tag_mac_address': tag.mac_address,
                'tag_uuid': tag.uuid
            }, 201
            
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

# File upload parser for Swagger UI
upload_parser = api.parser()
upload_parser.add_argument('image', location='files', type='file', required=True, help='JPG image file (max 50MB)')

@tags_ns.route('/update_tag/<string:tag_uuid>')
class UpdateTag(Resource):
    @api.expect(upload_parser)
    @api.marshal_with(update_tag_response_model, code=200)
    @api.marshal_with(update_tag_response_model, code=300)
    @api.marshal_with(error_model, code=404)
    @api.marshal_with(error_model, code=500)
    def post(self, tag_uuid):
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
                return {'error': 'Tag not found'}, 404
            
            # Try Flask-RESTX parser first, fallback to regular Flask
            try:
                args = upload_parser.parse_args()
                image_file = args['image']
            except Exception as e:
                # Fallback to regular Flask file handling
                if 'image' not in request.files:
                    db.close()
                    return {
                        'status': 'fail',
                        'message': 'Inappropriate image size'
                    }, 300
                image_file = request.files['image']
            
            # Check if file is selected
            if not image_file or image_file.filename == '':
                db.close()
                return {
                    'status': 'fail',
                    'message': 'Inappropriate image size'
                }, 300
            
            # Validate file type
            if not image_file.content_type or not image_file.content_type.startswith('image/jpeg'):
                db.close()
                return {
                    'status': 'fail',
                    'message': 'Inappropriate image size'
                }, 300
            
            # Read image data
            image_data = image_file.read()
            image_size = len(image_data)
            
            # Validate image size (max 50MB)
            MAX_SIZE = 50 * 1024 * 1024  # 50MB
            if image_size > MAX_SIZE:
                db.close()
                return {
                    'status': 'fail',
                    'message': 'Inappropriate image size'
                }, 300
            
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
                
                return {
                    'status': 'success'
                }, 200
                
            except Exception as e:
                db.close()
                return {
                    'status': 'fail',
                    'message': 'Inappropriate image size'
                }, 300
                
        except Exception as e:
            # Log the error for debugging
            print(f"Error in update_tag: {str(e)}")
            return {'error': f'Internal server error: {str(e)}'}, 500

@health_ns.route('/health')
class HealthCheck(Resource):
    @api.marshal_with(health_response_model, code=200)
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }, 200

# Backward compatibility routes (without /api prefix)
@app.route('/add_tag', methods=['POST'])
def add_tag_legacy():
    """Legacy route for backward compatibility"""
    return AddTag().post()

@app.route('/update_tag/<tag_uuid>', methods=['POST'])
def update_tag_legacy(tag_uuid):
    """Legacy route for backward compatibility"""
    return UpdateTag().post(tag_uuid)

@app.route('/health', methods=['GET'])
def health_check_legacy():
    """Legacy route for backward compatibility"""
    return HealthCheck().get()

if __name__ == "__main__":
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8000)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true'
    )
