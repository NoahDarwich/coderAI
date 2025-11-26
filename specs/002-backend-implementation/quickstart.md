# Quickstart Guide: Backend Implementation

**Feature**: 002-backend-implementation
**Date**: 2025-11-26

This guide provides a quick overview of implementing the backend for the data extraction workflow.

---

## Prerequisites

Before starting implementation, ensure you have:

1. **Python 3.11+** installed
2. **PostgreSQL 15+** running locally or accessible
3. **Redis 7+** (optional for MVP, required for production)
4. **Docker** (optional, for containerized development)
5. **OpenAI API key** (for LLM integration)

---

## Development Setup

### 1. Create Backend Directory Structure

```bash
# From repository root
mkdir -p backend/src/{api/routes,core,models,schemas,services,workers}
mkdir -p backend/tests/{api,services,integration}
mkdir -p backend/alembic/versions
mkdir -p backend/docker
```

### 2. Initialize Python Project

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt <<EOF
fastapi==0.100.0
uvicorn[standard]==0.23.0
sqlalchemy==2.0.20
alembic==1.12.0
psycopg2-binary==2.9.7
pydantic==2.3.0
pydantic-settings==2.0.3
langchain==0.3.0
langchain-openai==0.2.0
httpx==0.24.1
python-multipart==0.0.6
pandas==2.0.3
openpyxl==3.1.2
PyMuPDF==1.23.0
python-docx==0.8.11
arq==0.25.0
redis==5.0.0
EOF

cat > requirements-dev.txt <<EOF
-r requirements.txt
pytest==7.4.2
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.24.1  # For TestClient
black==23.9.1
ruff==0.0.292
EOF

# Install dependencies
pip install -r requirements-dev.txt
```

### 3. Configure Database

```bash
# Create .env file
cat > .env <<EOF
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/data_extraction

# Redis (optional for MVP)
REDIS_URL=redis://localhost:6379/0

# LLM Provider
OPENAI_API_KEY=sk-...

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
EOF

# Create database
createdb data_extraction
```

### 4. Initialize Alembic

```bash
# Initialize Alembic
alembic init alembic

# Edit alembic.ini to use environment variable
sed -i 's|sqlalchemy.url = .*|sqlalchemy.url = postgresql://postgres:password@localhost:5432/data_extraction|' alembic.ini

# Edit alembic/env.py to import models
# (See data-model.md for migration setup details)
```

---

## Implementation Phases

### Phase 1: Database Models & Migrations (Week 1)

**Goal**: Define SQLAlchemy models and create initial migration

**Steps**:
1. Create models in `src/models/` (Project, Variable, Document, etc.)
2. Generate initial migration: `alembic revision --autogenerate -m "Initial schema"`
3. Apply migration: `alembic upgrade head`
4. Write model tests in `tests/unit/test_models.py`

**Key Files**:
- `src/models/project.py`
- `src/models/variable.py`
- `src/models/document.py`
- `src/models/processing_job.py`
- `src/models/extraction.py`
- `alembic/versions/001_initial_schema.py`

**Reference**: See [data-model.md](data-model.md) for entity definitions

---

### Phase 2: Core Services (Week 2)

**Goal**: Implement business logic without API layer

**Steps**:
1. Create service layer in `src/services/`
2. Implement prompt generation logic
3. Integrate LangChain for LLM calls
4. Write service tests (mocked LLM responses)

**Key Files**:
- `src/services/prompt_generator.py` - Generate prompts from variable definitions
- `src/services/llm_client.py` - LangChain integration with retry logic
- `src/services/document_processor.py` - PDF/DOCX parsing
- `src/services/extraction_service.py` - Orchestrate LLM calls
- `src/services/job_manager.py` - Create and track processing jobs
- `src/services/export_service.py` - Generate CSV/Excel exports

**Testing**:
```bash
# Run service tests (mocked LLM)
pytest tests/services/ -v

# Coverage should be >90% for services
pytest tests/services/ --cov=src/services --cov-report=term-missing
```

**Reference**: See [research.md](research.md) for technology decisions

---

### Phase 3: API Routes (Week 3)

**Goal**: Implement REST API endpoints

**Steps**:
1. Create FastAPI app in `src/main.py`
2. Implement routes in `src/api/routes/`
3. Add Pydantic schemas in `src/schemas/`
4. Write API tests using TestClient

**Key Files**:
- `src/main.py` - FastAPI app initialization, CORS, middleware
- `src/api/routes/projects.py` - Project CRUD
- `src/api/routes/variables.py` - Variable CRUD
- `src/api/routes/documents.py` - Document upload
- `src/api/routes/processing.py` - Job management
- `src/api/routes/exports.py` - Export generation
- `src/schemas/project.py` - Pydantic request/response schemas
- `src/api/dependencies.py` - Database session dependency

**Testing**:
```bash
# Run API tests
pytest tests/api/ -v

# Test with real HTTP requests
uvicorn src.main:app --reload
curl http://localhost:8000/api/v1/projects
```

**Reference**: See [contracts/openapi.yaml](contracts/openapi.yaml) for API spec

---

### Phase 4: Background Workers (Week 4)

**Goal**: Implement asynchronous job processing

**Steps**:
1. Create worker in `src/workers/processing_worker.py`
2. Integrate Arq for job queue (or use in-memory queue for MVP)
3. Test background processing end-to-end

**Key Files**:
- `src/workers/processing_worker.py` - Process documents in background
- `src/services/job_manager.py` - Enqueue jobs, track progress

**Testing**:
```bash
# Start worker
arq src.workers.processing_worker.WorkerSettings

