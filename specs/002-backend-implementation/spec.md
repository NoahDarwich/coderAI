# Feature Specification: Backend Implementation for Data Extraction Workflow

**Feature Branch**: `002-backend-implementation`
**Created**: 2025-11-26
**Updated**: 2026-02-09
**Status**: In Progress
**Input**: backend-workflow-reference.md + USER_WORKFLOW.md + ai_agent_reference.md

## User Workflow Context

**Primary Workflow Step(s):** All steps 1-5 (backend services supporting complete workflow)

**Workflow Alignment:** This feature implements the backend services that power the 5-step user workflow. While the frontend handles user interaction (001-complete-user-workflow), the backend processes data, manages state, orchestrates LLM calls, and delivers structured datasets.

## Overview

The backend implements a **user-configurable corpus processing pipeline** that transforms user inputs into structured datasets. Each project defines its own domain, extraction targets, and variables through the frontend UI. The system auto-generates LLM assistant configurations from these definitions, ingests documents in multiple formats, processes them through LangChain-powered extraction stages, and delivers structured results.

**Pipeline Architecture Reference:** See [ai_agent_reference.md](/ai_agent_reference.md) for detailed pipeline stages, LLM integration patterns, and implementation patterns.

**Core Responsibilities:**
- Store and manage project metadata, schemas, and processing state
- **Auto-generate** LLM assistant configurations from user-defined variables (prompts, model configs, response schemas)
- **Ingest documents** in all common formats (PDF, DOCX, CSV, JSON, Parquet, plain text)
- Orchestrate the extraction pipeline: Extraction → Enrichment → Post-Processing → Storage
- Process documents through **LangChain** for multi-provider LLM abstraction
- Manage sample testing workflow with feedback-driven prompt refinement
- Aggregate and structure extraction results for CSV + Excel export with quality metrics
- Handle asynchronous processing with background jobs

**Architecture Decisions:**
- **LLM Provider**: LangChain 0.3+ (supports OpenAI, Anthropic, local models)
- **Database**: SQLAlchemy 2.0 (async) with Alembic migrations
- **Ingestion**: All common formats (PDF, DOCX, CSV, JSON, Parquet, TXT)
- **Assistant Config**: Auto-generated from user variables (not manually configured)
- **Export**: CSV + Excel with filtering, confidence scores, and codebook
- **Deferred (v2)**: Duplicate detection, external API enrichment (geocoding, etc.), advanced job queue

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Project & Schema Management (Priority: P1) 🎯 MVP

A researcher creates a project and defines extraction variables. The backend must store this configuration and make it available for processing.

**Why this priority**: Without persistent storage of project metadata and schemas, users cannot save work or process documents later. This is foundational for all other backend features.

**Workflow Step:** Steps 1-2 (Project Setup, Schema Definition)

**Independent Test**: Backend can receive project creation request with metadata, store project, accept variable definitions, store schema with versioning, and retrieve project state.

**Acceptance Scenarios**:

1. **Given** frontend sends project creation request, **When** backend receives project name and scale, **Then** backend creates project with unique ID and returns project object
2. **Given** user defines variable with name/type/instructions, **When** frontend sends variable definition, **Then** backend stores variable and associates with project
3. **Given** user edits variable, **When** frontend sends updated definition, **Then** backend updates variable and increments schema version
4. **Given** frontend requests project details, **When** backend receives project ID, **Then** backend returns complete project with all variables

---

### User Story 2 - Prompt Generation & Configuration (Priority: P1) 🎯 MVP

The backend transforms user's natural language extraction instructions into optimized LLM prompts with appropriate model configurations.

**Why this priority**: This is the intelligence layer. Without quality prompt generation, extractions will fail regardless of LLM power. This determines extraction quality.

**Workflow Step:** Step 2 (Schema Definition - background processing)

**Independent Test**: Backend receives variable definition, generates LLM prompt incorporating project context, stores prompt with model config, and supports prompt versioning.

**Acceptance Scenarios**:

