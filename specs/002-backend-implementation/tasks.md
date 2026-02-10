# Tasks: Backend Implementation

**Feature**: 002-backend-implementation
**Created**: 2025-11-26
**Updated**: 2026-02-10
**Source of Truth**: [CODERAI_REFERENCE.md](/CODERAI_REFERENCE.md) Section 13

---

## Development Phases

This task list follows the 5-phase development roadmap from CODERAI_REFERENCE.md. Each phase builds on the previous.

```
Phase 1 (MVP) → Phase 2 (Core) → Phase 3 (AI Co-pilot) → Phase 4 (Scale) → Phase 5 (Advanced)
```

---

## Phase 1: Foundation (MVP)

**Goal**: Basic end-to-end extraction pipeline. Single-user, sequential processing, CSV export.

**Scope**: Project CRUD, document upload (PDF, TXT), variable definition, basic extraction, CSV export.

### 1A: Directory Restructure & Setup

- [ ] T001 Restructure `backend/src/` → `backend/app/` to match CODERAI_REFERENCE.md Section 2.3
- [ ] T002 Update `alembic.ini` and `alembic/env.py` for new `backend/app/` import paths
- [ ] T003 Update `backend/app/main.py` entry point and all internal imports
- [ ] T004 Add `backend/app/core/exceptions.py` with standard error handling (RFC 7807)
- [ ] T005 Verify existing dependencies in `requirements.txt` match CODERAI_REFERENCE.md tech stack

### 1B: Data Model Updates

- [ ] T006 Update Project model: add `description`, change `unit_of_observation` to ENUM (DOCUMENT, ENTITY), add `entity_identification_pattern`, add `user_id` FK (nullable for Phase 1), update `status` ENUM to match (CREATED, SCHEMA_DEFINED, SAMPLE_COMPLETE, PROCESSING, COMPLETE)
- [ ] T007 Update Variable model: add `display_name`, `confidence_threshold` (float, default 0.7), `if_uncertain` ENUM (NULL, SKIP, FLAG), `if_multiple_values` ENUM (FIRST, LAST, ALL, SUMMARIZE), `max_values` (int), `default_value`, `validation_rules` (JSONB), `depends_on` (JSONB). Remove old `uncertainty_handling`/`edge_cases` JSONB fields
- [ ] T008 Update Prompt model: rename `prompt_text` → `system_prompt`, replace `model_config` JSONB with separate `model`, `temperature`, `max_tokens` columns, add `response_schema` (JSONB), add `is_active` (bool)
- [ ] T009 Update Document model: add `word_count` (int), `chunk_count` (int, default 0), `error_message` (text), update `status` ENUM (UPLOADED, PARSED, READY, FAILED)
- [ ] T010 Update Extraction model: change `value` to JSONB, add `entity_index` (int, nullable), `entity_text` (text, nullable), `prompt_version` (int), add `status` ENUM (EXTRACTED, VALIDATED, FLAGGED, FAILED), add `error_message`
- [ ] T011 Update ExtractionFeedback model: replace `is_correct` bool with `feedback_type` ENUM (CORRECT, INCORRECT, PARTIALLY_CORRECT), rename `correct_value` → `corrected_value` (JSONB), rename `user_comment` → `user_note`
- [ ] T012 Update ProcessingJob model: add `documents_processed` (int), `documents_failed` (int), `consecutive_failures` (int), update `status` ENUM (PENDING, RUNNING, PAUSED, COMPLETED, FAILED)
- [ ] T013 Update ProcessingLog model: replace `log_level` with `event_type` ENUM (JOB_STARTED, DOC_STARTED, DOC_COMPLETED, DOC_FAILED, JOB_COMPLETED, JOB_FAILED, JOB_PAUSED, JOB_RESUMED), add `metadata` (JSONB), remove `variable_id` FK
- [ ] T014 Generate Alembic migration for all model changes

### 1C: Schema Updates (Pydantic)

- [ ] T015 Update project schemas to match new Project model fields (unit_of_observation as enum, entity_identification_pattern, description)
- [ ] T016 Update variable schemas to match new Variable model fields (all 8 new fields)
- [ ] T017 Update processing/extraction schemas (JSONB value, entity_index, entity_text, prompt_version, status, feedback_type)
- [ ] T018 Update document schemas (word_count, chunk_count, status enum, error_message)

