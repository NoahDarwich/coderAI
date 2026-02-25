# Tasks: Backend Implementation

**Feature**: 002-backend-implementation
**Created**: 2025-11-26
**Updated**: 2026-02-25
**Source of Truth**: [CODERAI_REFERENCE.md](/CODERAI_REFERENCE.md) Section 13

---

## Development Phases

This task list follows the 5-phase development roadmap from CODERAI_REFERENCE.md. Each phase builds on the previous.

```
Phase 1 (MVP) → Phase 2 (Core) → Phase 3 (AI Co-pilot) → Phase 4 (Scale) → Phase 5 (Advanced)
```

> **Note**: The backend uses `backend/src/` (not `backend/app/`). Task T001 (directory restructure) was intentionally skipped — the rename would affect 50+ files with no functional benefit. All references to `backend/app/` below should be read as `backend/src/`.

---

## Phase 1: Foundation (MVP) — Complete

**Goal**: Basic end-to-end extraction pipeline. Single-user, sequential processing, CSV export.

**Scope**: Project CRUD, document upload (PDF, TXT), variable definition, basic extraction, CSV export.

### 1A: Directory Restructure & Setup

- [x] T001 ~~Restructure `backend/src/` → `backend/app/`~~ — Skipped (kept `src/`, updated docs instead)
- [x] T002 ~~Update `alembic.ini` and `alembic/env.py`~~ — N/A, already uses `src/` paths
- [x] T003 Update `backend/src/main.py` entry point and all internal imports
- [x] T004 Add `backend/src/core/exceptions.py` with standard error handling
- [x] T005 Verify existing dependencies in `requirements.txt` match tech stack

### 1B: Data Model Updates

- [x] T006 Update Project model: description, unit_of_observation (JSONB), user_id FK, status ENUM
- [x] T007 Update Variable model: confidence_threshold, uncertainty_handling (JSONB), edge_cases (JSONB), validation_rules, depends_on, order
- [x] T008 Update Prompt model: prompt_text, model_config_ (JSONB), is_active, version
- [x] T009 Update Document model: word_count, chunk_count, error_message, status ENUM, file_size
- [x] T010 Update Extraction model: entity_index, entity_text, prompt_version, status ENUM, error_message
- [x] T011 Update ExtractionFeedback model: feedback_type ENUM, corrected_value, user_note
- [x] T012 Update ProcessingJob model: documents_processed, documents_failed, consecutive_failures, status ENUM
- [x] T013 Update ProcessingLog model: log_level ENUM, event_type ENUM, metadata_ JSONB
- [x] T014 Generate Alembic migration for model changes

### 1C: Schema Updates (Pydantic)

- [x] T015 Update project schemas for new fields
- [x] T016 Update variable schemas for new fields
- [x] T017 Update processing/extraction schemas (entity fields, status, feedback_type)
- [x] T018 Update document schemas (word_count, chunk_count, status, error_message)

### 1D: Project & Variable CRUD

- [x] T019 Update project routes to handle new fields
- [x] T020 Update variable routes with auto-trigger prompt generation on create/update
- [x] T021 Update prompt_generator.py for new Prompt fields
- [x] T022 Set temperature per variable type (BOOLEAN=0.1, CATEGORY=0.1, DATE=0.15, NUMBER=0.15, TEXT=0.2)

### 1E: Document Ingestion

- [x] T023 Update document_processor.py to calculate word_count and set status transitions
- [x] T024 Set error_message on parse failure and status to FAILED
- [x] T025 Verify PDF extraction (PyMuPDF) and TXT support

### 1F: Basic Extraction Pipeline (Sequential)

- [x] T026 ~~Refactor extraction_service.py to use LangChain exclusively~~ — Uses OpenAI SDK directly with circuit breaker; agents use LangChain
- [x] T027 Implement pipeline: load document → load active prompt → call LLM → parse response → post-process → store
- [x] T028 Add post-processing step: type coercion, validation, default_value, confidence check, multi-value handling
- [x] T029 Store extractions atomically per document (savepoints)
- [x] T030 Implement job_manager for SAMPLE and FULL ProcessingJob records
- [x] T031 Track documents_processed, documents_failed, progress percentage on job
- [x] T032 Log events to ProcessingLog (all event types)

### 1G: Error Handling

