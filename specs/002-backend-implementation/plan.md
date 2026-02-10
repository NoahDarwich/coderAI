# Implementation Plan: Backend Implementation for Data Extraction Workflow

**Branch**: `002-backend-implementation` | **Date**: 2025-11-26 | **Updated**: 2026-02-10
**Spec**: [spec.md](spec.md) | **Source of Truth**: [CODERAI_REFERENCE.md](/CODERAI_REFERENCE.md)

## Summary

Build a FastAPI backend service implementing a **multi-tenant, user-configurable corpus processing pipeline** that powers the data extraction workflow. Each project defines its own domain, extraction targets, and variables. The system auto-generates LLM assistant configurations from user definitions, ingests documents (PDF, DOCX, TXT, HTML), processes them through LangChain-powered extraction stages, and delivers structured datasets via CSV + Excel export.

The backend uses **ARQ + Redis** for background job processing, **JWT authentication** with **Row-Level Security** for multi-tenancy, **WebSocket** for real-time progress, and **AI agents** (co-pilot, extractor, refiner) for LLM orchestration.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.100+, SQLAlchemy 2.0 async, Pydantic V2, LangChain 0.3+
**Job Queue**: ARQ + Redis 7+ (async-native)
**Auth**: JWT (access + refresh tokens) with PostgreSQL Row-Level Security
**Document Processing**: PyMuPDF (PDF), python-docx (DOCX), BeautifulSoup (HTML)
**Export**: pandas + openpyxl (CSV + Excel with codebook)
**Storage**: PostgreSQL 16+ with RLS
**Testing**: pytest with pytest-asyncio, coverage >80%
**Target Platform**: Linux server (containerized with Docker)
**Project Type**: Web backend (REST API + WebSocket serving existing Next.js frontend)

**Performance Goals**:
  - API response time <200ms (p95) for CRUD operations
  - Sample processing (20 docs × 5 vars) <5 minutes with real LLM calls
  - Export generation (100 docs × 10 vars) <3 seconds
  - Support 100 concurrent API requests without degradation

**Constraints**:
  - Must integrate with existing Next.js frontend via RESTful API + WebSocket
  - LLM API costs must be optimized (batch calls where possible)
  - Background jobs must survive server restarts (ARQ + Redis persistence)
  - Database migrations must be reversible (Alembic)
  - Multi-tenant isolation at database level (RLS)

**Scale/Scope**:
  - Support 100 concurrent projects
  - Handle projects with up to 10,000 documents
  - Support schemas with up to 50 variables
  - Process ~10-100 LLM API calls per minute (rate-limited)

## Project Structure

### Documentation (this feature)

```text
specs/002-backend-implementation/
├── spec.md              # Feature specification
├── plan.md              # This file
├── data-model.md        # Entity definitions (10 entities)
└── tasks.md             # Implementation tasks (5-phase roadmap)
```

### Source Code (target structure from CODERAI_REFERENCE.md Section 2.3)

```text
backend/
├── app/
│   ├── api/                    # FastAPI routes
│   │   ├── routes/
│   │   │   ├── projects.py
│   │   │   ├── documents.py
│   │   │   ├── variables.py
│   │   │   ├── jobs.py
│   │   │   └── export.py
│   │   └── deps.py             # Dependencies (auth, db session, tenant)
│   │
│   ├── core/                   # Configuration, security
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   ├── db/                     # Database layer
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── session.py          # Async session factory
│   │   └── rls.py              # Row-level security setup
│   │
│   ├── services/               # Business logic
│   │   ├── document_processor.py
│   │   ├── extraction_service.py
│   │   ├── prompt_generator.py
│   │   ├── feedback_analyzer.py
│   │   └── export_service.py
│   │
│   ├── agents/                 # LLM agent logic
│   │   ├── copilot.py          # Setup assistant
│   │   ├── extractor.py        # Extraction assistants
│   │   └── refiner.py          # Prompt refinement
│   │
│   ├── workers/                # ARQ background tasks
│   │   ├── tasks.py
│   │   └── worker_settings.py
│   │
│   └── main.py                 # FastAPI app entry
│
├── migrations/                 # Alembic
├── tests/
│   ├── api/                    # API endpoint tests
│   ├── services/               # Service layer unit tests
│   ├── integration/            # End-to-end tests
│   └── conftest.py
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt

frontend/                       # Existing from 001-complete-user-workflow
├── src/
└── package.json
```

**Current Code Location**: Code currently lives under `backend/src/`. A restructure to `backend/app/` is planned as part of Phase 1 foundation work.

## Architecture Decisions (from CODERAI_REFERENCE.md)