### 1D: Project & Variable CRUD

- [ ] T019 Update project routes to handle new fields (description, unit_of_observation enum, entity_identification_pattern)
- [ ] T020 Update variable routes to handle expanded fields and auto-trigger prompt generation on create/update
- [ ] T021 Update prompt_generator.py to output new Prompt fields (system_prompt, model, temperature, max_tokens, response_schema, is_active)
- [ ] T022 Set temperature per variable type: BOOLEAN=0.1, CATEGORY=0.1, DATE=0.15, NUMBER=0.15, TEXT=0.2

### 1E: Document Ingestion

- [ ] T023 Update document_processor.py to calculate `word_count` and set proper `status` transitions (UPLOADED → PARSED → READY)
- [ ] T024 Set `error_message` on parse failure and status to FAILED
- [ ] T025 Verify PDF extraction (PyMuPDF) and TXT support work with updated model

### 1F: Basic Extraction Pipeline (Sequential)

- [ ] T026 Refactor extraction_service.py to use LangChain exclusively (remove any direct OpenAI SDK usage)
- [ ] T027 Implement pipeline: load document → load active prompt per variable → call LLM via LangChain → parse response → post-process → store
- [ ] T028 Add post-processing step: type coercion, validation against `validation_rules`, apply `default_value`, confidence check against `confidence_threshold`, multi-value handling via `if_multiple_values`
- [ ] T029 Store extractions atomically per document (all variables in single transaction)
- [ ] T030 Implement job_manager to create SAMPLE and FULL ProcessingJob records and process sequentially (BackgroundTasks for Phase 1)
- [ ] T031 Track `documents_processed`, `documents_failed`, `progress` percentage on job
- [ ] T032 Log events to ProcessingLog (JOB_STARTED, DOC_STARTED, DOC_COMPLETED, DOC_FAILED, JOB_COMPLETED, JOB_FAILED)

### 1G: Error Handling

- [ ] T033 Add retry logic for LLM calls (exponential backoff via tenacity: 1s, 2s, 4s, 8s, 16s, max 5 retries)
- [ ] T034 Handle LLM response parsing errors (mark extraction as FAILED, log, continue)
- [ ] T035 Increment `consecutive_failures` on document failure, continue to next document
- [ ] T036 Mark Extraction status appropriately (EXTRACTED on success, FAILED on error)

### 1H: Feedback

- [ ] T037 Implement feedback endpoint (POST /extractions/{id}/feedback) with feedback_type, corrected_value, user_note
- [ ] T038 Store ExtractionFeedback records linked to extractions

### 1I: CSV Export

- [ ] T039 Update export_service.py for wide format with new model fields (JSONB values, multi-value columns using max_values)
- [ ] T040 Support long format export
- [ ] T041 Include optional metadata columns (_confidence, _source, _prompt_version per variable)

### 1J: API Route Cleanup

- [ ] T042 Ensure all routes return consistent error responses (RFC 7807)
- [ ] T043 Add job status endpoint (GET /jobs/{id}) with progress, documents_processed, documents_failed
- [ ] T044 Add extraction listing endpoint (GET /projects/{id}/extractions) with pagination and filtering

**Phase 1 Checkpoint**: Can create project → upload documents → define variables → run extraction → export CSV. Single-user, sequential.

---

## Phase 2: Core Features

**Goal**: Multi-tenancy, entity-level extraction, sample-first workflow, ARQ job queue, WebSocket, Excel export.

**Dependencies**: Phase 1 complete.

### 2A: Authentication & Multi-tenancy

- [ ] T045 Create User model with id, email, hashed_password, created_at, updated_at
- [ ] T046 Implement JWT auth: login endpoint, access token (15 min), refresh token (7 days)
- [ ] T047 Add `backend/app/core/security.py` with password hashing (bcrypt), token creation/verification
- [ ] T048 Create auth dependency in `deps.py` (extract user from JWT, inject into routes)
- [ ] T049 Add `user_id` FK to Project model (make non-nullable), generate migration
- [ ] T050 Implement Row-Level Security: enable RLS on projects and cascading tables
- [ ] T051 Set `app.current_user_id` at request start via SQLAlchemy event listener
- [ ] T052 Create `backend/app/db/rls.py` with RLS policy setup