- [x] T033 Add retry logic for LLM calls (exponential backoff, max retries)
- [x] T034 Handle LLM response parsing errors (mark extraction as FAILED, log, continue)
- [x] T035 Increment consecutive_failures on document failure, continue to next
- [x] T036 Mark Extraction status appropriately (EXTRACTED, FLAGGED, FAILED)

### 1H: Feedback

- [x] T037 Implement feedback endpoint (POST /extractions/{id}/feedback) with feedback_type, corrected_value, user_note
- [x] T038 Store ExtractionFeedback records linked to extractions

### 1I: CSV Export

- [x] T039 Update export_service.py for wide format
- [x] T040 Support long format export
- [x] T041 Include optional metadata columns (_confidence, _source, _prompt_version per variable)

### 1J: API Route Cleanup

- [x] T042 Consistent error responses across all routes
- [x] T043 Job status endpoint (GET /jobs/{id}) with progress
- [x] T044 Extraction listing endpoint (GET /projects/{id}/extractions) with pagination and filtering

**Phase 1 Checkpoint**: Can create project → upload documents → define variables → run extraction → export CSV. ✅

---

## Phase 2: Core Features — Complete

**Goal**: Multi-tenancy, entity-level extraction, sample-first workflow, ARQ job queue, WebSocket, Excel export.

### 2A: Authentication & Multi-tenancy

- [x] T045 Create User model with id, email, hashed_password, is_active, timestamps
- [x] T046 Implement JWT auth: login, register, access token (15 min), refresh token (7 days)
- [x] T047 Add `backend/src/core/security.py` with password hashing (bcrypt), token creation/verification
- [x] T048 Create auth dependency in `dependencies.py` (extract user from JWT, inject into routes)
- [x] T049 Add user_id FK to Project model (non-nullable)
- [x] T050 Implement Row-Level Security: enable RLS on all tenant-scoped tables
- [x] T051 Set `app.current_user_id` at request start via dependency (set_rls_context)
- [x] T052 Create `backend/src/core/rls.py` with RLS policy definitions

### 2B: Entity-Level Extraction

- [x] T053 Implement entity identification: identify_entities() in text_extraction_service.py
- [x] T054 For ENTITY projects: run entity identification first, then extract per entity x variable
- [x] T055 Store entity_index and entity_text on Extraction records
- [x] T056 Update export to handle entity-level rows (entity columns in output)

### 2C: Sample → Feedback → Full Run Workflow

- [x] T057 Workflow enforcement via project status transitions
- [x] T058 Allow user to select sample document IDs for SAMPLE job
- [x] T059 Implement feedback_analyzer.py: analyze feedback patterns
- [x] T060 Implement prompt refinement: generate improved prompt, save as new version
- [x] T061 Support re-running sample with updated prompts

### 2D: ARQ + Redis Job Queue

- [x] T062 Setup Redis connection in config
- [x] T063 Create `backend/src/workers/settings.py` with ARQ WorkerSettings
- [x] T064 Create extraction_worker.py, refinement_worker.py, export_worker.py
- [x] T065 Replace BackgroundTasks with ARQ job enqueueing
- [x] T066 Implement job resumability (skip already-processed documents)
- [x] T067 Implement pause/resume endpoints (POST /jobs/{id}/pause, /resume)
- [x] T068 Auto-pause job when consecutive_failures > 10

### 2E: WebSocket Real-time Updates

- [x] T069 Add WebSocket endpoint `/ws/jobs/{job_id}`
- [x] T070 Emit events: progress, document_completed, document_failed, job_completed, job_failed
- [x] T071 Authenticate WebSocket connections via JWT token parameter

### 2F: Excel Export with Codebook

- [x] T072 Implement Excel (.xlsx) export with formatting via openpyxl
- [x] T073 Generate codebook: variable definitions, classification rules, quality metrics
- [x] T074 Include codebook as separate sheet in Excel export + standalone codebook endpoint

**Phase 2 Checkpoint**: Multi-tenant, entity-level extraction, sample-first workflow, ARQ background processing, WebSocket progress, Excel + codebook export. ✅

---

## Phase 3: AI Co-pilot — Complete

**Goal**: AI-assisted variable definition, prompt refinement from feedback, guided setup.

### 3A: Co-pilot Agent

- [x] T075 Create `backend/src/agents/copilot.py` with LangChain-based co-pilot agent
- [x] T076 Implement variable suggestion: given domain + sample texts, suggest relevant variables
- [x] T077 Implement instruction refinement via co-pilot chat
- [x] T078 Implement category suggestion via co-pilot chat
- [x] T079 Add co-pilot API endpoints: POST /projects/{id}/copilot/message, POST /copilot/suggest-variables
- [x] T080 Store conversation history in Redis (24h TTL, max 20 turns)

