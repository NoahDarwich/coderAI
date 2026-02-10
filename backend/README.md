# Data Extraction Backend

FastAPI backend implementing a **user-configurable corpus processing pipeline**. Each project defines its own domain, extraction targets, and variables. The system auto-generates LLM assistant configurations, ingests documents in all common formats, processes them through LangChain-powered extraction stages, and delivers structured datasets.

**Pipeline Architecture:** See [ai_agent_reference.md](/ai_agent_reference.md) for detailed pipeline stages, LLM integration, and implementation patterns.

## Tech Stack

- **Framework**: FastAPI 0.100+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0 (async)
- **LLM Integration**: LangChain 0.3+ (multi-provider: OpenAI, Anthropic, local models)
- **Document Ingestion**: PyMuPDF (PDF), python-docx (DOCX), pandas + pyarrow (CSV/JSON/Parquet), plain text
- **Data Export**: pandas + openpyxl (CSV + Excel with filtering and metadata)
- **Background Jobs**: TBD (job queue strategy to be decided)
- **Migrations**: Alembic

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional for MVP)
- OpenAI API key

## Quick Start

### 1. Setup Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your configuration:
# - DATABASE_URL
# - OPENAI_API_KEY
# - ALLOWED_ORIGINS
```

### 4. Setup Database

```bash
# Create PostgreSQL database
createdb data_extraction

# Run migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/          # API endpoint routes
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── middleware.py    # CORS, error handling
│   ├── core/
│   │   ├── config.py        # Settings management
│   │   └── database.py      # Database connection
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic
│   │   ├── prompt_generator.py
│   │   ├── llm_client.py
│   │   ├── document_processor.py
│   │   ├── extraction_service.py
│   │   ├── job_manager.py
│   │   └── export_service.py
│   ├── workers/             # Background job workers
│   └── main.py              # FastAPI app initialization
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── docker/                  # Docker configuration
└── requirements.txt         # Python dependencies
```

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
ruff check src/ tests/ --fix

# Type checking (optional)
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

# View migration history
alembic history
```

## API Documentation

### Base URL

```
http://localhost:8000/api/v1
```

### Key Endpoints

**Projects**
- `POST /projects` - Create project
- `GET /projects` - List projects
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

**Variables**
- `GET /projects/{id}/variables` - List variables
- `POST /projects/{id}/variables` - Create variable
- `PUT /variables/{id}` - Update variable
- `DELETE /variables/{id}` - Delete variable

**Documents** (all common formats: PDF, DOCX, TXT, CSV, JSON, Parquet)
- `POST /projects/{id}/documents` - Upload document(s) or bulk ingest from tabular formats
- `GET /projects/{id}/documents` - List documents
- `DELETE /documents/{id}` - Delete document

**Processing**
- `POST /projects/{id}/jobs` - Create processing job
- `GET /jobs/{id}` - Get job status
- `GET /jobs/{id}/results` - Get extraction results
- `POST /extractions/{id}/feedback` - Submit feedback

**Export** (CSV + Excel with filtering)
- `POST /projects/{id}/export` - Generate export file (CSV or Excel, with optional confidence scores, source text, codebook)

For complete API documentation, visit http://localhost:8000/docs after starting the server.

## Pipeline Architecture

The processing pipeline runs per document through these stages:

```
Ingestion (multi-format) → Extraction → Enrichment (LLM per variable) → Post-Processing → Storage → Export
```

- **Assistant configs** are auto-generated from user-defined variables (not manually configured)
- **LLM calls** go through LangChain for provider flexibility
- **Atomic transactions** ensure all-or-nothing per document
- **Feedback loop** allows users to correct extractions and refine prompts

**Deferred (v2):** Duplicate detection, external API enrichment (geocoding), advanced job queue

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL` - PostgreSQL connection URL (required)
- `OPENAI_API_KEY` - OpenAI API key (required)
- `REDIS_URL` - Redis connection URL (optional for MVP)
- `ALLOWED_ORIGINS` - CORS allowed origins (required)
- `DEBUG` - Enable debug mode (default: True)
- `LOG_LEVEL` - Logging level (default: INFO)

## Docker Deployment

```bash
# Build image
docker build -f docker/Dockerfile -t data-extraction-backend:latest .

# Run with docker-compose
cd docker
docker-compose up
```

## Performance Targets

- API response time: <200ms (p95) for CRUD operations
- Sample processing (20 docs × 5 vars): <5 minutes with real LLM calls
- Export generation (100 docs × 10 vars): <3 seconds
- Concurrent requests: Support 100 concurrent API requests

## Troubleshooting

### Database connection issues

```bash
# Test database connection
psql -U postgres -d data_extraction -c "SELECT 1"

# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql+asyncpg://user:pass@host:port/dbname
```

### LLM API rate limits

If you encounter rate limit errors:
1. Check `LLM_RATE_LIMIT_CALLS` and `LLM_RATE_LIMIT_PERIOD` in .env
2. Reduce concurrent job processing
3. Add delays between LLM calls

### Alembic migration errors

```bash
# Check current migration version
alembic current

# View pending migrations
alembic heads

# Stamp database at current version (use carefully)
alembic stamp head
```

## Contributing

1. Follow the implementation tasks in `/specs/002-backend-implementation/tasks.md`
2. Write tests for new features
3. Ensure code passes linting and formatting checks
4. Update API documentation if adding new endpoints

## License

See repository LICENSE file.

## Support

For issues and questions, refer to:
- Implementation plan: `/specs/002-backend-implementation/plan.md`
- API contracts: `/specs/002-backend-implementation/contracts/`
- Quickstart guide: `/specs/002-backend-implementation/quickstart.md`
