# CoderAI Backend

FastAPI backend for CoderAI — a platform that transforms unstructured documents into structured datasets using LLM-powered extraction.

**Primary Reference:** See [CODERAI_REFERENCE.md](/CODERAI_REFERENCE.md) for complete architecture, data model, and API design.

## Tech Stack

- **Framework**: FastAPI (async)
- **Database**: PostgreSQL 16 with Row-Level Security (multi-tenancy)
- **ORM**: SQLAlchemy 2.0 async + Alembic migrations
- **Job Queue**: ARQ + Redis 7 (async-native)
- **LLM**: LangChain 0.3+ (OpenAI primary, multi-provider ready)
- **Document Parsing**: PyMuPDF (PDF), python-docx (DOCX), BeautifulSoup (HTML)
- **Export**: pandas + openpyxl (CSV + Excel)
- **Auth**: JWT (access + refresh tokens)
- **Observability**: Prometheus metrics, circuit breaker, Redis rate limiter

## Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- OpenAI API key

## Quick Start

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: DATABASE_URL, OPENAI_API_KEY, REDIS_URL

createdb coderai
alembic upgrade head

uvicorn src.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/                # FastAPI endpoints
│   │   │   ├── auth.py            # JWT login/register/refresh
│   │   │   ├── projects.py        # Project CRUD
│   │   │   ├── documents.py       # Document upload + management
│   │   │   ├── variables.py       # Variable CRUD + prompt generation
│   │   │   ├── processing.py      # Jobs, extractions, feedback
│   │   │   ├── exports.py         # CSV/Excel/codebook export
│   │   │   ├── copilot.py         # AI co-pilot endpoints
│   │   │   └── websocket.py       # Real-time job progress
│   │   ├── dependencies.py        # Auth, DB session, RLS context
│   │   └── middleware.py
│   ├── core/                      # Configuration, security, infra
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py            # JWT + password hashing
│   │   ├── redis.py
│   │   ├── rls.py                 # Row-Level Security policies
│   │   ├── rate_limiter.py        # Redis token-bucket rate limiter
│   │   ├── metrics.py             # Prometheus counters/histograms
│   │   ├── job_subscriber.py
│   │   └── websocket.py
│   ├── models/                    # SQLAlchemy ORM models
│   ├── schemas/                   # Pydantic request/response schemas
│   ├── services/                  # Business logic
│   │   ├── document_processor.py  # PDF/DOCX/HTML/TXT parsing + chunking
│   │   ├── text_extraction_service.py  # LLM extraction + circuit breaker
│   │   ├── prompt_generator.py    # Auto-generate prompts from variables
│   │   ├── feedback_analyzer.py   # Analyze feedback patterns
│   │   ├── export_service.py      # CSV/Excel/codebook generation
│   │   ├── post_processor.py      # Type coercion, validation, defaults
│   │   ├── response_parser.py     # LLM response parsing
│   │   └── job_manager.py         # Job orchestration
│   ├── agents/                    # LLM agent logic
│   │   ├── copilot.py             # Setup assistant (LangChain + Redis state)
│   │   ├── extractor.py           # Extraction wrapper
│   │   └── refiner.py             # LLM-based prompt refinement
│   ├── workers/                   # ARQ background tasks
│   │   ├── settings.py            # WorkerSettings + Redis config
│   │   ├── extraction_worker.py   # Document extraction jobs
│   │   ├── refinement_worker.py   # Prompt refinement jobs
│   │   └── export_worker.py       # Export generation jobs
│   └── main.py                    # FastAPI app entry point
├── docker/                        # Dockerfile + docker-compose.yml
├── migrations/                    # Alembic
├── run_worker.py                  # ARQ worker entry point
└── requirements.txt
```

## Commands

```bash
# Dev server
uvicorn src.main:app --reload

# Run ARQ worker
python run_worker.py
# Or: arq src.workers.settings.WorkerSettings

# Tests
pytest
pytest --cov=src --cov-report=html

# Migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Code quality
black src/ tests/
ruff check src/ tests/ --fix
```

## API Endpoints

All endpoints are prefixed with `/api/v1/`.

| Resource | Endpoints |
|----------|-----------|
| **Auth** | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh` |
| **Projects** | `POST /projects`, `GET /projects`, `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}` |
| **Documents** | `POST /projects/{id}/documents`, `GET /projects/{id}/documents`, `GET /documents/{id}`, `DELETE /documents/{id}` |
| **Variables** | `POST /projects/{id}/variables`, `GET /projects/{id}/variables`, `PATCH /variables/{id}`, `DELETE /variables/{id}`, `POST /variables/{id}/generate-prompt`, `POST /variables/{id}/refine` |
| **Jobs** | `POST /projects/{id}/jobs`, `GET /jobs/{id}`, `POST /jobs/{id}/pause`, `POST /jobs/{id}/resume`, `DELETE /jobs/{id}` |
| **Extractions** | `GET /projects/{id}/extractions`, `GET /extractions/{id}`, `POST /extractions/{id}/feedback` |
| **Export** | `POST /projects/{id}/export`, `GET /exports/{id}` |
| **Co-pilot** | `POST /projects/{id}/copilot/message`, `POST /copilot/suggest-variables`, `POST /copilot/refine`, `POST /copilot/refine/apply` |
| **WebSocket** | `/ws/jobs/{job_id}` (real-time progress) |
| **Health** | `GET /health/live`, `GET /health/ready` |
| **Metrics** | `GET /metrics` (Prometheus) |

## Environment Variables

See `.env.example`. Key variables:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/coderai
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=...
ALLOWED_ORIGINS=http://localhost:3000
LLM_MODEL=gpt-4o
```
