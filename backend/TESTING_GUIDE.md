# Backend Testing Guide

This guide explains how to test the backend implementation at different levels.

---

## Prerequisites

### 1. Install Dependencies

```bash
cd /home/noahdarwich/code/coderAI/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (for testing)
pip install -r requirements-dev.txt
```

### 2. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Required environment variables:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/data_extraction

# OpenAI API (for LLM extraction)
OPENAI_API_KEY=sk-your-api-key-here

# CORS (for frontend)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional
DEBUG=True
LOG_LEVEL=INFO
```

### 3. Set Up PostgreSQL Database

**Option A: Local PostgreSQL**
```bash
# Install PostgreSQL (if not already installed)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS (with Homebrew):
brew install postgresql

# Start PostgreSQL
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE data_extraction;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE data_extraction TO your_user;
\q
```

**Option B: Docker PostgreSQL**
```bash
# Run PostgreSQL in Docker
docker run --name postgres-dev \
  -e POSTGRES_USER=your_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=data_extraction \
  -p 5432:5432 \
  -d postgres:15

# Update .env with:
# DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost:5432/data_extraction
```

### 4. Run Database Migrations

```bash
cd /home/noahdarwich/code/coderAI/backend

# Initialize Alembic (if not already done)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Verify tables were created
psql -U your_user -d data_extraction -c "\dt"
```

---

## Testing Methods

## Method 1: Unit Tests (Automated)

### Run All Tests

```bash
cd /home/noahdarwich/code/coderAI/backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Test Files

```bash
# Test projects API
pytest tests/api/test_projects.py -v

# Test variables API
pytest tests/api/test_variables.py -v

# Test prompt generation
pytest tests/services/test_prompt_generator.py -v
```

### Run Single Test Function

```bash
# Run specific test
pytest tests/api/test_projects.py::test_create_project -v

# Run tests matching pattern
pytest -k "test_create" -v
```

### Expected Output

```
============================= test session starts ==============================
platform linux -- Python 3.11.0, pytest-7.4.0, pluggy-1.3.0
rootdir: /home/noahdarwich/code/coderAI/backend
plugins: asyncio-0.21.0, cov-4.1.0
collected 24 items

tests/api/test_projects.py::test_create_project PASSED                   [  4%]
tests/api/test_projects.py::test_list_projects PASSED                    [  8%]
tests/api/test_projects.py::test_get_project PASSED                      [ 12%]
...

============================== 24 passed in 2.45s ==============================
```

---

## Method 2: Interactive API Testing (Manual)

### Start the Development Server

```bash
cd /home/noahdarwich/code/coderAI/backend

# Start server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### Access API Documentation

Open your browser and navigate to:

1. **Swagger UI** (Interactive API docs): http://localhost:8000/docs
2. **ReDoc** (Alternative docs): http://localhost:8000/redoc
3. **OpenAPI JSON**: http://localhost:8000/openapi.json

### Test Endpoints via Swagger UI

1. Go to http://localhost:8000/docs
2. Click on any endpoint (e.g., "POST /api/v1/projects")
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. View the response

**Example: Create a Project**

1. Navigate to `POST /api/v1/projects`
2. Click "Try it out"
3. Enter request body:
```json
{
  "name": "Test Project",
  "scale": "SMALL",
  "language": "en",
  "domain": "political science"
}
```
4. Click "Execute"
5. You should see a 201 response with the created project

---

## Method 3: cURL Testing (Command Line)

### Test Health Endpoint

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "name": "Data Extraction Workflow API",
  "version": "1.0.0",
  "status": "healthy"
}
```

### Create a Project

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Research Project",
    "scale": "SMALL",
    "language": "en",
    "domain": "political science"
  }'
```

Expected response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Research Project",
  "scale": "SMALL",
  "language": "en",
  "domain": "political science",
  "status": "CREATED",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### List Projects

```bash
curl http://localhost:8000/api/v1/projects
```

### Get Project Details

```bash
# Replace {project_id} with actual UUID from create response
curl http://localhost:8000/api/v1/projects/{project_id}
```

### Create a Variable

```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/variables \
  -H "Content-Type: application/json" \
  -d '{
    "name": "event_type",
    "type": "CATEGORY",
    "instructions": "Extract the type of political event from the document",
    "classification_rules": {
      "categories": ["protest", "riot", "demonstration"],
      "allow_multiple": false
    },
    "order": 1
  }'