| Decision | Choice | Impact |
|----------|--------|--------|
| Domain | User-configurable per project | Each project defines its own extraction pipeline |
| LLM Provider | LangChain 0.3+ | Multi-provider abstraction (OpenAI primary) |
| Document Formats | PDF, DOCX, TXT, HTML (v1) | Broader format support in Phase 4 |
| Assistant Config | Auto-generated from variables | prompt_generator.py builds configs from Variable + Project |
| Job Queue | ARQ + Redis 7+ | Async-native, lightweight, persistent |
| Auth | JWT (access + refresh tokens) | Phase 2 feature |
| Multi-tenancy | PostgreSQL Row-Level Security | Database-enforced isolation |
| Real-time | WebSocket `/ws/jobs/{job_id}` | Phase 2 feature |
| AI Agents | Co-pilot, Extractor, Refiner | Phase 3 for co-pilot |
| DB Layer | SQLAlchemy 2.0 async + Alembic | Keep existing |
| Export | CSV + Excel with codebook | export_service.py with pandas + openpyxl |
| Circuit Breaker | 5 failures → open, 30s → half-open | LLM call resilience |
| Deferred (v2) | Duplicate detection, external APIs | Phase 5 |

## Pipeline Stages (per document)

From CODERAI_REFERENCE.md Section 4:

```
Document Upload → Ingestion → Extraction → Post-Processing → Storage → Export
```

1. **Ingestion**: Parse document from supported format, extract text, chunk if large
2. **Extraction**: For document-level: call LLM per variable. For entity-level: identify entities first, then extract per entity × variable
3. **Post-Processing**: Type coercion, validation against user rules, default values, confidence check, multi-value handling
4. **Storage**: Atomic save of all extractions per document (transaction per document)
5. **Export**: Aggregate into CSV/Excel with metadata columns and codebook

## Development Phases (from CODERAI_REFERENCE.md Section 13)

### Phase 1: Foundation (MVP)
- Project CRUD
- Document upload + parsing (PDF, TXT)
- Variable definition (manual)
- Basic extraction pipeline (sequential)
- Export to CSV
- Single-user (no auth)

### Phase 2: Core Features
- Authentication + multi-tenancy (JWT + RLS)
- Entity-level extraction
- Sample → Feedback → Full run workflow
- Job queue with ARQ + Redis
- Real-time progress (WebSocket)
- Excel export with codebook

### Phase 3: AI Co-pilot
- Variable suggestion
- Prompt refinement from feedback
- Guided setup wizard

### Phase 4: Scale & Polish
- Document chunking for large files
- Parallel processing
- Observability (metrics, tracing)
- Rate limiting + cost controls
- DOCX, HTML format support

### Phase 5: Advanced (v2)
- Duplicate detection
- External API enrichment (geocoding, etc.)
- Multi-model support
- Team collaboration

## Complexity Tracking

| Area | Approach | Justification |
|------|----------|---------------|
| Background jobs (ARQ + Redis) | Required from Phase 2 | Document processing takes minutes/hours, cannot block API |
| JWT auth + RLS | Phase 2 | Multi-tenant isolation is security-critical |
| Circuit breaker | Phase 1 resilience | Prevents cascading LLM failures |
| Prompt versioning | Phase 1 | Feedback-driven refinement requires version history |
| WebSocket | Phase 2 | Real-time progress for long-running jobs |

**Accepted Technical Debt:**
- Phase 1 runs single-user with no auth (add in Phase 2)
- Phase 1 uses FastAPI BackgroundTasks (migrate to ARQ in Phase 2)
- Phase 1 supports PDF + TXT only (add DOCX, HTML in Phase 4)
- No observability in Phase 1 (add Prometheus + OpenTelemetry in Phase 4)

## Plan Status

### Current State

Existing code lives under `backend/src/` with:
- 9 SQLAlchemy models (need expansion for new fields)
- 7 Pydantic schema modules (need updates)
- 5 route modules (need restructuring)
- 7 services (need refactoring for LangChain-only, pipeline stages, post-processing)
- Empty workers directory (need ARQ implementation)
- No agents directory (need co-pilot, extractor, refiner)

See [IMPLEMENTATION_STATUS.md](/backend/IMPLEMENTATION_STATUS.md) for detailed gap analysis.

### Next Steps

1. Restructure `backend/src/` → `backend/app/` (Phase 1)
2. Update models to match CODERAI_REFERENCE.md Section 3
3. Implement basic extraction pipeline (sequential, single-user)
4. Add CSV export
5. Proceed through phases 2-5 as defined above

---

**Plan Complete**: 2025-11-26
**Plan Updated**: 2026-02-10 (aligned with CODERAI_REFERENCE.md)