### 3B: Refinement Agent

- [x] T081 Create `backend/src/agents/refiner.py` with LLM-based prompt refinement
- [x] T082 Analyze feedback patterns: extracted vs expected, user notes, cross-extraction patterns
- [x] T083 Generate 2-3 prompt improvement options (PromptAlternative) for user selection
- [x] T084 Queue refinement_job via ARQ when sufficient feedback collected (>= 3 items)

### 3C: Guided Setup Wizard Support

- [x] T085 Add API endpoints to support wizard flow (project context questions, UoO recommendations)
- [x] T086 Smart defaults: suggest unit_of_observation based on document type

**Phase 3 Checkpoint**: Co-pilot suggests variables, refines prompts from feedback, assists with project setup. ✅

---

## Phase 4: Scale & Polish — Complete

**Goal**: Handle large documents, parallel processing, observability, additional formats.

### 4A: Document Chunking

- [x] T087 Create DocumentChunk model with id, document_id, chunk_index, text, token_count, overlap_previous
- [x] T088 Implement chunking: split documents > 5000 words via create_chunks_for_document()
- [x] T089 ~~Use LangChain RecursiveCharacterTextSplitter~~ — Uses custom word-count-based chunking in document_processor.py
- [x] T090 For chunked documents: process all chunks, merge results by best confidence

### 4B: Parallel Processing

- [x] T091 Configure ARQ WorkerSettings (max_jobs, timeouts)
- [x] T092 Implement concurrent variable extraction within a document (asyncio.gather with semaphore, max_concurrency=5)

### 4C: Observability

- [x] T093 Add Prometheus metrics: documents_processed_total, extractions_total, llm_calls_total, llm_call_duration_seconds, extraction_confidence histogram, jobs_total, document_processing_duration_seconds
- [x] T094 Add OpenTelemetry tracing (tracing.py, spans on LLM calls in copilot + extraction service)
- [x] T095 Structured logging with job_id, document_id in processing logs

### 4D: Rate Limiting & Cost Controls

- [x] T096 Redis token-bucket rate limiter per project (backend/src/core/rate_limiter.py)
- [x] T097 LLM call rate limiting: configurable requests per window
- [x] T098 RateLimitExceeded exception with remaining/retry info

### 4E: Additional Format Support

- [x] T099 DOCX support in document_processor.py using python-docx
- [x] T100 HTML support in document_processor.py using BeautifulSoup

### 4F: Health Checks & Deployment

- [x] T101 Health endpoints: /health/live (liveness), /health/ready (DB + Redis check)
- [x] T102 Dockerfile and docker-compose.yml (API + Worker + PostgreSQL + Redis)
- [x] T103 Graceful shutdown (shutdown_requested flag in worker ctx, checkpoint at document boundary)

### 4G: Circuit Breaker

- [x] T104 Circuit breaker for LLM calls: open after 5 failures, half-open after 30s, close after 3 successes
- [x] T105 Fail fast with error message when circuit is open

**Phase 4 Checkpoint**: Large document chunking, parallel extraction, Prometheus + OTEL observability, rate limiting, DOCX/HTML support, Docker deployment, circuit breaker, graceful shutdown. ✅

---

## Phase 5: Advanced (v2) — Not started

**Goal**: Duplicate detection, external API enrichment, multi-model, team collaboration.

- [ ] T106 Duplicate detection: identify similar documents before processing
- [ ] T107 External API enrichment: geocoding, entity resolution, etc.
- [ ] T108 Multi-model support: configure different LLM models per variable or project
- [ ] T109 Team collaboration: shared projects, role-based access control

**Phase 5 Checkpoint**: Advanced features for enterprise use cases.

---

## Task Summary

| Phase | Description | Task Count | Status |
|-------|-------------|------------|--------|
| 1 | Foundation (MVP) | 44 tasks (T001-T044) | **Complete** |
| 2 | Core Features | 30 tasks (T045-T074) | **Complete** |
| 3 | AI Co-pilot | 12 tasks (T075-T086) | **Complete** |
| 4 | Scale & Polish | 19 tasks (T087-T105) | **Complete** |
| 5 | Advanced (v2) | 4 tasks (T106-T109) | Not started |
| **Total** | | **109 tasks** | **105 complete, 4 pending (Phase 5)** |
