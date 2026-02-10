# Feature Specification: Backend Implementation for Data Extraction Workflow

**Feature Branch**: `002-backend-implementation`
**Created**: 2025-11-26
**Updated**: 2026-02-10
**Status**: In Progress
**Source of Truth**: [CODERAI_REFERENCE.md](/CODERAI_REFERENCE.md)

## User Workflow Context

**Primary Workflow Step(s):** All steps 1-6 (backend services supporting complete workflow)

**Workflow Alignment:** This feature implements the backend services that power the 6-step user workflow defined in USER_WORKFLOW.md. While the frontend handles user interaction (001-complete-user-workflow), the backend processes data, manages state, orchestrates LLM calls, and delivers structured datasets.

## Overview

CoderAI is a **multi-tenant SaaS platform** that transforms unstructured documents into structured datasets using LLM-powered extraction. The backend implements a user-configurable corpus processing pipeline where each project defines its own domain, extraction targets, and variables through the frontend UI. The system auto-generates LLM assistant configurations from these definitions, ingests documents, processes them through LangChain-powered extraction stages, and delivers structured results.

**Architecture Reference:** See [CODERAI_REFERENCE.md](/CODERAI_REFERENCE.md) for complete architecture, data model, pipeline stages, API design, and deployment specifications.

**Core Responsibilities:**
- Store and manage project metadata, schemas, and processing state with multi-tenant isolation
- **Auto-generate** LLM assistant configurations from user-defined variables (prompts, model configs, response schemas)
- **Ingest documents** in supported formats (PDF, DOCX, TXT, HTML)
- Orchestrate the extraction pipeline: Ingestion → Extraction → Post-Processing → Storage → Export
- Process documents through **LangChain** for multi-provider LLM abstraction
- Manage sample testing workflow with feedback-driven prompt refinement
- Aggregate and structure extraction results for CSV + Excel export with quality metrics
- Handle asynchronous processing with **ARQ + Redis** background jobs
- Provide real-time progress updates via **WebSocket**
- Enforce **Row-Level Security** for multi-tenant data isolation

**Architecture Decisions (from CODERAI_REFERENCE.md Section 2.2):**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| API Framework | FastAPI (async) | Native async, automatic OpenAPI docs, Pydantic validation |
| Database | PostgreSQL 16+ with RLS | JSONB for flexible schemas, RLS for multi-tenancy |
| ORM | SQLAlchemy 2.0 async | Industry standard, Alembic migrations |
| Job Queue | ARQ + Redis 7+ | Async-native, lightweight, Redis-backed |
| LLM Framework | LangChain 0.3+ | Multi-provider abstraction, structured output parsing |
| Real-time | WebSocket or SSE | Job progress without polling |
| Auth | JWT (access + refresh tokens) | Stateless, standard |
| Multi-tenancy | Row-Level Security | Database-enforced isolation |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Project & Schema Management (Priority: P1) — Phase 1 MVP

A researcher creates a project and defines extraction variables. The backend must store this configuration with multi-tenant isolation and make it available for processing.

**Why this priority**: Without persistent storage of project metadata and schemas, users cannot save work or process documents later. This is foundational for all other backend features.

**Workflow Step:** Steps 1-3 (Project Setup, Unit of Observation, Schema Definition)

**Independent Test**: Backend can receive project creation request with metadata, store project, accept variable definitions with all expanded fields, store schema with versioning, and retrieve project state.

**Acceptance Scenarios**:

1. **Given** frontend sends project creation request, **When** backend receives project name, domain, language, and unit_of_observation, **Then** backend creates project with unique ID and returns project object
2. **Given** user defines variable with name/type/instructions and expanded fields (confidence_threshold, if_uncertain, if_multiple_values, validation_rules), **When** frontend sends variable definition, **Then** backend stores variable and associates with project
3. **Given** user edits variable, **When** frontend sends updated definition, **Then** backend updates variable and a new prompt version is generated
4. **Given** frontend requests project details, **When** backend receives project ID, **Then** backend returns complete project with all variables and configuration
5. **Given** project has unit_of_observation=ENTITY, **When** user creates project, **Then** entity_identification_pattern is stored and used in extraction

---

### User Story 2 - Prompt Generation & Configuration (Priority: P1) — Phase 1 MVP

The backend transforms user's natural language extraction instructions into optimized LLM prompts with appropriate model configurations. Prompts are versioned and auto-generated.

**Why this priority**: This is the intelligence layer. Without quality prompt generation, extractions will fail regardless of LLM power.

**Workflow Step:** Step 3 (Schema Definition - background processing)