### 2B: Entity-Level Extraction

- [ ] T053 Implement entity identification assistant: given document text and `entity_identification_pattern`, identify distinct entities
- [ ] T054 For ENTITY projects: run entity identification first, then extract per entity × variable
- [ ] T055 Store `entity_index` and `entity_text` on Extraction records
- [ ] T056 Update export wide format to handle entity-level rows (one row per entity, not per document)

### 2C: Sample → Feedback → Full Run Workflow

- [ ] T057 Enforce workflow: CREATED → (define variables) → SCHEMA_DEFINED → (sample run) → SAMPLE_COMPLETE → (full run) → PROCESSING → COMPLETE
- [ ] T058 Allow user to select sample document IDs for SAMPLE job
- [ ] T059 Implement feedback_analyzer.py: analyze feedback patterns across extractions for a variable
- [ ] T060 Implement prompt refinement: generate improved prompt from feedback, save as new version with is_active=true, deactivate previous
- [ ] T061 Support re-running sample with updated prompts

### 2D: ARQ + Redis Job Queue

- [ ] T062 Setup Redis connection in config
- [ ] T063 Create `backend/app/workers/worker_settings.py` with ARQ WorkerSettings
- [ ] T064 Create `backend/app/workers/tasks.py` with extraction_job, prompt_refinement_job, export_job
- [ ] T065 Replace BackgroundTasks usage with ARQ job enqueueing
- [ ] T066 Implement job resumability (skip already-processed documents on resume)
- [ ] T067 Implement pause/resume endpoints (POST /jobs/{id}/pause, POST /jobs/{id}/resume)
- [ ] T068 Auto-pause job when `consecutive_failures` > 10

### 2E: WebSocket Real-time Updates

- [ ] T069 Add WebSocket endpoint `/ws/jobs/{job_id}` in main.py
- [ ] T070 Emit events during processing: progress, document_completed, document_failed, job_completed, job_failed
- [ ] T071 Authenticate WebSocket connections via JWT token parameter

### 2F: Excel Export with Codebook

- [ ] T072 Implement Excel (.xlsx) export with formatting via openpyxl
- [ ] T073 Generate codebook: variable definitions, classification rules, quality metrics (avg confidence, % flagged, % null)
- [ ] T074 Include codebook as separate sheet in Excel export or separate file

**Phase 2 Checkpoint**: Multi-tenant, entity-level extraction, sample-first workflow, ARQ background processing, WebSocket progress, Excel + codebook export.

---

## Phase 3: AI Co-pilot

**Goal**: AI-assisted variable definition, prompt refinement from feedback, guided setup.

**Dependencies**: Phase 2 complete.

### 3A: Co-pilot Agent

- [ ] T075 Create `backend/app/agents/copilot.py` with LangChain-based co-pilot agent
- [ ] T076 Implement variable suggestion: given document type + domain, suggest relevant variables
- [ ] T077 Implement instruction refinement: improve user-written extraction instructions
- [ ] T078 Implement category suggestion: for CATEGORY variables, propose categories from sample content
- [ ] T079 Add co-pilot API endpoints: POST /projects/{id}/copilot/message, POST /copilot/suggest-variables
- [ ] T080 Store conversation history in session (Redis or DB) for stateful co-pilot interactions

### 3B: Refinement Agent

- [ ] T081 Create `backend/app/agents/refiner.py` with prompt refinement agent
- [ ] T082 Analyze feedback patterns: what was extracted vs expected, user notes, cross-extraction patterns
- [ ] T083 Generate 2-3 prompt improvement options for user selection
- [ ] T084 Queue prompt_refinement_job via ARQ when sufficient feedback collected

### 3C: Guided Setup Wizard Support

- [ ] T085 Add API endpoints to support wizard flow (project context questions, unit of observation recommendations)
- [ ] T086 Smart defaults: suggest unit_of_observation based on document type

**Phase 3 Checkpoint**: Co-pilot suggests variables, refines prompts from feedback, assists with project setup.

---

## Phase 4: Scale & Polish

