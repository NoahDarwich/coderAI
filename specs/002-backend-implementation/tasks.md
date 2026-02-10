# Tasks: Backend Implementation for Data Extraction Workflow

**Feature**: 002-backend-implementation
**Branch**: `002-backend-implementation`
**Created**: 2025-11-26
**Updated**: 2026-02-09 (Pipeline architecture alignment + Phases 1-4 Complete)
**Status**: In Progress - User Stories 1-2 Complete ✅

---

## Task Summary

- **Total Tasks**: 111 tasks
- **Completed**: 37 tasks (Phases 1-4) ✅
- **Remaining**: 74 tasks
- **MVP Scope**: All 5 user stories (US1-US5) - Complete backend implementation
- **Parallel Opportunities**: 62 tasks marked [P]
- **Estimated Duration**: 5 weeks (following quickstart.md phases)

---

## Pipeline Architecture Alignment

This implementation follows the pipeline architecture defined in [ai_agent_reference.md](/ai_agent_reference.md):

**Key Decisions:**
- **LLM Provider**: LangChain 0.3+ (multi-provider abstraction)
- **Document Formats**: All common (PDF, DOCX, CSV, JSON, Parquet, TXT)
- **Assistant Config**: Auto-generated from user-defined variables
- **Export**: CSV + Excel with filtering, confidence scores, and codebook
- **Deferred (v2)**: Duplicate detection, external API enrichment, advanced job queue

**Pipeline Stages per Document:**
1. Ingestion (multi-format parsing)
2. Extraction (identify records per unit of observation)
3. Enrichment (LLM call per variable via LangChain)
4. Post-Processing (validation, normalization)
5. Storage (atomic transaction per document)
6. Export (CSV + Excel with metadata)

---

## User Workflow Alignment

This backend implementation supports the complete 5-step user workflow from USER_WORKFLOW.md:

| Workflow Step | User Stories | Backend Responsibilities |
|---------------|--------------|-------------------------|
| **Step 1: Project Setup & Document Input** | US1 | Store project metadata, handle document uploads, validate inputs, support cloud connection metadata |
| **Step 2: Unit of Observation** | US1, US2 | Store unit of observation config (document-level vs entity-level), use in prompt generation |
| **Step 3: Schema Definition** | US1, US2 | Store variable definitions with extraction instructions, classification rules, edge case handling, generate LLM prompts |
| **Step 4: Schema Review & Confirmation** | US1, US2, US3 | Retrieve complete schema, support sample testing, accept user feedback on extractions, update prompts |
| **Step 5A: Sample Testing** | US3 | Process sample subset, return results with confidence scores, accept corrections, refine prompts |
| **Step 5B: Full Processing** | US4 | Batch process all documents, track progress, handle errors, continue despite failures |
| **Step 6: Results & Export** | US5 | Aggregate extractions, structure dataset (wide/long format), generate CSV/Excel/JSON |

---

## User Story Mapping

| Phase | User Story | Task Count | Dependencies | Status |
|-------|-----------|------------|--------------|--------|
| 1 | Setup | 7 | None (start here) | ✅ Complete |
| 2 | Foundational | 7 | Phase 1 complete | ✅ Complete |
| 3 | US1: Project & Schema Management | 12 | Phase 2 complete | ✅ Complete |
| 4 | US2: Prompt Generation & Configuration | 11 | US1 complete | ✅ Complete |
| 5 | US3: Sample Processing & Validation | 25 | US2 complete | 🔄 Ready to start |
| 6 | US4: Full Batch Processing | 12 | US3 complete | ⏳ Pending |
| 7 | US5: Data Export | 15 | US4 complete | ⏳ Pending |
| 8 | Polish & Cross-Cutting | 16 | All US complete | ⏳ Pending |

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic backend structure

**Dependencies**: None

