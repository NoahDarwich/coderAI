# Implementation Plan: Backend Implementation for Data Extraction Workflow

**Branch**: `002-backend-implementation` | **Date**: 2025-11-26 | **Spec**: [spec.md](/home/noahdarwich/code/coderAI/specs/002-backend-implementation/spec.md)
**Input**: Feature specification from `/specs/002-backend-implementation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a FastAPI backend service that powers the 5-step data extraction workflow by managing projects, generating LLM prompts, orchestrating batch document processing, and delivering structured datasets. The backend will integrate with the existing Next.js frontend (001-complete-user-workflow) through a RESTful API, using PostgreSQL for persistence and background job processing for scalability.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.100+, SQLAlchemy 2.0, Pydantic V2, LangChain 0.3+, OpenAI Python SDK
**Storage**: PostgreSQL 15+ (primary database), Redis 7+ (job queue and caching)
**Testing**: pytest with pytest-asyncio, coverage >80%
**Target Platform**: Linux server (containerized with Docker), deployed to Railway/Render
**Project Type**: Web backend (REST API serving existing Next.js frontend)
**Performance Goals**:
  - API response time <200ms (p95) for CRUD operations
  - Sample processing (20 docs × 5 vars) <5 minutes with real LLM calls
  - Export generation (100 docs × 10 vars) <3 seconds
  - Support 100 concurrent API requests without degradation
**Constraints**:
  - Must integrate with existing Next.js 16 frontend via RESTful API
  - LLM API costs must be optimized (batch calls where possible)
  - Background jobs must survive server restarts (persistent job queue)
  - Database migrations must be reversible
**Scale/Scope**:
  - Support 100 concurrent projects
  - Handle projects with up to 1000 documents
  - Support schemas with up to 50 variables
  - Process ~10-100 LLM API calls per minute (rate-limited)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

**I. UI-First Design:**
- [x] All features align with Phase 1 scope - **EXCEPTION**: This is Phase 2 backend integration work
- [x] Mock data strategy defined - **CLARIFICATION**: Backend replaces mocks from 001-complete-user-workflow
- [x] Service layer abstraction identified - Frontend already has typed service layer ready for integration

**II. User Experience Excellence:**
- [x] Accessibility requirements identified - Backend must return structured errors for frontend display
- [x] Error states and loading states planned - API returns standardized error codes and progress states
- [x] Mobile responsiveness considerations - N/A for backend, handled by frontend

**III. Rapid Iteration:**
- [x] shadcn/ui components identified - N/A for backend
- [x] Technical debt acceptable for Phase 1 documented - See Complexity Tracking below
- [x] Phase 2 integration points noted - This IS Phase 2 (backend integration)

**IV. User Workflow Fidelity:**
- [x] Feature maps to specific USER_WORKFLOW.md steps (1-5) - All steps 1-5
- [x] Does NOT introduce features outside the 5-step workflow - Backend only implements workflow support
- [x] Navigation flow aligns with workflow progression - Backend state transitions match UI flow
- [x] Workflow design principles applied:
  - Clarity over cleverness - Simple REST API, predictable state transitions
  - Progress visibility - Real-time progress tracking via API polling
  - Reversibility - Schema versioning allows rollback
  - Asynchronous awareness - Background jobs with explicit status endpoints
  - Data transparency - Complete audit logging of processing events

### User Workflow Mapping

**Primary Workflow Step(s):** All steps 1-5 (backend services supporting complete workflow)

**Workflow Compliance:**
- Step 1 (Project Setup & Document Input): Backend stores project metadata, handles document uploads, validates inputs
- Step 2 (Schema Definition Wizard): Backend stores variable definitions, generates LLM prompts, provides AI suggestions
- Step 3 (Schema Review & Confirmation): Backend retrieves complete schema for preview, supports CRUD operations on variables
- Step 4 (Processing - Sample & Full): Backend orchestrates sample/full processing jobs, manages LLM API calls, tracks progress, handles errors
- Step 5 (Results & Export): Backend aggregates extractions, generates export files in requested formats, includes metadata

**Rationale:** The backend is the execution engine for the user workflow. While the frontend (001-complete-user-workflow) handles user interaction with mock data, this backend implementation provides real data processing, LLM orchestration, and persistent storage. The backend's API structure mirrors the frontend's service layer contracts, enabling seamless integration.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Web application (frontend already exists from 001-complete-user-workflow)
backend/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── projects.py        # Project CRUD endpoints
│   │   │   ├── variables.py       # Variable definition endpoints
│   │   │   ├── documents.py       # Document upload endpoints
│   │   │   ├── processing.py      # Job creation and status endpoints
│   │   │   └── exports.py         # Export generation endpoints
│   │   ├── dependencies.py        # FastAPI dependencies (DB session, auth)
│   │   └── middleware.py          # CORS, error handling, logging
│   ├── core/
│   │   ├── config.py              # Settings (env vars, DB URLs)
│   │   ├── database.py            # SQLAlchemy engine and session
│   │   └── security.py            # API key validation (future)
│   ├── models/
│   │   ├── project.py             # SQLAlchemy ORM models
│   │   ├── variable.py
│   │   ├── document.py
│   │   ├── prompt.py
│   │   ├── processing_job.py
│   │   ├── extraction.py
│   │   └── processing_log.py
│   ├── schemas/
│   │   ├── project.py             # Pydantic schemas for API
│   │   ├── variable.py
│   │   ├── document.py
│   │   ├── processing.py
│   │   └── export.py
│   ├── services/
│   │   ├── prompt_generator.py    # LLM prompt generation logic
│   │   ├── llm_client.py          # LangChain + OpenAI integration
│   │   ├── document_processor.py  # Document parsing and chunking
│   │   ├── extraction_service.py  # Orchestrates LLM calls per variable
│   │   ├── job_manager.py         # Background job creation and tracking
│   │   └── export_service.py      # Dataset aggregation and file generation
│   ├── workers/
│   │   └── processing_worker.py   # Celery/Arq worker for background jobs
│   └── main.py                    # FastAPI app initialization
├── alembic/
│   ├── versions/                  # Database migration files
│   └── env.py
├── tests/
│   ├── api/                       # API endpoint tests
│   ├── services/                  # Service layer unit tests
│   ├── integration/               # End-to-end tests with test DB
│   └── conftest.py                # Pytest fixtures
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml         # PostgreSQL + Redis + API
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md

frontend/                          # Existing from 001-complete-user-workflow
├── src/
│   ├── app/                       # Next.js 16 app directory
│   ├── components/
│   ├── services/
│   │   └── api.ts                 # Service layer (will integrate with backend)
│   └── types/
└── package.json
```