1. **Given** user defines text variable with instructions, **When** backend generates prompt, **Then** prompt includes project context, variable type, and extraction format specifications
2. **Given** user defines categorical variable with classification rules, **When** backend generates prompt, **Then** prompt includes categories and selection logic
3. **Given** variable requires high precision, **When** backend configures model, **Then** temperature is set to 0.2 or lower
4. **Given** variable is updated, **When** backend regenerates prompt, **Then** new prompt version is stored and previous versions are retained

---

### User Story 3 - Sample Processing & Validation (Priority: P1) 🎯 MVP

A researcher tests their schema on a sample of documents. The backend processes the sample, returns results, accepts feedback, and refines prompts.

**Why this priority**: Sample testing prevents costly errors. Users need to validate extraction quality before processing hundreds of documents. Feedback loop is critical for prompt refinement.

**Workflow Step:** Step 4A (Sample Testing)

**Independent Test**: Backend processes sample subset, calls LLM for each variable, parses responses, accepts user flags for incorrect extractions, analyzes corrections, and updates prompts.

**Acceptance Scenarios**:

1. **Given** user requests sample processing, **When** backend receives sample request with 10 document IDs, **Then** backend creates processing job for those 10 documents only
2. **Given** sample job starts, **When** backend processes each document, **Then** LLM is called for each variable with that variable's prompt
3. **Given** LLM returns response, **When** backend parses response, **Then** extracted value and confidence score are stored
4. **Given** user flags extraction as incorrect, **When** backend receives correction with explanation, **Then** backend analyzes error and modifies prompt
5. **Given** prompt is updated, **When** user re-runs sample, **Then** new prompt version is used

---

### User Story 4 - Full Batch Processing (Priority: P1) 🎯 MVP

A researcher processes all documents after validating schema. The backend runs asynchronous batch processing with progress tracking and error handling.

**Why this priority**: This is the core deliverable. Without reliable batch processing, the tool cannot handle real research workloads. Background processing is essential for large datasets.

**Workflow Step:** Step 4B (Full Processing)

**Independent Test**: Backend creates batch job for all documents, processes asynchronously, tracks progress, logs errors, continues despite failures, and notifies on completion.

**Acceptance Scenarios**:

1. **Given** user approves schema after sample, **When** frontend triggers full processing, **Then** backend creates processing job with status "PROCESSING"
2. **Given** processing job starts, **When** backend processes documents, **Then** progress updates are stored (documents completed, current document, percentage)
3. **Given** document processing fails, **When** error occurs, **Then** error is logged, document is marked failed, and processing continues with next document
4. **Given** all documents processed, **When** job completes, **Then** job status updates to "COMPLETE" and notification is triggered
5. **Given** user navigates away, **When** processing continues, **Then** frontend can poll for progress updates

---

### User Story 5 - Data Aggregation & Export (Priority: P1) 🎯 MVP

A researcher exports processed data in desired format. The backend aggregates extractions, structures dataset, and generates export file with metadata.

**Why this priority**: This delivers the final product. Without export, all processing is wasted. Different export formats support different analysis workflows.

**Workflow Step:** Step 5 (Results & Export)

**Independent Test**: Backend retrieves all extractions for project, structures data in wide/long format, includes optional metadata (confidence scores, source text), and generates CSV/Excel/JSON.

**Acceptance Scenarios**:

1. **Given** processing complete, **When** frontend requests results, **Then** backend returns dataset with columns = variables, rows = documents
2. **Given** user requests CSV wide format, **When** backend generates export, **Then** each row represents one document with all variables as columns
3. **Given** user requests CSV long format, **When** backend generates export, **Then** each row represents one extraction (document ID, variable name, value)
4. **Given** user includes confidence scores, **When** backend generates export, **Then** additional columns include confidence for each variable
5. **Given** user includes source text, **When** backend generates export, **Then** additional columns include document excerpt that generated extraction

---

### Edge Cases