**Independent Test**: Backend receives variable definition, generates LLM prompt incorporating project context (domain, language, unit_of_observation), stores prompt with model config (temperature per variable type), and supports prompt versioning.

**Acceptance Scenarios**:

1. **Given** user defines text variable with instructions, **When** backend generates prompt, **Then** prompt includes project context, variable type, response_schema, and extraction format
2. **Given** user defines categorical variable with classification rules, **When** backend generates prompt, **Then** prompt includes categories and selection logic
3. **Given** variable type is BOOLEAN, **When** backend configures model, **Then** temperature is set to 0.1
4. **Given** variable is updated, **When** backend regenerates prompt, **Then** new prompt version is stored with is_active=true and previous version deactivated

---

### User Story 3 - Document Upload & Ingestion (Priority: P1) — Phase 1 MVP

Users upload documents in supported formats. The backend parses and stores text content, calculates word counts, and chunks large documents.

**Why this priority**: Documents are the raw material for extraction. Without ingestion, nothing else works.

**Workflow Step:** Step 1 (Project Setup & Document Input)

**Acceptance Scenarios**:

1. **Given** user uploads PDF, **When** backend receives file, **Then** text is extracted via PyMuPDF, word_count calculated, status set to READY
2. **Given** user uploads DOCX, **When** backend receives file, **Then** text is extracted via python-docx
3. **Given** document exceeds 5000 words, **When** backend processes it, **Then** document is chunked into DocumentChunk records (2000-3000 tokens, 200-300 token overlap)
4. **Given** document parsing fails, **When** error occurs, **Then** document status set to FAILED with error_message

---

### User Story 4 - Sample Processing & Validation (Priority: P1) — Phase 1 MVP

A researcher tests their schema on a sample of documents. The backend processes the sample, returns results with confidence scores, accepts feedback, and supports prompt refinement.

**Why this priority**: Sample testing prevents costly errors. Users need to validate extraction quality before processing hundreds of documents.

**Workflow Step:** Step 5A (Sample Testing)

**Independent Test**: Backend processes sample subset, calls LLM for each variable, parses responses, stores extractions with confidence and source_text, accepts user feedback.

**Acceptance Scenarios**:

1. **Given** user requests sample processing, **When** backend receives sample request with document IDs, **Then** backend creates ProcessingJob with type=SAMPLE
2. **Given** sample job starts, **When** backend processes each document, **Then** LLM is called for each variable using auto-generated prompt via LangChain
3. **Given** LLM returns response, **When** backend parses response, **Then** extracted value (JSONB), confidence score, source_text, and prompt_version are stored
4. **Given** user flags extraction as incorrect, **When** backend receives feedback with feedback_type and corrected_value, **Then** ExtractionFeedback is stored
5. **Given** prompt is updated after feedback, **When** user re-runs sample, **Then** new prompt version is used

---

### User Story 5 - Full Batch Processing (Priority: P1) — Phase 1/2

A researcher processes all documents after validating schema. The backend runs asynchronous batch processing with progress tracking and error handling.

**Why this priority**: This is the core deliverable. Without reliable batch processing, the tool cannot handle real research workloads.

**Workflow Step:** Step 5B (Full Processing)

**Acceptance Scenarios**:

1. **Given** user approves schema after sample, **When** frontend triggers full processing, **Then** backend creates ProcessingJob with type=FULL and status=PENDING
2. **Given** processing job starts, **When** backend processes documents, **Then** progress updates are stored (documents_processed, documents_failed, progress percentage)
3. **Given** document processing fails, **When** error occurs, **Then** error is logged in ProcessingLog, document marked FAILED, consecutive_failures incremented, processing continues
4. **Given** consecutive_failures > 10, **When** threshold exceeded, **Then** job auto-pauses with status=PAUSED
5. **Given** all documents processed, **When** job completes, **Then** job status updates to COMPLETED and project status to COMPLETE

---

### User Story 6 - Data Aggregation & Export (Priority: P1) — Phase 1 MVP

A researcher exports processed data. The backend aggregates extractions, structures dataset, and generates export files with metadata.

**Why this priority**: This delivers the final product. Without export, all processing is wasted.

**Workflow Step:** Step 6 (Results & Export)

**Acceptance Scenarios**:

1. **Given** processing complete, **When** frontend requests results, **Then** backend returns dataset with columns=variables, rows=unit_of_observation
2. **Given** user requests CSV wide format, **When** backend generates export, **Then** each row represents one unit of observation with all variables as columns
3. **Given** variable has max_values=3 with if_multiple_values=ALL, **When** backend generates export, **Then** wide format includes variable_1, variable_2, variable_3 columns
4. **Given** user includes confidence scores, **When** backend generates export, **Then** _confidence_{variable} columns are included
5. **Given** user requests codebook, **When** backend generates export, **Then** codebook includes variable definitions, classification rules, and quality metrics

---

### Edge Cases

- What happens when LLM call times out? (Retry up to 5 times with exponential backoff: 1s, 2s, 4s, 8s, 16s)
- What happens when LLM returns malformed response? (Log parse error, mark extraction as FAILED, continue processing)
- What happens when user cancels processing mid-job? (Update job status to PAUSED, stop processing new documents, preserve completed extractions)
- What happens when project has 0 documents during processing? (Return validation error, do not create job)
- What happens when document exceeds LLM context window? (Chunk document, process chunks separately, merge/deduplicate results)
- What happens when circuit breaker opens? (5 consecutive LLM failures → fail fast for 30s, then half-open with 3 successes to close)
- What happens when concurrent processing jobs run for same project? (Prevent via status check — only one active job per project)

## Requirements *(mandatory)*

### Functional Requirements

**Project & Schema Management**
- **FR-001**: System MUST store project metadata (id, user_id, name, description, domain, language, unit_of_observation, entity_identification_pattern, status)
- **FR-002**: System MUST store variable definitions with expanded fields (name, display_name, type, instructions, classification_rules, confidence_threshold, if_uncertain, if_multiple_values, max_values, default_value, validation_rules, depends_on, order)
- **FR-003**: System MUST support prompt versioning with is_active flag
- **FR-004**: System MUST associate variables with projects via project_id FK
- **FR-005**: System MUST retrieve complete project state (metadata + schema + processing status)

**Prompt Generation (Auto-Generated)**
- **FR-006**: System MUST auto-generate LLM assistant configurations from variable definitions
- **FR-007**: System MUST incorporate full project context into prompts (domain, language, unit_of_observation, entity_identification_pattern)
- **FR-008**: System MUST specify output JSON schema in prompts matching variable type
- **FR-009**: System MUST set model temperature per variable type (0.1 for BOOLEAN/CATEGORY, 0.15 for DATE/NUMBER, 0.2 for TEXT)
- **FR-010**: System MUST store generated prompts with version history, model, temperature, max_tokens, response_schema

**LLM Integration**
- **FR-011**: System MUST use LangChain 0.3+ for all LLM calls
- **FR-012**: System MUST support OpenAI as default provider with ability to switch to other providers

**Document Ingestion**
- **FR-013**: System MUST support document upload in PDF, DOCX, TXT, HTML formats
- **FR-014**: System MUST extract text content using appropriate parsers (PyMuPDF, python-docx, BeautifulSoup)
- **FR-015**: System MUST calculate word_count and set document status (UPLOADED → PARSED → READY → FAILED)
- **FR-016**: System MUST chunk large documents (>5000 words) into DocumentChunk records with semantic boundaries

**Extraction Pipeline**
- **FR-017**: System MUST create processing jobs (SAMPLE or FULL) with configurable document subset
- **FR-018**: System MUST call LLM for each (document, variable) pair via auto-generated prompt
- **FR-019**: System MUST store extraction results with value (JSONB), confidence, source_text, prompt_version, status
- **FR-020**: System MUST support entity-level extraction (multiple records per document based on entity_identification_pattern)
- **FR-021**: System MUST track processing progress (documents_processed, documents_failed, progress percentage)
- **FR-022**: System MUST apply post-processing (type coercion, validation, default values, confidence check, multi-value handling)
- **FR-023**: System MUST save extractions atomically per document (all-or-nothing)

**Error Handling & Resilience**
- **FR-024**: System MUST retry failed LLM calls up to 5 times with exponential backoff via tenacity
- **FR-025**: System MUST implement circuit breaker (open after 5 consecutive failures, half-open after 30s)
- **FR-026**: System MUST log errors in ProcessingLog with event_type, message, and metadata
- **FR-027**: System MUST continue processing after individual document failures
- **FR-028**: System MUST auto-pause job when consecutive_failures > 10
- **FR-029**: System MUST support job pause/resume/cancel

**Feedback & Refinement**
- **FR-030**: System MUST accept user feedback with feedback_type (CORRECT, INCORRECT, PARTIALLY_CORRECT), corrected_value, and user_note
- **FR-031**: System MUST analyze feedback patterns and support prompt refinement
- **FR-032**: System MUST create new prompt version on refinement (previous version deactivated)

