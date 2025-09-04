# Flask Tag Management System

A simple Flask-based web API for managing tags with image upload functionality.

## Features

- **Add Tag**: Create a new tag with a MAC address and generate a UUID
- **Update Tag**: Upload an image to an existing tag
- **Health Check**: Simple health check endpoint
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Upload**: Image upload with validation (JPG only, max 5MB)

## API Endpoints

### POST /add_tag
Add a new tag to the system.

**Request Body:**
```json
{
    "tag_mac_address": "AA:BB:CC:DD:EE:FF"
}
```

**Response:**
```json
{
    "tag_mac_address": "AA:BB:CC:DD:EE:FF",
    "tag_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

### POST /update_tag/{tag_uuid}
Update a tag with an image file.

**Request:** Multipart form data with `image` field containing a JPG file.

**Response:**
```json
{
    "status": "success"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00"
}
```

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   Copy `env.example` to `.env` and update the database URL:
   ```bash
   cp env.example .env
   ```

3. **Database Setup:**
   Make sure PostgreSQL is running and the database exists. You can recreate tables using:
   ```bash
   python recreate_tables.py
   ```

4. **Run the Application:**
   ```bash
   python app.py
   ```

The application will start on `http://localhost:8000`

## Testing

Run the test script to verify all endpoints:
```bash
python test_endpoints.py
```

## Database Schema

The `tags` table contains:
- `id`: Primary key
- `uuid`: Unique identifier for the tag
- `mac_address`: MAC address of the tag (unique)
- `image_path`: Path to the uploaded image
- `image_size`: Size of the uploaded image in bytes
- `created_at`: Timestamp when the tag was created
- `updated_at`: Timestamp when the tag was last updated

## File Storage

Images are stored in the `uploads/images/` directory with the naming pattern:
`{tag_uuid}_{timestamp}.jpg`

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

## CORS

CORS is enabled for all origins to allow cross-origin requests.
