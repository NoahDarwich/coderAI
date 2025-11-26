# Data Extraction Workflow - Backend API

FastAPI backend service for the research data extraction tool.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional for MVP)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup

```bash
# Create database
createdb data_extraction

# Run migrations
alembic upgrade head
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/api/test_projects.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/          # API endpoint definitions
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── middleware.py    # CORS, error handling
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── database.py      # Database connection
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic layer
│   ├── workers/             # Background job processors
│   └── main.py              # FastAPI application entry point
├── tests/
│   ├── api/                 # API endpoint tests
│   ├── services/            # Service layer tests
│   └── integration/         # End-to-end tests
├── alembic/                 # Database migrations
├── docker/                  # Docker configuration
└── requirements.txt         # Python dependencies
```

## Docker

### Build and Run

```bash
# Build image
docker build -f docker/Dockerfile -t backend:latest .

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up
```

### Environment Variables

See `.env.example` for all configuration options.

## API Endpoints

### Projects
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Variables
- `GET /api/v1/projects/{id}/variables` - List project variables
- `POST /api/v1/projects/{id}/variables` - Create variable
- `GET /api/v1/variables/{id}` - Get variable details
- `PUT /api/v1/variables/{id}` - Update variable
- `DELETE /api/v1/variables/{id}` - Delete variable

### Documents
- `GET /api/v1/projects/{id}/documents` - List documents
- `POST /api/v1/projects/{id}/documents` - Upload document
- `DELETE /api/v1/documents/{id}` - Delete document

### Processing
- `POST /api/v1/projects/{id}/jobs` - Create processing job
- `GET /api/v1/jobs/{id}` - Get job status
- `GET /api/v1/jobs/{id}/results` - Get job results
- `DELETE /api/v1/jobs/{id}` - Cancel job

### Export
- `POST /api/v1/projects/{id}/export` - Generate export file

## License

Proprietary
