# coderAI Development Guidelines

Last updated: 2026-02-11

**Primary Reference**: [`CODERAI_REFERENCE.md`](/CODERAI_REFERENCE.md) is the single source of truth for architecture, data model, API design, and pipeline stages. All implementation work should align with that document.

## Active Technologies

**Backend**:
- Python 3.11+ / FastAPI (async) / Pydantic V2
- SQLAlchemy 2.0 async + Alembic migrations
- PostgreSQL 16 with Row-Level Security (multi-tenancy)
- ARQ + Redis 7 (async job queue)
- LangChain 0.3+ (LLM abstraction: OpenAI primary, multi-provider ready)
- Document parsing: PyMuPDF (PDF), python-docx (DOCX), BeautifulSoup (HTML)
- Export: pandas + openpyxl (CSV + Excel)
- Auth: JWT (access + refresh tokens)

**Frontend**:
- TypeScript 5.6+ / React 19 / Next.js 15 (App Router)
- Tailwind CSS 4.0 / shadcn/ui
- Zustand (state), TanStack Query (data fetching), TanStack Table (grids)

## Project Structure

```text
coderai/
├── backend/
│   ├── src/
│   │   ├── api/routes/         # FastAPI endpoints
│   │   ├── core/               # Config, security, database, redis
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic
│   │   ├── agents/             # LLM agents (co-pilot, extractor, refiner)
│   │   ├── workers/            # ARQ background tasks
│   │   └── main.py
│   ├── migrations/             # Alembic
│   ├── docker/                 # Dockerfile + docker-compose.yml
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   ├── components/
│   │   ├── services/           # API clients
│   │   └── types/
│   └── package.json
└── docker-compose.yml
```

## Commands

```bash
# Backend
cd backend && pytest                    # Run tests
cd backend && alembic upgrade head      # Run migrations
cd backend && uvicorn src.main:app --reload  # Dev server
cd backend && arq src.workers.settings.WorkerSettings  # Start worker
cd backend && python run_worker.py      # Start worker (alternative)

# Frontend
cd frontend && npm test && npm run lint
```

## Architecture

- **Pipeline**: Upload Documents → Define Variables (AI-assisted) → Sample Run → Review & Refine → Full Run → Export
- **Pipeline stages per document**: Ingestion → Extraction → Post-Processing → Storage → Export
- **AI agents**: Co-pilot (setup assistant), Extraction assistants (per-variable), Refinement agent (prompt improvement)
- **Job system**: ARQ + Redis for async processing (extraction, prompt refinement, export)
- **Real-time**: WebSocket for job progress updates
- **Multi-tenancy**: PostgreSQL RLS, database-enforced isolation
- **LLM resilience**: Retry with exponential backoff + circuit breaker

## Development Phases

1. **Phase 1 (MVP)**: Project CRUD, document upload (PDF/TXT), variable definition, basic extraction, CSV export, single-user
2. **Phase 2**: Auth + multi-tenancy, entity-level extraction, sample/feedback/full workflow, ARQ jobs, WebSocket, Excel + codebook
3. **Phase 3**: AI co-pilot (variable suggestions, prompt refinement, guided wizard)
4. **Phase 4**: Document chunking, parallel processing, observability, rate limiting, DOCX/HTML
5. **Phase 5 (v2)**: Duplicate detection, external API enrichment, multi-model, team collaboration