- [x] T001 Create backend directory structure per plan.md (backend/src/{api/routes,core,models,schemas,services,workers}, backend/tests/, backend/alembic/, backend/docker/)
- [x] T002 [P] Initialize Python virtual environment and install core dependencies (FastAPI, SQLAlchemy, Pydantic, Alembic) in backend/requirements.txt
- [x] T003 [P] Create development requirements file with pytest, black, ruff in backend/requirements-dev.txt
- [x] T004 [P] Configure environment variables in backend/.env.example (DATABASE_URL, REDIS_URL, OPENAI_API_KEY, CORS origins)
- [x] T005 [P] Setup database connection configuration in backend/src/core/config.py using Pydantic Settings
- [x] T006 [P] Create SQLAlchemy async engine and session management in backend/src/core/database.py
- [x] T007 Initialize Alembic for database migrations in backend/alembic/ with env.py configured for async SQLAlchemy

**Validation**: Directory structure matches plan.md, dependencies installed, Alembic initialized ✅

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Dependencies**: Phase 1 complete

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create base SQLAlchemy model with common fields (id, created_at, updated_at) in backend/src/models/base.py
- [x] T009 [P] Setup FastAPI application with CORS middleware in backend/src/main.py
- [x] T010 [P] Create database dependency for FastAPI route injection in backend/src/api/dependencies.py
- [x] T011 [P] Configure structured error handling middleware (RFC 7807 format) in backend/src/api/middleware.py
- [x] T012 [P] Setup PostgreSQL enums (project_scale, project_status, variable_type, content_type, job_type, job_status, log_level) in backend/alembic/versions/001_create_enums.py
- [x] T013 [P] Create Pydantic base schemas with config for camelCase serialization in backend/src/schemas/base.py
- [x] T014 [P] Setup logging configuration with structured JSON logging in backend/src/core/logging.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 1 - Project & Schema Management (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Store project metadata and variable definitions with versioning support, including unit of observation configuration

**Workflow Steps**:
- Step 1: Project Setup & Document Input
- Step 2: Unit of Observation
- Step 3: Schema Definition

**Independent Test**: Create project via API with unit of observation config, add variables with extraction instructions and edge case handling, retrieve complete project state

**Dependencies**: Phase 2 complete

### Database Models for User Story 1

- [x] T015 [P] [US1] Create Project model in backend/src/models/project.py (id, name, scale, language, domain, unit_of_observation JSONB, status, timestamps)
- [x] T016 [P] [US1] Create Variable model in backend/src/models/variable.py (id, project_id FK, name, type, instructions, classification_rules JSONB, uncertainty_handling JSONB, edge_cases JSONB, order, timestamps)
- [x] T017 [US1] Generate Alembic migration for projects and variables tables in backend/alembic/versions/002_create_projects_variables.py

### Pydantic Schemas for User Story 1

- [x] T018 [P] [US1] Create ProjectCreate schema with unit_of_observation config (what_each_row_represents, rows_per_document, entity_identification_pattern) in backend/src/schemas/project.py
- [x] T019 [P] [US1] Create ProjectUpdate, ProjectResponse schemas in backend/src/schemas/project.py
- [x] T020 [P] [US1] Create VariableCreate schema with uncertainty_handling (confidence_threshold, if_uncertain_action, multiple_values_action) in backend/src/schemas/variable.py
- [x] T021 [P] [US1] Create VariableUpdate, VariableResponse schemas with edge_cases and validation_rules in backend/src/schemas/variable.py

### API Routes for User Story 1

- [x] T022 [US1] Implement project CRUD endpoints (POST /projects, GET /projects, GET /projects/{id}, PUT /projects/{id}, DELETE /projects/{id}) in backend/src/api/routes/projects.py
- [x] T023 [US1] Implement variable CRUD endpoints (GET /projects/{id}/variables, POST /projects/{id}/variables, GET /variables/{id}, PUT /variables/{id}, DELETE /variables/{id}) in backend/src/api/routes/variables.py

### Validation & Edge Cases for User Story 1

- [x] T024 [US1] Add input validation for project creation (name 1-255 chars, valid scale enum, unit_of_observation required) in project routes
- [x] T025 [US1] Add input validation for variable creation (name alphanumeric+underscore, instructions 10-5000 chars, type-specific validation) in variable routes
- [x] T026 [US1] Implement schema versioning logic (increment version on variable update) in variable update endpoint

**Acceptance Criteria**:
1. ✅ Frontend can create project with unit of observation config (document-level or entity-level)
2. ✅ Frontend can create variable with uncertainty handling (confidence threshold, multi-value strategy)
3. ✅ Frontend can define edge case handling (missing fields, validation rules)
4. ✅ Frontend can retrieve complete project with all variables and configuration

**Checkpoint**: Projects and variables fully manageable with workflow-aligned configuration ✅

---

## Phase 4: User Story 2 - Prompt Generation & Configuration (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Generate optimized LLM prompts from variable definitions incorporating project context, unit of observation, and user-provided instructions

**Workflow Step**: Step 3 (Schema Definition - background processing)

**Independent Test**: Create variable, verify prompt generated automatically with project context (document type, domain, unit of observation), model config, and extraction instructions

**Dependencies**: US1 complete (requires Variable and Project models)

### Database Models for User Story 2

- [x] T027 [US2] Create Prompt model in backend/src/models/prompt.py (id, variable_id FK, prompt_text, model_config JSONB, version, created_at)
- [x] T028 [US2] Generate Alembic migration for prompts table in backend/alembic/versions/003_create_prompts.py

### Service Layer for User Story 2

- [x] T029 [US2] Implement PromptGenerator service with generate_prompt method in backend/src/services/prompt_generator.py
- [x] T030 [US2] Incorporate project context into prompts (document_type, domain, language from Step 1) in PromptGenerator
- [x] T031 [US2] Incorporate unit of observation into prompts (what_each_row_represents, extraction_mode, entity_identification) in PromptGenerator
- [x] T032 [US2] Create prompt templates for different variable types (TEXT, NUMBER, DATE, CATEGORY, BOOLEAN) in PromptGenerator
- [x] T033 [US2] Include uncertainty handling instructions in prompts (confidence threshold, if_uncertain behavior, multi-value strategy) in PromptGenerator
- [x] T034 [US2] Add edge case handling to prompts (if missing, validation rules, dependencies) in PromptGenerator
- [x] T035 [US2] Implement model configuration selection (temperature, max_tokens based on variable type and precision) in PromptGenerator
- [x] T036 [US2] Add prompt versioning service methods (create new version, retrieve latest, retrieve specific version) in backend/src/services/prompt_service.py

### Integration with User Story 1

- [x] T037 [US2] Update variable creation endpoint to auto-generate prompt (version 1) when variable is created in backend/src/api/routes/variables.py

**Acceptance Criteria**:
1. ✅ Prompt includes project context: "You are extracting from [FILE_TYPE] in [DOMAIN] in [LANGUAGE]"
2. ✅ Prompt includes unit of observation: "Each row represents [UNIT]" with extraction mode instructions
3. ✅ Prompt includes variable-specific instructions from user
4. ✅ Prompt includes uncertainty handling strategy
5. ✅ Variable update creates new prompt version

**Checkpoint**: Prompts automatically generated with rich context from workflow steps 1-3 ✅

---

## Phase 5: User Story 3 - Sample Processing & Validation (Priority: P1) 🎯 MVP

**Goal**: Process sample subset of documents with LLM, return results with confidence scores, accept feedback, refine prompts based on user corrections

**Workflow Steps**:
- Step 4: Schema Review & Confirmation
- Step 5A: Sample Testing

**Independent Test**: Upload documents, create sample job for user-selected number of docs, verify extractions created with confidence scores, submit feedback on incorrect extractions, verify prompt updated based on patterns

**Dependencies**: US2 complete (requires prompt generation)

### Database Models for User Story 3

- [ ] T038 [P] [US3] Create Document model in backend/src/models/document.py (id, project_id FK, name, content, content_type, size_bytes, uploaded_at)
- [ ] T039 [P] [US3] Create ProcessingJob model in backend/src/models/processing_job.py (id, project_id FK, job_type, status, document_ids JSONB, progress, started_at, completed_at)
- [ ] T040 [P] [US3] Create Extraction model in backend/src/models/extraction.py (id, job_id FK, document_id FK, variable_id FK, value, confidence, source_text, created_at)
- [ ] T041 [P] [US3] Create ExtractionFeedback model in backend/src/models/extraction_feedback.py (id, extraction_id FK, is_correct, correct_value, user_comment, created_at)
- [ ] T042 [P] [US3] Create ProcessingLog model in backend/src/models/processing_log.py (id, job_id FK, document_id FK nullable, variable_id FK nullable, log_level, message, created_at)
- [ ] T043 [US3] Generate Alembic migration for processing tables in backend/alembic/versions/004_create_processing_tables.py

### Document Processing Services (Multi-Format Ingestion)

- [ ] T044 [P] [US3] Implement DocumentProcessor service for PDF text extraction using PyMuPDF in backend/src/services/document_processor.py
- [ ] T045 [P] [US3] Add DOCX text extraction support using python-docx in DocumentProcessor
- [ ] T046 [P] [US3] Add plain text file support in DocumentProcessor
- [ ] T044a [P] [US3] Add CSV bulk ingestion support (each row becomes a document, user maps text column) using pandas in DocumentProcessor
- [ ] T044b [P] [US3] Add JSON bulk ingestion support (configurable text field mapping) in DocumentProcessor
- [ ] T044c [P] [US3] Add Parquet bulk ingestion support using pyarrow + pandas in DocumentProcessor
- [ ] T047 [US3] Implement document chunking logic for large documents (>10 pages or >5000 words) in DocumentProcessor

### LLM Integration Services (LangChain Multi-Provider)

- [ ] T048 [US3] Setup LangChain LLM client with provider abstraction (OpenAI default, support Anthropic/local) and retry logic (max 3 retries, exponential backoff via tenacity) in backend/src/services/llm_client.py
- [ ] T049 [US3] Implement structured output parsing using LangChain JsonOutputParser with Pydantic schemas for LLM responses in llm_client
- [ ] T050 [US3] Create ExtractionService to orchestrate pipeline stages per document (extraction → enrichment → post-processing → storage) in backend/src/services/extraction_service.py
- [ ] T050a [US3] Implement auto-generated assistant config usage in ExtractionService (load Prompt + model_config per variable, call via LangChain)
- [ ] T051 [US3] Add confidence score extraction and validation (0.0-1.0 range) in ExtractionService
- [ ] T052 [US3] Add source text extraction (document excerpt that generated result) in ExtractionService
- [ ] T053 [US3] Add error handling for LLM failures (timeout, rate limit, malformed response) with logging in ExtractionService
- [ ] T053a [US3] Add post-processing step (date normalization, type coercion, validation against user-defined rules) in ExtractionService

### Job Management Services

- [ ] T054 [US3] Implement JobManager service for creating processing jobs in backend/src/services/job_manager.py
- [ ] T055 [US3] Add job progress tracking methods (update progress percentage, mark complete/failed) in JobManager
- [ ] T056 [US3] Implement sample processing worker logic (process user-selected subset of documents) in backend/src/workers/processing_worker.py
- [ ] T057 [US3] Add job cancellation support (update status to CANCELLED, stop processing) in JobManager

### API Routes for User Story 3

- [ ] T058 [P] [US3] Implement document upload endpoint (POST /projects/{id}/documents with multipart form data) in backend/src/api/routes/documents.py
- [ ] T059 [P] [US3] Implement document listing and retrieval endpoints (GET /projects/{id}/documents, GET /documents/{id}, DELETE /documents/{id}) in backend/src/api/routes/documents.py
- [ ] T060 [US3] Implement job creation endpoint (POST /projects/{id}/jobs with job_type=SAMPLE, document_count) in backend/src/api/routes/processing.py
- [ ] T061 [US3] Implement job status endpoint (GET /jobs/{id} with progress, status, current document, extraction statistics) in backend/src/api/routes/processing.py
- [ ] T062 [US3] Implement job results endpoint (GET /jobs/{id}/results returning extractions with confidence scores, filterable by confidence threshold) in backend/src/api/routes/processing.py

### Feedback Loop & Interactive Review (NEW from USER_WORKFLOW.md)

- [ ] T063 [US3] Implement extraction detail endpoint (GET /extractions/{id} with source text, AI reasoning, confidence) in backend/src/api/routes/processing.py
- [ ] T064 [US3] Implement feedback submission endpoint (POST /extractions/{id}/feedback with is_correct, correct_value, user_comment) in backend/src/api/routes/processing.py
- [ ] T065 [US3] Create FeedbackAnalyzer service to identify error patterns from user corrections in backend/src/services/feedback_analyzer.py
- [ ] T066 [US3] Implement prompt refinement logic based on feedback patterns in FeedbackAnalyzer
- [ ] T067 [US3] Add extraction statistics endpoint (GET /jobs/{id}/statistics with success_rate_per_variable, avg_confidence, common_errors) in backend/src/api/routes/processing.py

### Pydantic Schemas for User Story 3

- [ ] T068 [P] [US3] Create DocumentUpload, DocumentResponse schemas in backend/src/schemas/document.py
- [ ] T069 [P] [US3] Create JobCreate (with document_count for sample), JobResponse, JobStatus schemas in backend/src/schemas/processing.py
- [ ] T070 [P] [US3] Create ExtractionResponse (with source_text, reasoning), ExtractionDetail, FeedbackCreate schemas in backend/src/schemas/processing.py

### Background Processing Setup

- [ ] T071 [US3] Setup in-memory async queue for MVP (use asyncio.Queue for job processing) in backend/src/workers/queue_manager.py
- [ ] T072 [US3] Create background task runner to consume jobs from queue in backend/src/workers/task_runner.py

**Acceptance Criteria**:
1. ✅ User can select number of sample documents (e.g., 20 docs)
2. ✅ LLM called for each (document, variable) with enriched prompt
3. ✅ Extractions include value, confidence score (0-1), and source text
4. ✅ User can click extraction to see source text, AI reasoning, confidence
5. ✅ User can flag extraction as incorrect and provide correct value
6. ✅ Feedback analyzer identifies patterns and updates prompt
7. ✅ Re-running sample uses updated prompt version

**Checkpoint**: Sample testing with interactive review and feedback loop fully functional

---

## Phase 6: User Story 4 - Full Batch Processing (Priority: P1) 🎯 MVP

**Goal**: Process all documents asynchronously with real-time progress tracking, error resilience, and continuous quality monitoring

**Workflow Step**: Step 5B (Full Processing)

**Independent Test**: Create full processing job for all documents, verify async execution, track progress in real-time, verify error recovery, verify completion with all extractions

**Dependencies**: US3 complete (requires extraction service and sample validation)

### Full Processing Implementation

- [ ] T073 [US4] Add full batch processing support (job_type=FULL, document_ids=all) in JobManager service
- [ ] T074 [US4] Implement real-time progress updates (documents_completed/total, current_document, percentage, estimated_time_remaining) in processing worker
- [ ] T075 [US4] Add running statistics (success_rate, items_flagged_for_review, avg_processing_time_per_doc) in processing worker
- [ ] T076 [US4] Implement resilient error handling (log failures, continue processing, mark document as failed) in processing worker
- [ ] T077 [US4] Implement job status transitions (PENDING → PROCESSING → COMPLETE/FAILED) in processing worker

### Project Status Updates

- [ ] T078 [US4] Update project status to PROCESSING when full job starts in job creation endpoint
- [ ] T079 [US4] Update project status to COMPLETE when full job completes successfully in processing worker
- [ ] T080 [US4] Update project status to ERROR on job failure with error details in processing worker

### Progress Polling & Continuous Quality Monitoring (NEW from USER_WORKFLOW.md)

- [ ] T081 [P] [US4] Add progress polling endpoint (GET /jobs/{id}/progress with detailed stats) in backend/src/api/routes/processing.py
- [ ] T082 [P] [US4] Add processing logs retrieval endpoint (GET /jobs/{id}/logs with filtering by log_level, timestamps) in backend/src/api/routes/processing.py
- [ ] T083 [US4] Implement pause/resume functionality for long-running jobs in JobManager
- [ ] T084 [US4] Add flagged items retrieval (GET /jobs/{id}/flagged for low-confidence extractions) in backend/src/api/routes/processing.py

### Error Recovery

- [ ] T085 [US4] Implement retry logic for failed extractions (exponential backoff, max 3 retries) in ExtractionService
- [ ] T086 [US4] Add timeout handling for slow LLM calls (30 second timeout per call) in llm_client
- [ ] T087 [US4] Implement job resumption after server restart (mark in-progress jobs as PENDING on startup) in task_runner

**Acceptance Criteria**:
1. ✅ Full job created with status PROCESSING
2. ✅ Real-time progress updates (docs completed, percentage, estimated time remaining)
3. ✅ Running statistics (success rate, flagged items, avg time per doc)
4. ✅ User can pause and review flagged items during processing
5. ✅ Errors logged, processing continues with next document
6. ✅ Job status updates to COMPLETE when done
7. ✅ User can navigate away, processing continues in background

**Checkpoint**: Full processing works reliably with real-time monitoring and quality control

---

## Phase 7: User Story 5 - Data Aggregation & Export (Priority: P1) 🎯 MVP

**Goal**: Aggregate extractions into structured datasets and generate export files in multiple formats with rich metadata

**Workflow Step**: Step 6 (Results & Export)

**Independent Test**: Complete processing job, request export in CSV wide format with confidence scores and source text, verify file generation with correct structure and metadata

**Dependencies**: US4 complete (requires completed extractions)

### Export Service Implementation

- [ ] T088 [US5] Implement ExportService to aggregate extractions into pandas DataFrame in backend/src/services/export_service.py
- [ ] T089 [US5] Add wide format export (1 row per document, columns = variables) respecting unit of observation in ExportService
- [ ] T090 [US5] Add long format export (1 row per extraction with document_id, variable_name, value) in ExportService
- [ ] T091 [US5] Add optional confidence score columns in export formats in ExportService
- [ ] T092 [US5] Add optional source text columns in export formats in ExportService

### File Generation (CSV + Excel)

- [ ] T093 [P] [US5] Implement CSV export generation using pandas to_csv in ExportService
- [ ] T094 [P] [US5] Implement Excel export generation using pandas to_excel with openpyxl in ExportService

### Export Metadata & Quality Metrics (NEW from USER_WORKFLOW.md)

- [ ] T098 [US5] Add codebook generation (project metadata + variable definitions with all workflow context) to export package in ExportService
- [ ] T099 [US5] Include extraction statistics in export metadata (success rate per variable, average confidence, completion percentage) in ExportService
- [ ] T100 [US5] Add data summary section (row count, column count, processing date, quality metrics) in ExportService

### API Routes for User Story 5

- [ ] T101 [US5] Implement export endpoint (POST /projects/{id}/export with format, includeConfidence, includeSourceText options) in backend/src/api/routes/exports.py
- [ ] T102 [US5] Add export file download support (return file stream with correct content-type headers) in export endpoint

### Pydantic Schemas for User Story 5

- [ ] T103 [P] [US5] Create ExportRequest schema (format, include_confidence, include_source_text, min_confidence_threshold) in backend/src/schemas/export.py
- [ ] T104 [P] [US5] Create ExportResponse schema with download_url and metadata in backend/src/schemas/export.py

**Acceptance Criteria**:
1. ✅ Backend returns dataset with columns=variables, rows=unit_of_observation
2. ✅ CSV wide format has 1 row per unit (document or entity)
3. ✅ CSV long format has 1 row per extraction
4. ✅ Confidence scores included when requested
5. ✅ Source text included when requested
6. ✅ Export includes codebook with complete workflow context
7. ✅ Export includes quality metrics (completion %, confidence stats)
8. ✅ Multiple export formats supported (CSV, Excel, JSON, XML, PDF)

**Checkpoint**: Complete workflow functional - can export structured, high-quality datasets with rich metadata

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, logging, monitoring, deployment readiness

**Dependencies**: All user stories (US1-US5) complete

### Performance Optimization

- [ ] T105 [P] Add database indexes per data-model.md (projects.status, variables.project_order, extractions.doc_var, etc.) via Alembic migration in backend/alembic/versions/005_add_indexes.py
- [ ] T106 [P] Configure SQLAlchemy connection pooling (pool_size=20, max_overflow=10, pool_pre_ping=True) in backend/src/core/database.py
- [ ] T107 [P] Add LLM API rate limiting (max 10 calls per 60 seconds) in llm_client using RateLimiter

### Logging & Monitoring

- [ ] T108 [P] Add structured logging for all API endpoints (request ID, user context, duration) in middleware
- [ ] T109 [P] Configure Sentry error tracking for production monitoring in backend/src/core/config.py
- [ ] T110 [P] Add health check endpoint (GET /health with database connection test) in backend/src/api/routes/health.py

### Docker & Deployment

- [ ] T111 Create Dockerfile for backend service in backend/docker/Dockerfile
- [ ] T112 Create docker-compose.yml with PostgreSQL, Redis, API services in backend/docker/docker-compose.yml
- [ ] T113 [P] Add database migration runner to Docker entrypoint script in backend/docker/entrypoint.sh
- [ ] T114 [P] Create production environment configuration template in backend/.env.production

### Documentation

- [ ] T115 [P] Verify OpenAPI schema auto-generated by FastAPI matches contracts/openapi.yaml
- [ ] T116 [P] Create backend README.md with setup instructions, API overview, deployment guide in backend/README.md
- [ ] T117 [P] Run quickstart.md validation (verify all setup steps work on fresh environment)

### Code Quality

- [ ] T118 [P] Configure black formatter and ruff linter in backend/pyproject.toml
- [ ] T119 [P] Add pre-commit hooks for formatting and linting in backend/.pre-commit-config.yaml
- [ ] T120 Run full linting and formatting pass across entire backend codebase

**Validation**: Performance targets met (<200ms API response, <5min sample processing), monitoring configured, deployment ready

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
  ↓
Phase 2 (Foundational) ← BLOCKS all user stories
  ↓
Phase 3 (US1: Project & Schema)
  ↓
Phase 4 (US2: Prompt Generation) ← Uses US1 models
  ↓
Phase 5 (US3: Sample Processing) ← Uses US2 prompts
  ↓
Phase 6 (US4: Full Processing) ← Extends US3 extraction logic
  ↓
Phase 7 (US5: Export) ← Uses US4 extractions
  ↓
Phase 8 (Polish)
```

### Dependency Justification

- **US1 → US2**: Prompt generation requires Variable and Project models
- **US2 → US3**: Sample processing requires generated prompts with full context
- **US3 → US4**: Full processing reuses extraction service and feedback mechanisms
- **US4 → US5**: Export requires completed extractions from processing jobs

### Recommended Sequential Order (MVP Path)

All stories are P1 and tightly integrated. Recommended order:

1. **Phase 1 (Setup)** → Foundation structure
2. **Phase 2 (Foundational)** → Database, API framework, middleware
3. **Phase 3 (US1)** → Projects & Variables → **Checkpoint: Can manage schemas with workflow config**
4. **Phase 4 (US2)** → Prompt Generation → **Checkpoint: Prompts auto-generated with rich context**
5. **Phase 5 (US3)** → Sample Processing → **Checkpoint: Can test with feedback loop**
6. **Phase 6 (US4)** → Full Processing → **Checkpoint: Can process all documents with monitoring**
7. **Phase 7 (US5)** → Export → **Checkpoint: Complete workflow functional**
8. **Phase 8 (Polish)** → Performance, deployment, monitoring

### Parallel Opportunities

**Within Setup (Phase 1):**
- T002-T006 can run in parallel (different files)

**Within Foundational (Phase 2):**
- T009-T014 can run in parallel (different files)

**Within User Story 1:**
- T015-T016 (models) can run in parallel
- T018-T021 (schemas) can run in parallel

**Within User Story 2:**
- Schemas can run with services

**Within User Story 3:**
- T038-T042 (models) can run in parallel
- T044-T046 (document processors) can run in parallel
- T058-T059 (document routes) can run in parallel
- T068-T070 (schemas) can run in parallel

**Within User Story 5:**
- T093-T097 (file generators) can run in parallel
- T103-T104 (schemas) can run in parallel

**Within Polish (Phase 8):**
- T105-T107 (performance) can run in parallel
- T108-T110 (logging/monitoring) can run in parallel
- T113-T114 (deployment) can run in parallel
- T115-T117 (docs) can run in parallel
- T118-T119 (code quality) can run in parallel

---

## Implementation Strategy

### MVP First (All 5 Stories - Complete Workflow)

All user stories are P1 and form the complete data extraction pipeline. Each builds on the previous to enable the full workflow from USER_WORKFLOW.md.

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Project & Schema with workflow config)
4. Complete Phase 4: US2 (Prompt Generation with context enrichment)
5. Complete Phase 5: US3 (Sample Processing with feedback loop)
6. Complete Phase 6: US4 (Full Processing with quality monitoring)
7. Complete Phase 7: US5 (Export with rich metadata)
8. **VALIDATE END-TO-END**: Full workflow test
9. Complete Phase 8: Polish & Deploy

### Integration Checkpoints

- **After Phase 3**: Can create projects with unit of observation, define variables with edge cases
- **After Phase 4**: Variables auto-generate prompts with full workflow context
- **After Phase 5**: Can run sample processing, review results interactively, refine prompts
- **After Phase 6**: Can run full processing with real-time monitoring
- **After Phase 7**: Can export complete datasets with quality metrics
- **After Phase 8**: Production-ready deployment

---

## Task Summary

**Total Tasks**: 120 tasks

**Tasks per Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (User Story 1): 12 tasks
- Phase 4 (User Story 2): 11 tasks
- Phase 5 (User Story 3): 35 tasks
- Phase 6 (User Story 4): 15 tasks
- Phase 7 (User Story 5): 17 tasks
- Phase 8 (Polish): 16 tasks

**Parallel Opportunities**: 62 tasks marked with [P]

**Independent Test Criteria**:
- US1: Create project with unit of observation config, add variables with edge case handling
- US2: Verify prompt includes project context, unit of observation, uncertainty handling
- US3: Run sample with user-selected docs, review results interactively, submit feedback
- US4: Run full processing with real-time monitoring, pause/resume, error recovery
- US5: Export with confidence scores, source text, quality metrics, and codebook

**Estimated Implementation**: 5 weeks (per quickstart.md)
- Week 1: Phases 1-2 (Setup + Foundational)
- Week 2: Phases 3-4 (US1 + US2)
- Week 3: Phase 5 (US3 - Sample Processing with feedback)
- Week 4: Phase 6 (US4 - Full Processing with monitoring)
- Week 5: Phases 7-8 (US5 + Polish)

---

## Notes

- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story] Description with file path`
- [P] tasks = different files, no dependencies within phase
- [Story] label (US1-US5) maps task to user story for traceability
- Backend implements complete USER_WORKFLOW.md (Steps 1-6)
- Focus on workflow enrichment features: unit of observation, context enrichment, feedback loop, quality monitoring
- Backend integrates with existing frontend from 001-complete-user-workflow

---

**Tasks Ready for Execution** - Complete workflow support with USER_WORKFLOW.md alignment