**Goal**: Handle large documents, parallel processing, observability, additional formats.

**Dependencies**: Phase 3 complete.

### 4A: Document Chunking

- [ ] T087 Create DocumentChunk model with id, document_id FK, chunk_index, text, token_count, overlap_previous
- [ ] T088 Implement semantic chunking: respect paragraph/section boundaries, 2000-3000 tokens, 200-300 token overlap
- [ ] T089 Use LangChain RecursiveCharacterTextSplitter or custom semantic splitter
- [ ] T090 For chunked documents: process all chunks, merge/deduplicate extraction results

### 4B: Parallel Processing

- [ ] T091 Scale ARQ workers: configure max_jobs per worker, multiple worker instances
- [ ] T092 Implement concurrent document processing within a job (process N documents in parallel)

### 4C: Observability

- [ ] T093 Add Prometheus metrics: documents_processed_total, extractions_total, llm_calls_total, llm_call_duration_seconds, llm_tokens_used_total, job_queue_depth, extraction_confidence histogram
- [ ] T094 Add OpenTelemetry tracing: request → service → LLM call → database chain
- [ ] T095 Structured JSON logging with correlation_id, job_id, document_id, variable_id, user_id, duration_ms

### 4D: Rate Limiting & Cost Controls

- [ ] T096 Per-project token budget: track tokens used, pause job if budget exceeded
- [ ] T097 LLM call rate limiting: max N requests/minute (configurable)
- [ ] T098 Queue throttling: reject new jobs with 429 if queue depth > threshold

### 4E: Additional Format Support

- [ ] T099 Add DOCX support in document_processor.py using python-docx
- [ ] T100 Add HTML support in document_processor.py using BeautifulSoup

### 4F: Health Checks & Deployment

- [ ] T101 Add health endpoints: `/health/live` (process running), `/health/ready` (DB + Redis + LLM reachable)
- [ ] T102 Create Dockerfile and docker-compose.yml (API + Worker + PostgreSQL + Redis)
- [ ] T103 Implement graceful shutdown: stop accepting jobs, wait for in-progress extractions, checkpoint progress

### 4G: Circuit Breaker

- [ ] T104 Implement circuit breaker for LLM calls: open after 5 consecutive failures, half-open after 30s, close after 3 successes
- [ ] T105 Fail fast with user-friendly error when circuit is open

**Phase 4 Checkpoint**: Handles large documents, parallel processing, full observability, rate limiting, DOCX/HTML support, production-ready deployment.

---

## Phase 5: Advanced (v2)

**Goal**: Duplicate detection, external API enrichment, multi-model, team collaboration.

**Dependencies**: Phase 4 complete.

- [ ] T106 Duplicate detection: identify similar documents before processing
- [ ] T107 External API enrichment: geocoding, entity resolution, etc.
- [ ] T108 Multi-model support: configure different LLM models per variable or project
- [ ] T109 Team collaboration: shared projects, role-based access control

**Phase 5 Checkpoint**: Advanced features for enterprise use cases.

---

## Task Summary

| Phase | Description | Task Count | Status |
|-------|-------------|------------|--------|
| 1 | Foundation (MVP) | 44 tasks (T001-T044) | Partially implemented |
| 2 | Core Features | 30 tasks (T045-T074) | Not started |
| 3 | AI Co-pilot | 12 tasks (T075-T086) | Not started |
| 4 | Scale & Polish | 19 tasks (T087-T105) | Not started |
| 5 | Advanced (v2) | 4 tasks (T106-T109) | Not started |
| **Total** | | **109 tasks** | |

### Existing Code Status

The following code exists under `backend/src/` and partially covers Phase 1 tasks:
- Models: 9 SQLAlchemy models (need field updates per T006-T013)
- Schemas: 7 Pydantic modules (need updates per T015-T018)
- Routes: 5 route modules (need updates per T019-T020, T042-T044)
- Services: 7 services (need refactoring per T026-T032)
- Workers: Empty `__init__.py` (T062-T068 for ARQ)
- Agents: Does not exist (T075-T084 for agents)

See [IMPLEMENTATION_STATUS.md](/backend/IMPLEMENTATION_STATUS.md) for detailed gap analysis.
