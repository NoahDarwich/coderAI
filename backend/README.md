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
pip install -r requirements-dev.txt

cp .env.example .env
# Edit .env: DATABASE_URL, OPENAI_API_KEY, REDIS_URL

createdb coderai
alembic upgrade head

uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Project Structure

```
backend/
├── app/
│   ├── api/routes/             # FastAPI endpoints
│   ├── core/                   # Config, security, exceptions
│   ├── db/                     # Models, session, RLS
│   ├── services/               # Business logic
│   ├── agents/                 # LLM agents (co-pilot, extractor, refiner)
│   ├── workers/                # ARQ background tasks
│   └── main.py
├── migrations/                 # Alembic
├── tests/
└── pyproject.toml
```

## Commands

```bash
# Dev server
uvicorn app.main:app --reload

# Run worker
arq app.workers.worker_settings.WorkerSettings

# Tests
pytest
pytest --cov=app --cov-report=html

# Migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Code quality
black app/ tests/
ruff check app/ tests/ --fix
```

## API Endpoints

| Resource | Endpoints |
|----------|-----------|
| **Projects** | `POST /projects`, `GET /projects`, `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}` |
| **Documents** | `POST /projects/{id}/documents`, `GET /projects/{id}/documents`, `GET /documents/{id}`, `DELETE /documents/{id}` |
| **Variables** | `POST /projects/{id}/variables`, `GET /projects/{id}/variables`, `PATCH /variables/{id}`, `DELETE /variables/{id}` |
| **Jobs** | `POST /projects/{id}/jobs`, `GET /jobs/{id}`, `POST /jobs/{id}/pause`, `POST /jobs/{id}/resume`, `DELETE /jobs/{id}` |
| **Extractions** | `GET /projects/{id}/extractions`, `GET /extractions/{id}`, `POST /extractions/{id}/feedback` |
| **Export** | `POST /projects/{id}/export`, `GET /exports/{id}` |
| **Co-pilot** | `POST /projects/{id}/copilot/message`, `POST /copilot/suggest-variables` |
| **WebSocket** | `/ws/jobs/{job_id}` (real-time progress) |

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
