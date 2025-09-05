# Flask Tag Management System

A simple, self-contained Flask-based web API for managing tags with image upload functionality.

## 📋 What Has Been Accomplished

### ✅ Project Setup

- **Flask Web API** with PostgreSQL database integration
- **Docker containerization** with Docker Compose for easy deployment
- **Self-contained architecture** - everything works with a single command
- **Environment configuration** with `.env` file support
- **Database auto-creation** - tables are created automatically on startup

### ✅ Core Features Implemented

- **Tag Management**: Create tags with MAC addresses and auto-generated UUIDs
- **Image Upload**: Upload JPG images to existing tags with validation
- **Health Monitoring**: Health check endpoint for service monitoring
- **Data Validation**: MAC address uniqueness, file type validation, size limits
- **Error Handling**: Comprehensive error responses with proper HTTP status codes

### ✅ Database Design

- **PostgreSQL** with SQLAlchemy ORM
- **Tags table** with UUID, MAC address, image path, timestamps
- **Connection pooling** for optimal performance
- **Auto-retry mechanism** for database connection reliability

### ✅ Testing & Quality Assurance

- **Automated test suite** with comprehensive endpoint testing
- **Service readiness checks** to ensure reliable testing
- **Error case validation** for robust error handling
- **Manual testing guides** with Postman examples
- **Database verification** commands for data inspection

### ✅ Production Readiness

- **CORS configuration** for cross-origin requests
- **File upload security** with type and size validation
- **Database connection resilience** with retry mechanisms
- **Environment-based configuration** for different deployments
- **Resource cleanup** scripts and commands

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone and navigate to the project:**

   ```bash
   cd tag-management
   ```
2. **Start the application:**

   ```bash
   docker-compose up --build
   ```
3. **Wait for containers to be ready:**

   ```bash
   # Wait 30-60 seconds for containers to start up
   # You'll see "Database tables created successfully!" in the logs
   ```
4. **Verify containers are running:**

   ```bash
   # Check if both containers are running
   docker-compose ps

   # Should show both containers as "Up"
   # tag-management-flask-app-1   Up   0.0.0.0:8000->8000/tcp
   # tag-management-postgres-1    Up   0.0.0.0:5432->5432/tcp
   ```
5. **Test the application:**

   ```bash
   python test_endpoints.py
   ```

   **What this does:** The test script automatically tests all API endpoints:

   - ✅ Health check endpoint
   - ✅ Add tag functionality
   - ✅ Duplicate MAC address prevention
   - ✅ Image upload with validation
   - ✅ Error handling for invalid requests

   **Alternative - Manual Testing with Postman:**

   **Base URL:** `http://localhost:8000`

   **1. Health Check**

   - Method: `GET`
   - URL: `http://localhost:8000/health`
   - Expected Response: `{"status": "healthy", "timestamp": "..."}`

   **2. Add Tag**

   - Method: `POST`
   - URL: `http://localhost:8000/add_tag`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):

   ```json
   {
       "tag_mac_address": "AA:BB:CC:DD:EE:FF"
   }
   ```

   - Expected Response: `{"tag_mac_address": "AA:BB:CC:DD:EE:FF", "tag_uuid": "..."}`

   **3. Update Tag with Image**

   - Method: `POST`
   - URL: `http://localhost:8000/update_tag/{tag_uuid}`
   - Headers: `Content-Type: multipart/form-data`
   - Body (form-data): Key: `image`, Type: `File`, Value: Select a JPG image
   - Expected Response 200: `{"status": "success"}`
   - Expected Response 300: `{"status": "fail", "message": "Inappropriate image size"}`

That's it! The application will be running on `http://localhost:8000`

## ✨ Features

- **Add Tag**: Create a new tag with a MAC address and generate a UUID
- **Update Tag**: Upload an image to an existing tag
- **Health Check**: Simple health check endpoint
- **Database**: PostgreSQL with SQLAlchemy ORM (auto-created)
- **File Upload**: Image upload with validation (JPG only, max 50MB)
- **Self-contained**: Everything works out of the box with Docker

## 📡 API Endpoints

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

### POST /update_tag/

Update a tag with an image file.

**Request:** JPG image file as multipart form data

**Response 200 (Success):**

```json
{
    "status": "success"
}
```