# Create job via API, verify worker processes it
pytest tests/integration/test_job_processing.py -v
```

**MVP Simplification**:
- Use FastAPI `BackgroundTasks` instead of Arq for initial implementation
- Migrate to Arq + Redis when persistence becomes critical

---

### Phase 5: Integration & Deployment (Week 5)

**Goal**: Deploy backend and integrate with frontend

**Steps**:
1. Create Dockerfile and docker-compose.yml
2. Deploy to Railway/Render
3. Update frontend API service layer to use real backend
4. End-to-end testing

**Key Files**:
- `docker/Dockerfile`
- `docker/docker-compose.yml`
- `.github/workflows/deploy.yml` (CI/CD)

**Deployment**:
```bash
# Build Docker image
docker build -f docker/Dockerfile -t backend:latest .

# Run locally
docker-compose up

# Deploy to Railway (example)
railway up
```

---

## Development Workflow

### Daily Development Loop

```bash
# 1. Start development server
uvicorn src.main:app --reload --port 8000

# 2. Make changes to code

# 3. Run tests
pytest tests/ -v --cov=src

# 4. Format code
black src/ tests/
ruff check src/ tests/ --fix

# 5. Commit changes
git add .
git commit -m "feat: implement project CRUD endpoints"
```

### Database Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Add extraction feedback table"

# Review migration in alembic/versions/
# Edit if autogenerate missed anything

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Testing Strategy

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/api/test_projects.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests only (slower, uses test DB)
pytest tests/integration/ -v

# Run with real LLM (expensive, slow)
pytest tests/integration/ -v --use-real-llm
```

---

## Architecture Overview

### Request Flow

```
Frontend Request
  ↓
FastAPI Route (/api/routes/projects.py)
  ↓
Service Layer (/services/...)
  ↓
Database Models (/models/...)
  ↓
PostgreSQL
```

### Background Job Flow

```
API creates ProcessingJob (status=PENDING)
  ↓
Worker picks up job (status=PROCESSING)
  ↓
For each (document, variable):
  → Extract text from document
  → Get latest prompt for variable
  → Call LLM with prompt + document text
  → Parse response (structured output)
  → Create Extraction record
  → Log to ProcessingLog
  ↓
Update job progress (0-100%)
  ↓
Job status → COMPLETE
```

### Service Layer Pattern

Each service is responsible for a domain:

- **PromptGenerator**: Generate LLM prompts from variable definitions
- **LLMClient**: Call OpenAI/Anthropic with retry logic
- **DocumentProcessor**: Parse PDF/DOCX, chunk large documents
- **ExtractionService**: Orchestrate (document × variable) LLM calls
- **JobManager**: Create jobs, track progress, handle cancellation
- **ExportService**: Aggregate extractions, generate CSV/Excel

**Benefits**:
- Testable (mock database, mock LLM)
- Reusable (services can be called from API or CLI)
- Maintainable (clear separation of concerns)

---

## Key Design Decisions

### 1. Async-First Architecture

**Decision**: Use `async/await` throughout

**Rationale**:
- FastAPI is async-native
- SQLAlchemy 2.0 supports async
- LangChain supports async LLM calls
- Better concurrency for I/O-bound operations

**Example**:
```python
# All database queries are async
async def get_project(db: AsyncSession, project_id: str):
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()
```

### 2. Structured Output with Pydantic

**Decision**: Use Pydantic for LLM response parsing

**Rationale**:
- Type-safe extraction results
- Automatic validation
- Clear error messages when LLM returns invalid JSON

**Example**:
```python
from pydantic import BaseModel

class ExtractionResult(BaseModel):
    value: str
    confidence: float
    source_text: str

# LangChain automatically parses LLM response to this schema
```

### 3. Database Transaction Boundaries

**Decision**: Explicit transactions with context manager

**Rationale**:
- Atomic operations (all-or-nothing)
- Automatic rollback on errors
- Prevents orphaned records

**Example**:
```python
async with db.begin():
    project = Project(name="Test")
    db.add(project)
    await db.flush()  # Get project.id
    variable = Variable(project_id=project.id, name="var1")
    db.add(variable)
    # Commit happens automatically if no exception
```

---

## Common Issues & Solutions

### Issue: Database connection pool exhausted

**Symptom**: `TimeoutError: QueuePool limit exceeded`

**Solution**:
```python
# In src/core/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,        # Increase from default 5
    max_overflow=10,     # Allow overflow connections
    pool_pre_ping=True   # Test connections before use
)
```

### Issue: LLM API rate limits

**Symptom**: `RateLimitError: 429 Too Many Requests`

**Solution**:
```python
# In src/services/llm_client.py
from langchain.llms import OpenAI

llm = OpenAI(
    max_retries=3,
    request_timeout=30,
    # Add rate limiting
    rate_limiter=RateLimiter(max_calls=10, period=60)
)
```

### Issue: Background jobs not processing

**Symptom**: Jobs stuck in `PENDING` status

**Solution**:
```bash
# Verify worker is running
arq src.workers.processing_worker.WorkerSettings

# Check Redis connection
redis-cli ping

# Check worker logs for errors
docker logs backend-worker
```

---

## Next Steps

After quickstart implementation:

1. **Load Testing**: Use Locust to test 100 concurrent requests
2. **Monitoring**: Add Sentry for error tracking
3. **Logging**: Configure structured logging (JSON format)
4. **Caching**: Add Redis caching for frequent queries
5. **Authentication**: Add JWT-based authentication
6. **Documentation**: Auto-generate API docs with FastAPI

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0 Docs**: https://docs.sqlalchemy.org/en/20/
- **LangChain Docs**: https://python.langchain.com/docs/
- **Alembic Tutorial**: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- **Arq Docs**: https://arq-docs.helpmanual.io/

---

**Ready to Start**: All design artifacts complete. Proceed to implementation!