```

### Upload a Document

```bash
# Create a test text file
echo "This is a test document about a protest event." > test_document.txt

# Upload document
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/documents \
  -F "files=@test_document.txt"
```

---

## Method 4: Python Script Testing

Create a test script to interact with the API:

```python
# test_api.py
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_workflow():
    """Test complete workflow: create project, add variables, upload docs, process."""

    async with httpx.AsyncClient() as client:
        # 1. Create project
        print("1. Creating project...")
        response = await client.post(
            f"{BASE_URL}/api/v1/projects",
            json={
                "name": "API Test Project",
                "scale": "SMALL",
                "language": "en",
                "domain": "test"
            }
        )
        response.raise_for_status()
        project = response.json()
        project_id = project["id"]
        print(f"✓ Project created: {project_id}")

        # 2. Add variable
        print("\n2. Creating variable...")
        response = await client.post(
            f"{BASE_URL}/api/v1/projects/{project_id}/variables",
            json={
                "name": "test_var",
                "type": "TEXT",
                "instructions": "Extract test information",
                "order": 1
            }
        )
        response.raise_for_status()
        variable = response.json()
        print(f"✓ Variable created: {variable['name']}")
        print(f"  Current prompt preview: {variable['current_prompt']['prompt_text'][:100]}...")

        # 3. List variables
        print("\n3. Listing variables...")
        response = await client.get(
            f"{BASE_URL}/api/v1/projects/{project_id}/variables"
        )
        response.raise_for_status()
        variables = response.json()
        print(f"✓ Found {len(variables)} variable(s)")

        # 4. Get project details
        print("\n4. Getting project details...")
        response = await client.get(
            f"{BASE_URL}/api/v1/projects/{project_id}"
        )
        response.raise_for_status()
        project_detail = response.json()
        print(f"✓ Project: {project_detail['name']}")
        print(f"  Variables: {project_detail['variable_count']}")
        print(f"  Documents: {project_detail['document_count']}")
        print(f"  Status: {project_detail['status']}")

        print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_workflow())
```

Run the test:
```bash
python test_api.py
```

---

## Method 5: Postman/Insomnia Testing

### Import OpenAPI Spec

1. **Get OpenAPI spec**: http://localhost:8000/openapi.json
2. **Import to Postman**:
   - Open Postman
   - Click "Import"
   - Paste URL: `http://localhost:8000/openapi.json`
   - Click "Import"
3. **Import to Insomnia**:
   - Open Insomnia
   - Click "Create" → "Import From" → "URL"
   - Paste URL: `http://localhost:8000/openapi.json`

### Example Request Collection

Save this as `postman_collection.json`:

```json
{
  "info": {
    "name": "Data Extraction API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Create Project",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "url": "http://localhost:8000/api/v1/projects",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"Test Project\",\n  \"scale\": \"SMALL\",\n  \"language\": \"en\"\n}"
        }
      }
    },
    {
      "name": "List Projects",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/api/v1/projects"
      }
    }
  ]
}
```

---

## Method 6: Integration Testing (End-to-End)

### Full Workflow Test

```bash
#!/bin/bash
# test_workflow.sh - Complete workflow test

BASE_URL="http://localhost:8000"

echo "=== Data Extraction API Workflow Test ==="

# 1. Create project
echo -e "\n1. Creating project..."
PROJECT_RESPONSE=$(curl -s -X POST $BASE_URL/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Workflow Test","scale":"SMALL","language":"en"}')

PROJECT_ID=$(echo $PROJECT_RESPONSE | jq -r '.id')
echo "✓ Project ID: $PROJECT_ID"

# 2. Create variable
echo -e "\n2. Creating variable..."
curl -s -X POST $BASE_URL/api/v1/projects/$PROJECT_ID/variables \
  -H "Content-Type: application/json" \
  -d '{
    "name":"event_date",
    "type":"DATE",
    "instructions":"Extract the date of the event",
    "order":1
  }' | jq '.name'

# 3. Upload document
echo -e "\n3. Uploading document..."
echo "The protest occurred on January 15, 2024." > test_doc.txt
DOC_RESPONSE=$(curl -s -X POST $BASE_URL/api/v1/projects/$PROJECT_ID/documents \
  -F "files=@test_doc.txt")
DOCUMENT_ID=$(echo $DOC_RESPONSE | jq -r '.[0].id')
echo "✓ Document ID: $DOCUMENT_ID"

# 4. Create processing job
echo -e "\n4. Creating processing job..."
JOB_RESPONSE=$(curl -s -X POST $BASE_URL/api/v1/projects/$PROJECT_ID/jobs \
  -H "Content-Type: application/json" \
  -d "{\"job_type\":\"SAMPLE\",\"document_ids\":[\"$DOCUMENT_ID\"]}")
JOB_ID=$(echo $JOB_RESPONSE | jq -r '.id')
echo "✓ Job ID: $JOB_ID"

# 5. Check job status
echo -e "\n5. Checking job status..."
sleep 2
curl -s $BASE_URL/api/v1/jobs/$JOB_ID | jq '{status, progress, documents_completed, documents_total}'

# 6. Get results (when complete)
echo -e "\n6. Getting results..."
sleep 3
curl -s $BASE_URL/api/v1/jobs/$JOB_ID/results | jq '.extractions[0] | {value, confidence, source_text}'

echo -e "\n✅ Workflow test complete!"
```

