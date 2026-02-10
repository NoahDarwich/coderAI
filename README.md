# CoderAI

A multi-tenant SaaS platform that transforms unstructured documents into structured datasets using LLM-powered extraction.

Researchers and analysts upload document corpora, define extraction variables through an AI-assisted wizard, iterate on a sample, then run full extraction and export results.

## Documentation

| Document | Purpose |
|----------|---------|
| [CODERAI_REFERENCE.md](CODERAI_REFERENCE.md) | **Single source of truth** — architecture, data model, API, pipeline, deployment |
| [USER_WORKFLOW.md](USER_WORKFLOW.md) | 6-step user workflow with UI-level detail |
| [API-SPECIFICATION.md](API-SPECIFICATION.md) | Full REST API + WebSocket request/response schemas |
| [FRONTEND-DESIGN.md](FRONTEND-DESIGN.md) | Frontend component architecture and design patterns |
| [backend/README.md](backend/README.md) | Backend quick start and project structure |
| [backend/IMPLEMENTATION_STATUS.md](backend/IMPLEMENTATION_STATUS.md) | Backend gap analysis vs. target architecture |

### Feature Specs

| Feature | Spec | Plan | Tasks |
|---------|------|------|-------|
| 001 - Frontend Workflow | [spec](specs/001-complete-user-workflow/spec.md) | [plan](specs/001-complete-user-workflow/plan.md) | [tasks](specs/001-complete-user-workflow/tasks.md) |
| 002 - Backend Implementation | [spec](specs/002-backend-implementation/spec.md) | [plan](specs/002-backend-implementation/plan.md) | [tasks](specs/002-backend-implementation/tasks.md) |

## Tech Stack

**Backend**: Python 3.11+ / FastAPI / SQLAlchemy 2.0 async / Alembic / LangChain 0.3+ / ARQ + Redis

**Frontend**: Next.js 15 / React 19 / TypeScript / Tailwind CSS / shadcn/ui / Zustand / TanStack Query

**Database**: PostgreSQL 16+ with Row-Level Security

**See** [CODERAI_REFERENCE.md Section 2.2](CODERAI_REFERENCE.md) for full technology decisions.

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # Edit: DATABASE_URL, OPENAI_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Development Phases

1. **Foundation (MVP)** — Project CRUD, document upload, variable definition, basic extraction, CSV export
2. **Core Features** — Auth + multi-tenancy, entity-level extraction, ARQ jobs, WebSocket, Excel export
3. **AI Co-pilot** — Variable suggestion, prompt refinement, guided setup
4. **Scale & Polish** — Chunking, parallel processing, observability, rate limiting
5. **Advanced (v2)** — Duplicate detection, external APIs, multi-model, team collaboration

See [CODERAI_REFERENCE.md Section 13](CODERAI_REFERENCE.md) for details.