**Data Export**
- **FR-033**: System MUST aggregate extractions into dataset (columns=variables, rows=unit_of_observation)
- **FR-034**: System MUST support CSV wide format (1 row per unit, multi-value columns for max_values > 1)
- **FR-035**: System MUST support CSV long format (1 row per extraction)
- **FR-036**: System MUST support Excel (.xlsx) export with formatting
- **FR-037**: System MUST optionally include metadata columns (_confidence, _source, _prompt_version per variable)
- **FR-038**: System MUST generate codebook (variable definitions, classification rules, quality metrics)

**Background Jobs (ARQ + Redis)**
- **FR-039**: System MUST use ARQ + Redis for background job processing
- **FR-040**: System MUST support job types: extraction_job, prompt_refinement_job, export_job
- **FR-041**: System MUST support job resumability (skip already-processed documents on resume)

**Authentication & Multi-tenancy (Phase 2)**
- **FR-042**: System MUST implement JWT authentication (access + refresh tokens)
- **FR-043**: System MUST enforce Row-Level Security at database level
- **FR-044**: System MUST set tenant context per request via SQLAlchemy event listener

**Real-time Updates (Phase 2)**
- **FR-045**: System MUST provide WebSocket endpoint for real-time job progress
- **FR-046**: System MUST emit events: progress, document_completed, document_failed, job_completed, job_failed

**AI Co-pilot (Phase 3)**
- **FR-047**: System MUST support co-pilot agent for variable suggestions based on document type and domain
- **FR-048**: System MUST support refinement agent for prompt improvement from feedback patterns

### Non-Functional Requirements

**Performance**
- **NFR-001**: Sample processing (20 documents, 5 variables) MUST complete within 5 minutes
- **NFR-002**: API response time for CRUD operations MUST be < 200ms (p95)
- **NFR-003**: System MUST support concurrent processing via ARQ workers
- **NFR-004**: Export generation (100 docs × 10 vars) MUST complete in < 3 seconds

**Scalability**
- **NFR-005**: System MUST handle projects with up to 10,000 documents
- **NFR-006**: System MUST handle schemas with up to 50 variables
- **NFR-007**: Database queries MUST use indexes for fast retrieval
- **NFR-008**: LLM API calls MUST be rate-limited (configurable per-minute limit)

**Reliability**
- **NFR-009**: Job failures MUST not corrupt database state (atomic transactions)
- **NFR-010**: Processing MUST be resumable after server restart
- **NFR-011**: Circuit breaker MUST prevent cascading LLM failures
- **NFR-012**: Idempotent processing (reprocessing overwrites, not duplicates)

**Security**
- **NFR-013**: API keys MUST be stored in environment variables
- **NFR-014**: Multi-tenant data isolation MUST be enforced at database level (RLS)
- **NFR-015**: All API endpoints MUST validate inputs via Pydantic
- **NFR-016**: User-defined instructions MUST be sandboxed against prompt injection

### Key Entities (from CODERAI_REFERENCE.md Section 3)

See [data-model.md](data-model.md) for complete entity definitions. Summary:

- **User**: Authentication and tenant identity
- **Project**: Research project with domain, language, unit_of_observation, status
- **Variable**: Extraction target with expanded configuration (18 fields)
- **Prompt**: Versioned auto-generated LLM prompt with model config
- **Document**: Uploaded document with parsed text, word_count, status
- **DocumentChunk**: Chunks for large documents with token overlap
- **ProcessingJob**: SAMPLE or FULL extraction job with progress tracking
- **Extraction**: Single extracted value per document×variable (or entity×variable)
- **ExtractionFeedback**: User feedback with feedback_type enum
- **ProcessingLog**: Audit trail with event_type enum and metadata

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend can store and retrieve project with 10 variables in < 200ms
- **SC-002**: Prompt generation for variable completes in < 1 second
- **SC-003**: Sample processing (20 documents, 5 variables) completes in < 5 minutes with real LLM calls
- **SC-004**: Failed LLM calls are retried automatically with exponential backoff (up to 5 retries)
- **SC-005**: Circuit breaker opens after 5 consecutive failures and recovers via half-open state
- **SC-006**: Export generation for 100 documents × 10 variables completes in < 3 seconds
- **SC-007**: Background processing via ARQ updates progress in real-time
- **SC-008**: Row-Level Security prevents cross-tenant data access
- **SC-009**: Entity-level extraction produces correct number of records per document
- **SC-010**: All API endpoints return appropriate error codes and messages for invalid inputs