- What happens when LLM call times out? (Retry up to 3 times, then mark extraction as failed with timeout error)
- What happens when LLM returns malformed response? (Log parse error, mark extraction as failed, continue processing)
- What happens when user cancels processing mid-job? (Update job status to CANCELLED, stop processing new documents, preserve completed extractions)
- What happens when project has 0 documents during processing? (Return validation error, do not create job)
- What happens when user requests export before processing complete? (Return error with processing status, or return partial results with warning)
- What happens when document exceeds LLM context window? (Chunk document, process chunks separately, aggregate results or return error)

## Requirements *(mandatory)*

### Functional Requirements

**Project & Schema Management**
- **FR-001**: System MUST store project metadata (ID, name, scale, creation date, status)
- **FR-002**: System MUST store variable definitions with name, type, instructions, classification rules
- **FR-003**: System MUST support schema versioning (track prompt updates)
- **FR-004**: System MUST associate variables with projects via project ID
- **FR-005**: System MUST retrieve complete project state (metadata + schema + processing status)

**Prompt Generation (Auto-Generated)**
- **FR-006**: System MUST auto-generate LLM assistant configurations from variable definitions
- **FR-007**: System MUST incorporate full project context into prompts (document type, domain, language, unit of observation)
- **FR-008**: System MUST specify output format in prompts (JSON schema matching variable type)
- **FR-009**: System MUST auto-select model parameters per variable type (temperature, max_tokens based on precision needs)
- **FR-010**: System MUST store generated prompts with version history for feedback-driven refinement

**LLM Integration**
- **FR-010a**: System MUST use LangChain 0.3+ for all LLM calls (multi-provider abstraction)
- **FR-010b**: System MUST support OpenAI as default provider with ability to switch to Anthropic/local models

**Document Processing**
- **FR-011**: System MUST create processing jobs with configurable document subset (sample vs full)
- **FR-012**: System MUST call LLM API for each (document, variable) pair
- **FR-013**: System MUST parse LLM responses and extract structured data
- **FR-014**: System MUST store extraction results with document ID, variable ID, value, confidence score
- **FR-015**: System MUST track processing progress (documents completed, current document, percentage)
- **FR-016**: System MUST support asynchronous processing (background jobs)

**Error Handling & Resilience**
- **FR-017**: System MUST retry failed LLM calls up to 3 times with exponential backoff
- **FR-018**: System MUST log errors with context (document ID, variable ID, error message)
- **FR-019**: System MUST continue processing after individual document/variable failures
- **FR-020**: System MUST mark documents as FAILED when all retries exhausted
- **FR-021**: System MUST support job cancellation mid-processing

**Feedback & Refinement**
- **FR-022**: System MUST accept user feedback on extraction quality (correct/incorrect flags)
- **FR-023**: System MUST analyze feedback and identify prompt improvement opportunities
- **FR-024**: System MUST update prompts based on feedback and create new version
- **FR-025**: System MUST support re-running sample with updated prompts

**Document Ingestion**
- **FR-025a**: System MUST support document upload in all common formats (PDF, DOCX, TXT, CSV, JSON, Parquet)
- **FR-025b**: System MUST support bulk ingestion from tabular formats (CSV, JSON, Parquet) where each row becomes a document
- **FR-025c**: System MUST extract text content from each format using appropriate parsers (PyMuPDF, python-docx, pandas)

**Data Export**
- **FR-026**: System MUST aggregate extractions into dataset structure (columns = variables, rows = unit of observation)
- **FR-027**: System MUST support CSV wide format export (1 row per unit of observation)
- **FR-028**: System MUST support CSV long format export (1 row per extraction)
- **FR-029**: System MUST optionally include confidence scores in export
- **FR-030**: System MUST optionally include source text spans in export
- **FR-031**: System MUST include project metadata and variable definitions (codebook) in export package
- **FR-031a**: System MUST support Excel (.xlsx) export format
- **FR-031b**: System MUST include quality metrics in export metadata (success rate, avg confidence)