Run the workflow test:
```bash
chmod +x test_workflow.sh
./test_workflow.sh
```

---

## Method 7: Load Testing (Performance)

### Using Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Create a test project when user starts."""
        response = self.client.post("/api/v1/projects", json={
            "name": "Load Test Project",
            "scale": "SMALL",
            "language": "en"
        })
        self.project_id = response.json()["id"]

    @task(3)
    def list_projects(self):
        """List all projects."""
        self.client.get("/api/v1/projects")

    @task(2)
    def get_project(self):
        """Get project details."""
        self.client.get(f"/api/v1/projects/{self.project_id}")

    @task(1)
    def create_variable(self):
        """Create a variable."""
        self.client.post(
            f"/api/v1/projects/{self.project_id}/variables",
            json={
                "name": f"var_{int(time.time())}",
                "type": "TEXT",
                "instructions": "Test variable",
                "order": 1
            }
        )
```

Run load test:
```bash
pip install locust
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 to start test
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Solution:**
- Check PostgreSQL is running: `sudo service postgresql status`
- Verify DATABASE_URL in `.env`
- Test connection: `psql -U your_user -d data_extraction`

**2. Missing OpenAI API Key**
```
ValueError: OpenAI API key is required
```
**Solution:**
- Add OPENAI_API_KEY to `.env`
- Get key from: https://platform.openai.com/api-keys

**3. Module Import Errors**
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**4. Alembic Migration Errors**
```
Target database is not up to date
```
**Solution:**
```bash
alembic upgrade head
```

**5. Port Already in Use**
```
ERROR: [Errno 48] Address already in use
```
**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
# Or use a different port
uvicorn src.main:app --reload --port 8001
```

---

## Quick Start Test Script

Save this as `quick_test.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Quick Backend Test"
echo "===================="

# 1. Check Python
echo -n "Checking Python... "
python --version

# 2. Check PostgreSQL
echo -n "Checking PostgreSQL... "
psql --version

# 3. Check virtual environment
echo -n "Checking virtual environment... "
if [ -d "venv" ]; then
    echo "✓ Found"
else
    echo "✗ Not found - creating..."
    python -m venv venv
fi

# 4. Activate and install
source venv/bin/activate
echo "Installing dependencies..."
pip install -q -r requirements.txt

# 5. Check database
echo -n "Checking database connection... "
python -c "from sqlalchemy import create_engine; import os; create_engine(os.getenv('DATABASE_URL', 'postgresql://localhost/data_extraction')).connect()" && echo "✓ Connected"

# 6. Run migrations
echo "Running migrations..."
alembic upgrade head

# 7. Start server
echo "Starting server..."
uvicorn src.main:app --reload &
SERVER_PID=$!

# Wait for server to start
sleep 3

# 8. Test API
echo "Testing API..."
curl -s http://localhost:8000/ | jq '.'

# 9. Cleanup
echo "Stopping server..."
kill $SERVER_PID

echo "✅ All checks passed!"
```

Run it:
```bash
chmod +x quick_test.sh
./quick_test.sh
```

---

## Next Steps

1. **Start with Method 1** (Unit Tests) to verify core functionality
2. **Use Method 2** (Swagger UI) for interactive testing during development
3. **Use Method 6** (Workflow Test) to verify end-to-end flow
4. **Use Method 7** (Load Testing) before production deployment

For continuous integration, add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: alembic upgrade head
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost/postgres
      - run: pytest --cov=src --cov-report=xml
      - run: pytest --cov=src --cov-report=html
```

Happy testing! 🎉