**Structure Decision**: Web application structure (Option 2) with separate `backend/` and `frontend/` directories. Frontend already exists from feature 001-complete-user-workflow. Backend follows FastAPI best practices with clear separation of API routes, business logic (services), database models, and background workers.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Phase 2 work (backend) | Frontend (001) needs real data processing to be functional | Mock data cannot perform actual LLM extractions or process documents at scale |
| Background job queue (Redis + worker) | Document processing takes minutes/hours, cannot block API | Synchronous processing would timeout HTTP requests and prevent concurrent work |
| Database migrations (Alembic) | Schema evolution required for production | Manual SQL changes are error-prone and not reversible |
| LangChain dependency | Prompt orchestration, retry logic, LLM abstraction | Building custom LLM client would duplicate well-tested functionality |

**Justification for Technical Debt:**
- **Accepted**: No authentication in Phase 1 (add in Phase 2 after frontend integration validated)
- **Accepted**: Simple retry logic (3 attempts with exponential backoff, no circuit breaker yet)
- **Accepted**: In-memory job queue for MVP (migrate to Redis only when needed for scale/persistence)
- **Rejected**: Skipping database migrations (migrations are non-negotiable for production readiness)

---

## Plan Status

### Constitution Check Re-evaluation (Post Phase 1 Design)

**Re-check Status**: ✅ PASSED

All constitution principles remain satisfied after design phase:

1. **UI-First Design**: Backend supports frontend workflow, service layer contracts defined
2. **User Experience Excellence**: API returns structured errors and progress states for frontend
3. **Rapid Iteration**: Technical debt documented and justified, MVP scope clear
4. **User Workflow Fidelity**: Backend state transitions match 5-step workflow, no extra features

**No new violations introduced during design phase.**

---

### Phase Completion Summary

✅ **Phase 0 (Research)**: Complete
- All NEEDS CLARIFICATION items resolved
- Technology stack finalized (FastAPI, PostgreSQL, LangChain)
- Architecture patterns decided (async-first, service layer, structured output)
- Output: [research.md](research.md)

✅ **Phase 1 (Design & Contracts)**: Complete
- Entity relationship model defined with 8 tables
- Database schema with indexes and constraints documented
- OpenAPI 3.0 specification generated (31 endpoints)
- Pydantic schemas defined for all request/response types
- Output: [data-model.md](data-model.md), [contracts/openapi.yaml](contracts/openapi.yaml), [quickstart.md](quickstart.md)

✅ **Agent Context Update**: Complete
- CLAUDE.md updated with Python 3.11+, FastAPI, PostgreSQL, Redis
- Technology stack now available to AI agents for implementation

---

### Ready for Implementation

**Branch**: `002-backend-implementation`
**Artifacts**:
- ✅ Feature specification (spec.md)
- ✅ Implementation plan (plan.md) - this file
- ✅ Research findings (research.md)
- ✅ Data model (data-model.md)
- ✅ API contracts (contracts/openapi.yaml)
- ✅ Quickstart guide (quickstart.md)

**Next Command**: `/speckit.tasks` to generate tasks.md (Phase 2)

**Estimated Implementation**: 5 weeks (see quickstart.md for phase breakdown)

---

**Plan Complete**: 2025-11-26