### Non-Functional Requirements

**Performance**
- **NFR-001**: Sample processing (20 documents, 5 variables) MUST complete within 5 minutes (with real LLM calls)
- **NFR-002**: API response time for project retrieval MUST be < 200ms
- **NFR-003**: System MUST support concurrent processing of multiple projects
- **NFR-004**: Background jobs MUST not block API requests

**Scalability**
- **NFR-005**: System MUST handle projects with up to 1000 documents
- **NFR-006**: System MUST handle schemas with up to 50 variables
- **NFR-007**: Database queries MUST use indexes for fast retrieval
- **NFR-008**: LLM API calls MUST be rate-limited to prevent quota exhaustion

**Reliability**
- **NFR-009**: Job failures MUST not corrupt database state
- **NFR-010**: Processing MUST be resumable after server restart
- **NFR-011**: System MUST maintain data integrity during concurrent updates
- **NFR-012**: Failed LLM calls MUST not cause job termination

**Security**
- **NFR-013**: API keys for LLM providers MUST be stored in environment variables
- **NFR-014**: User documents MUST be stored securely (encryption at rest if required)
- **NFR-015**: API endpoints MUST validate all inputs
- **NFR-016**: Database queries MUST use parameterized statements (prevent SQL injection)

### Key Entities

- **Project**: Research project with metadata
  - Fields: id (UUID), name (string), scale (enum: SMALL, LARGE), language (string), domain (string), status (enum), created_at (timestamp), updated_at (timestamp)

- **Variable**: Extraction target definition
  - Fields: id (UUID), project_id (FK), name (string), type (enum: TEXT, NUMBER, DATE, CATEGORY, BOOLEAN), instructions (text), classification_rules (JSON), order (int), created_at (timestamp), updated_at (timestamp)

- **Prompt**: Generated LLM prompt for a variable
  - Fields: id (UUID), variable_id (FK), prompt_text (text), model_config (JSON: model, temperature, max_tokens), version (int), created_at (timestamp)

- **Document**: Uploaded document (supports all common formats)
  - Fields: id (UUID), project_id (FK), name (string), content (text), content_type (enum: PDF, DOCX, TXT, CSV, JSON, PARQUET), uploaded_at (timestamp)

- **ProcessingJob**: Batch processing job
  - Fields: id (UUID), project_id (FK), job_type (enum: SAMPLE, FULL), status (enum: PENDING, PROCESSING, COMPLETE, FAILED, CANCELLED), document_ids (JSON array), progress (int 0-100), started_at (timestamp), completed_at (timestamp)

- **Extraction**: Single extracted value
  - Fields: id (UUID), job_id (FK), document_id (FK), variable_id (FK), value (text), confidence (float 0-1), source_text (text), created_at (timestamp)

- **ExtractionFeedback**: User feedback on extraction quality
  - Fields: id (UUID), extraction_id (FK), is_correct (boolean), user_comment (text), created_at (timestamp)

- **ProcessingLog**: Log entry for processing events
  - Fields: id (UUID), job_id (FK), document_id (FK), variable_id (FK), log_level (enum: INFO, WARNING, ERROR), message (text), created_at (timestamp)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend can store and retrieve project with 10 variables in < 200ms
- **SC-002**: Prompt generation for variable completes in < 1 second
- **SC-003**: Sample processing (20 documents, 5 variables) completes in < 5 minutes with real LLM calls
- **SC-004**: Failed LLM calls are retried automatically without manual intervention
- **SC-005**: Processing job continues successfully after single document failure (99% success rate for remaining documents)
- **SC-006**: Export generation for 100 documents × 10 variables completes in < 3 seconds
- **SC-007**: Background processing updates progress in real-time (< 1 second delay)
- **SC-008**: API maintains 99.9% uptime during 8-hour processing jobs
- **SC-009**: Database supports 100 concurrent project queries without degradation
- **SC-010**: All API endpoints return appropriate error codes and messages for invalid inputs