**Response 300 (Failure):**

```json
{
    "status": "fail",
    "message": "Inappropriate image size"
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

## 🗄️ Database Schema

The `tags` table contains:

- `id`: Primary key
- `uuid`: Unique identifier for the tag
- `mac_address`: MAC address of the tag (unique)
- `image_path`: Path to the uploaded image
- `image_size`: Size of the uploaded image in bytes
- `created_at`: Timestamp when the tag was created
- `updated_at`: Timestamp when the tag was last updated

## 📁 File Storage

Images are stored in the `uploads/images/` directory with the naming pattern:
`{tag_uuid}_{timestamp}.jpg`

## 🔧 Configuration

The application uses environment variables from `.env` file:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key
- `DEBUG`: Debug mode (True/False)
- `HOST`: Host to bind to (default: 0.0.0.0)
- `PORT`: Port to bind to (default: 8000)

## 🧪 Testing

### Automated Testing

Run the comprehensive test suite:

```bash
python test_endpoints.py
```

The test script will:

- Wait for the service to be ready
- Test all API endpoints
- Validate error handling
- Clean up test data

### Manual Testing with curl Commands

#### 1. Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**

```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00"
}
```

#### 2. Add Tag

```bash
curl -X POST http://localhost:8000/add_tag \
  -H "Content-Type: application/json" \
  -d '{"tag_mac_address": "AA:BB:CC:DD:EE:FF"}'
```

**Expected Response:**

```json
{
    "tag_mac_address": "AA:BB:CC:DD:EE:FF",
    "tag_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 3. Add Another Tag (Different MAC)

```bash
curl -X POST http://localhost:8000/add_tag \
  -H "Content-Type: application/json" \
  -d '{"tag_mac_address": "11:22:33:44:55:66"}'
```

#### 4. Test Duplicate MAC Address (Error Case)

```bash
curl -X POST http://localhost:8000/add_tag \
  -H "Content-Type: application/json" \
  -d '{"tag_mac_address": "AA:BB:CC:DD:EE:FF"}'
```

**Expected Response:** `400 Bad Request`

#### 5. Update Tag with Image

First, get a tag UUID from step 2, then:

```bash
# Create a test JPG image (if you don't have one)
echo "test" > test_image.jpg

# Upload image to tag (replace {tag_uuid} with actual UUID)
curl -X POST http://localhost:8000/update_tag/{tag_uuid} \
  -F "image=@test_image.jpg"
```

**Expected Response 200 (Success):**

```json
{
    "status": "success"
}
```

#### 6. Test Image Upload Error Cases

**Missing Image File:**

```bash
curl -X POST http://localhost:8000/update_tag/{tag_uuid}
```

**Expected Response:** `300` with `{"status": "fail", "message": "Inappropriate image size"}`

**Empty Filename:**

```bash
curl -X POST http://localhost:8000/update_tag/{tag_uuid} \
  -F "image=@"
```

**Wrong File Type (PNG):**

```bash
# Create a PNG file
echo "test" > test_image.png

curl -X POST http://localhost:8000/update_tag/{tag_uuid} \
  -F "image=@test_image.png"
```

**Non-existent Tag:**

```bash
curl -X POST http://localhost:8000/update_tag/00000000-0000-0000-0000-000000000000 \
  -F "image=@test_image.jpg"
```

**Expected Response:** `404 Not Found`

#### 7. Test with Verbose Output

```bash
# See full HTTP response including headers
curl -v -X GET http://localhost:8000/health

# See response status code only
curl -w "%{http_code}\n" -o /dev/null -s http://localhost:8000/health

# Test with response time
curl -w "Time: %{time_total}s\nStatus: %{http_code}\n" -o /dev/null -s http://localhost:8000/health
```

### Manual Testing with Postman

#### 1. Health Check

- **Method:** `GET`
- **URL:** `http://localhost:8000/health`
- **Expected Response:**

```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00"
}
```

#### 2. Add Tag

- **Method:** `POST`
- **URL:** `http://localhost:8000/add_tag`
- **Headers:** `Content-Type: application/json`
- **Body (raw JSON):**

```json
{
    "tag_mac_address": "AA:BB:CC:DD:EE:FF"
}
```

- **Expected Response:**

```json
{
    "tag_mac_address": "AA:BB:CC:DD:EE:FF",
    "tag_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 3. Update Tag with Image

- **Method:** `POST`
- **URL:** `http://localhost:8000/update_tag/{tag_uuid}`
- **Headers:** `Content-Type: multipart/form-data`
- **Body (form-data):**
  - Key: `image`, Type: `File`, Value: Select a JPG image file
- **Expected Response 200 (Success):**

```json
{
    "status": "success"
}
```

- **Expected Response 300 (Failure):**

```json
{
    "status": "fail",
    "message": "Inappropriate image size"
}
```

#### 4. Test Error Cases

**Duplicate MAC Address:**

- **Method:** `POST`
- **URL:** `http://localhost:8000/add_tag`
- **Body:** Same as Add Tag
- **Expected Response:** `400 Bad Request`

**Non-existent Tag Update:**

- **Method:** `POST`
- **URL:** `http://localhost:8000/update_tag/00000000-0000-0000-0000-000000000000`
- **Body:** Image file
- **Expected Response:** `404 Not Found`

**Invalid Image (Wrong Type/Size/Missing):**

- **Method:** `POST`
- **URL:** `http://localhost:8000/update_tag/{valid_uuid}`
- **Body:** PNG, oversized file, or no file
- **Expected Response:** `300` with `{"status": "fail", "message": "Inappropriate image size"}`

## 🐳 Docker Services

- **Flask App**: Port 8000
- **PostgreSQL**: Port 5432
- **Database User**: `flask_api_user`
- **Database Name**: `tag_management`

## 🛠️ Development

### Local Development (without Docker , dont use this because you are now running everything in the docker)

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
2. **Set up environment:**

   ```bash
   cp env.example .env
   # Edit .env with your database settings
   ```
3. **Run the application:**

   ```bash
   python app.py
   ```

## 📊 Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success (image upload success)
- `201`: Created (tag creation success)
- `300`: Image upload failure (wrong type, size, or missing file)
- `400`: Bad Request (duplicate MAC address)
- `404`: Not Found (tag not found)
- `500`: Internal Server Error

## 🔧 Debugging & Troubleshooting

### Essential Commands

#### Start the Application

```bash
# Start with fresh build
docker-compose up --build

# Start in background
docker-compose up -d --build

# Start with logs
docker-compose up --build --force-recreate
```

#### Check Service Status

```bash
# Check running containers
docker-compose ps

# Expected output:
# NAME                         IMAGE                      COMMAND                           SERVICE
# tag-management-flask-app-1   tag-management-flask-app   "python app.py"                   flask-app
# tag-management-postgres-1    postgres:15                "docker-entrypoint.sh postgres"   postgres

# Check container logs
docker-compose logs flask-app
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f flask-app
```

#### Verify Application is Ready

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-01T12:00:00"}

# Check database connection
docker exec tag-management-postgres-1 psql -U flask_api_user -d tag_management -c "SELECT 1;"

# Expected response:
#  ?column? 
# ----------
#         1
```

#### Database Operations -> Remember that the database is running as a container so below code will be used to connect to the database ( -it means integrated terminal)

```bash
# Connect to database
docker exec -it tag-management-postgres-1 psql -U flask_api_user -d tag_management

# Check database tables
docker exec -it tag-management-postgres-1 psql -U flask_api_user -d tag_management -c "\dt"

# View all tags
docker exec -it tag-management-postgres-1 psql -U flask_api_user -d tag_management -c "SELECT * FROM tags;"

# Count tags
docker exec -it tag-management-postgres-1 psql -U flask_api_user -d tag_management -c "SELECT COUNT(*) FROM tags;"
```

#### Clean Up (Development Only)

```bash
# Stop containers (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# WARNING: Only use in development - removes all data
# docker-compose down -v
# docker system prune -f
```

### Common Issues & Solutions

#### 1. Database Connection Issues

**Problem:** `connection to server at "postgres" failed: Connection refused`

**Solution:**

```bash
# Wait for database to be ready
docker-compose logs postgres

# Restart services
docker-compose restart

# Check if database is running
docker-compose ps
```

#### 2. Port Already in Use

**Problem:** `Port 8000 is already in use`

**Solution:**

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

#### 3. Image Upload Fails

**Problem:** `Only JPG images are allowed`

**Solution:**

- Ensure file is actually a JPG
- Check file extension is `.jpg` or `.jpeg`
- Verify file is not corrupted
- File size must be under 50MB

#### 4. Test Failures

**Problem:** Tests fail with connection errors

**Solution:**

```bash
# Wait for service to be ready
Start-Sleep -Seconds 30

# Check if service is responding
curl http://localhost:8000/health

# Run tests with verbose output
python test_endpoints.py
```

#### 5. Containers Not Starting

**Problem:** Containers fail to start or keep restarting

**Solution:**

```bash
# Check container status
docker-compose ps

# Check logs for errors
docker-compose logs

# Check if ports are available
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Restart containers
docker-compose restart

# If still failing, check Docker resources
docker system df
```

### Development Workflow

#### 1. Fresh Start (Development Only)

```bash
# Stop containers
docker-compose stop

# Start fresh (keeps existing data)
docker-compose up --build

# WARNING: Only for development - removes all data
# docker-compose down -v
# docker-compose up --build
```

#### 2. Complete Docker Cleanup (Development Only)

**⚠️ WARNING: These commands will remove ALL Docker containers, images, volumes, and networks from your local machine. Use only in development!**

```bash
# Stop all running containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Remove all volumes
docker volume rm $(docker volume ls -q)

# Remove all networks (except default ones)
docker network rm $(docker network ls -q)

# Remove all unused data (containers, networks, images, build cache)
docker system prune -a --volumes

# Alternative: Nuclear option - removes EVERYTHING
docker system prune -a --volumes --force
```

**Step-by-step cleanup for this project only:**

```bash
# Stop and remove project containers
docker-compose down -v

# Remove project images
docker rmi tag-management-flask-app
docker rmi postgres:15

# Remove project volumes
docker volume rm tag-management_postgres_data

# Clean up any dangling resources
docker system prune -f
```

**Verify cleanup:**

```bash
# Check containers (should be empty)
docker ps -a

# Check images (should not show project images)
docker images

# Check volumes (should not show project volumes)
docker volume ls

# Check networks
docker network ls
```

#### 2. Code Changes

```bash
# After code changes, rebuild
docker-compose up --build

# Or restart just the Flask app
docker-compose restart flask-app
```

#### 3. Database Reset (Development Only)

```bash
# WARNING: This removes all data - use only in development
# docker-compose down -v
# docker-compose up -d

# Safer alternative - restart containers
docker-compose restart
```

### Monitoring & Logs

#### View Application Logs

```bash
# All logs
docker-compose logs

# Flask app only
docker-compose logs flask-app

# PostgreSQL only
docker-compose logs postgres

# Follow logs
docker-compose logs -f
```

#### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage (safe to run)
docker system df

# Volume usage (safe to run)
docker volume ls

# WARNING: Don't run these in production
# docker system prune -f
# docker volume prune -f
```

### Testing Commands

#### Run Tests

```bash
# Basic test
python test_endpoints.py

# Test with curl
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/add_tag -H "Content-Type: application/json" -d '{"tag_mac_address": "AA:BB:CC:DD:EE:FF"}'
```

#### Test Image Upload

```bash
# Create test image
echo "test" > test.jpg

# Upload image (replace UUID with actual tag UUID)
curl -X POST http://localhost:8000/update_tag/{uuid} -F "image=@test.jpg"
```

## 🔒 Security

- CORS is enabled for all origins
- File upload size limit: 50MB
- Only JPG images are allowed
- MAC address uniqueness enforced

## ⚠️ Production Safety

### Commands to AVOID in Production:

- `docker-compose down -v` - Removes all data volumes
- `docker system prune -f` - Removes all unused containers, networks, images
- `docker volume prune -f` - Removes all unused volumes
- `docker-compose down -v --remove-orphans` - Removes containers and volumes

### Safe Production Commands:

- `docker-compose up -d` - Start services
- `docker-compose stop` - Stop services (keeps data)
- `docker-compose restart` - Restart services (keeps data)
- `docker-compose logs -f` - View logs
- `docker-compose ps` - Check status

### Production Deployment:

1. Use environment-specific `.env` files
2. Set up proper backup strategies for database volumes
3. Use Docker secrets for sensitive data
4. Monitor container health and resource usage
5. Never run destructive commands without proper backups
