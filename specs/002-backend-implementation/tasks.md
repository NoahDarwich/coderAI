# Implementation Tasks: Backend Implementation for Data Extraction Workflow

**Feature**: 002-backend-implementation
**Branch**: `002-backend-implementation`
**Created**: 2025-11-26
**Status**: Ready for Implementation

---

## Task Summary

- **Total Tasks**: 89
- **MVP Scope**: All 5 user stories (US1-US5) - Complete backend implementation
- **Parallel Opportunities**: 47 tasks marked [P]
- **Estimated Duration**: 5 weeks (following quickstart.md phases)

---

## User Story Mapping

| Phase | User Story | Task Count | Dependencies |
|-------|-----------|------------|--------------|
| 1 | Setup | 12 | None (start here) |
| 2 | Foundational | 14 | Phase 1 complete |
| 3 | US1: Project & Schema Management | 13 | Phase 2 complete |
| 4 | US2: Prompt Generation | 10 | US1 complete |
| 5 | US3: Sample Processing | 12 | US2 complete |
| 6 | US4: Full Batch Processing | 11 | US3 complete |
| 7 | US5: Data Export | 9 | US4 complete |
| 8 | Polish & Cross-Cutting | 8 | All US complete |

---

## Phase 1: Setup & Project Initialization

**Goal**: Initialize backend directory structure, dependencies, and development environment

**Tasks**:

- [X] T001 Create backend directory structure per plan.md at backend/
- [X] T002 Create backend/requirements.txt with FastAPI 0.100+, SQLAlchemy 2.0, Pydantic V2, LangChain 0.3+, OpenAI SDK, PyMuPDF, python-docx, pandas, openpyxl
- [X] T003 Create backend/requirements-dev.txt with pytest, pytest-asyncio, pytest-cov, black, ruff
- [X] T004 Create backend/.env.example with DATABASE_URL, REDIS_URL, OPENAI_API_KEY, API_HOST, API_PORT, DEBUG, ALLOWED_ORIGINS placeholders
- [X] T005 Create backend/.gitignore with Python patterns (__pycache__/, *.pyc, .venv/, venv/, dist/, *.egg-info/, .env, *.log)
- [X] T006 Create backend/README.md with setup instructions and development commands
- [X] T007 Initialize Alembic in backend/ with alembic init alembic command
- [X] T008 Create backend/alembic.ini configuration with database URL from environment variable
- [X] T009 Create backend/docker/Dockerfile for containerized deployment
- [X] T010 Create backend/docker/docker-compose.yml with PostgreSQL, Redis, and API services
- [X] T011 Create backend/src/core/config.py with Pydantic Settings for environment variables
- [X] T012 Create backend/src/core/database.py with SQLAlchemy async engine and session factory

**Validation**: Directory structure matches plan.md, dependencies installed, Alembic initialized

---

## Phase 2: Foundational Infrastructure

**Goal**: Set up database models, schemas, and core services (blocking prerequisites for all user stories)

**Dependencies**: Phase 1 complete

**Tasks**:

- [X] T013 [P] Create backend/src/models/__init__.py with Base model import
- [X] T014 [P] Create backend/src/models/project.py with Project SQLAlchemy model (fields per data-model.md)
- [X] T015 [P] Create backend/src/models/variable.py with Variable SQLAlchemy model (fields per data-model.md)
- [X] T016 [P] Create backend/src/models/prompt.py with Prompt SQLAlchemy model (fields per data-model.md)
- [X] T017 [P] Create backend/src/models/document.py with Document SQLAlchemy model (fields per data-model.md)
- [X] T018 [P] Create backend/src/models/processing_job.py with ProcessingJob SQLAlchemy model (fields per data-model.md)
- [X] T019 [P] Create backend/src/models/extraction.py with Extraction SQLAlchemy model (fields per data-model.md)
- [X] T020 [P] Create backend/src/models/extraction_feedback.py with ExtractionFeedback SQLAlchemy model (fields per data-model.md)
- [X] T021 [P] Create backend/src/models/processing_log.py with ProcessingLog SQLAlchemy model (fields per data-model.md)
- [X] T022 Generate initial Alembic migration with alembic revision --autogenerate -m "Initial schema" in backend/
- [X] T023 Review and edit generated migration in backend/alembic/versions/ to ensure all models included
- [X] T024 Apply migration with alembic upgrade head in backend/
- [X] T025 [P] Create backend/src/api/dependencies.py with get_db dependency for database sessions
- [X] T026 [P] Create backend/src/api/middleware.py with CORS middleware and error handling

**Validation**: Database migrations applied successfully, all 8 tables created with indexes

---

## Phase 3: User Story 1 - Project & Schema Management

**Goal**: Implement project CRUD and variable definition storage

**User Story**: US1 - A researcher creates a project and defines extraction variables. The backend must store this configuration and make it available for processing.

**Independent Test**: Backend can receive project creation request with metadata, store project, accept variable definitions, store schema with versioning, and retrieve project state.

**Dependencies**: Phase 2 complete

**Tasks**:

- [X] T027 [US1] Create backend/src/schemas/project.py with ProjectCreate, ProjectUpdate, Project, ProjectDetail Pydantic schemas
- [X] T028 [US1] Create backend/src/schemas/variable.py with VariableCreate, VariableUpdate, Variable, VariableDetail Pydantic schemas
- [X] T029 [US1] Create backend/src/api/routes/projects.py with POST /api/v1/projects endpoint (create project)
- [X] T030 [US1] Implement GET /api/v1/projects endpoint (list projects with pagination) in backend/src/api/routes/projects.py
- [X] T031 [US1] Implement GET /api/v1/projects/{projectId} endpoint (get project details) in backend/src/api/routes/projects.py
- [X] T032 [US1] Implement PUT /api/v1/projects/{projectId} endpoint (update project) in backend/src/api/routes/projects.py
- [X] T033 [US1] Implement DELETE /api/v1/projects/{projectId} endpoint (delete project) in backend/src/api/routes/projects.py
- [X] T034 [US1] Create backend/src/api/routes/variables.py with GET /api/v1/projects/{projectId}/variables endpoint (list variables)
- [X] T035 [US1] Implement POST /api/v1/projects/{projectId}/variables endpoint (create variable) in backend/src/api/routes/variables.py
- [X] T036 [US1] Implement GET /api/v1/variables/{variableId} endpoint (get variable details) in backend/src/api/routes/variables.py
- [X] T037 [US1] Implement PUT /api/v1/variables/{variableId} endpoint (update variable) in backend/src/api/routes/variables.py
- [X] T038 [US1] Implement DELETE /api/v1/variables/{variableId} endpoint (delete variable) in backend/src/api/routes/variables.py
- [X] T039 [US1] Create backend/src/main.py with FastAPI app initialization, include routers, configure CORS

**Acceptance Criteria**:
1. ✅ Frontend can create project with name and scale, backend returns project with UUID
2. ✅ Frontend can create variable with name/type/instructions, backend stores and associates with project
3. ✅ Frontend can update variable, backend updates and increments schema version
4. ✅ Frontend can retrieve complete project with all variables

**Validation**: All project and variable CRUD operations work via API, OpenAPI docs available at /docs

---

## Phase 4: User Story 2 - Prompt Generation & Configuration

**Goal**: Transform user's natural language instructions into optimized LLM prompts

**User Story**: US2 - The backend transforms user's natural language extraction instructions into optimized LLM prompts with appropriate model configurations.

**Independent Test**: Backend receives variable definition, generates LLM prompt incorporating project context, stores prompt with model config, and supports prompt versioning.

**Dependencies**: US1 complete (requires Variable model)

**Tasks**:

- [X] T040 [US2] Create backend/src/services/prompt_generator.py with generate_prompt(variable, project_context) function
- [X] T041 [US2] Implement prompt template for TEXT variable type in backend/src/services/prompt_generator.py
- [X] T042 [US2] Implement prompt template for CATEGORY variable type with classification rules in backend/src/services/prompt_generator.py
- [X] T043 [US2] Implement prompt template for NUMBER variable type in backend/src/services/prompt_generator.py
- [X] T044 [US2] Implement prompt template for DATE variable type in backend/src/services/prompt_generator.py
- [X] T045 [US2] Implement prompt template for BOOLEAN variable type in backend/src/services/prompt_generator.py
- [X] T046 [US2] Implement model configuration logic (temperature=0.2 for precision, max_tokens based on type) in backend/src/services/prompt_generator.py
- [X] T047 [US2] Update POST /api/v1/projects/{projectId}/variables endpoint to auto-generate prompt on variable creation in backend/src/api/routes/variables.py
- [X] T048 [US2] Update PUT /api/v1/variables/{variableId} endpoint to regenerate prompt and increment version on variable update in backend/src/api/routes/variables.py
- [X] T049 [US2] Update GET /api/v1/variables/{variableId} endpoint to include current prompt in response in backend/src/api/routes/variables.py

**Acceptance Criteria**:
1. ✅ Text variable generates prompt with project context and extraction format
2. ✅ Categorical variable generates prompt with categories and selection logic
3. ✅ High precision variables have temperature ≤ 0.2
4. ✅ Variable update creates new prompt version and preserves old versions

**Validation**: Prompts generated correctly for all variable types, prompt versioning works

---

## Phase 5: User Story 3 - Sample Processing & Validation

**Goal**: Process sample documents, return results, accept feedback, refine prompts

**User Story**: US3 - A researcher tests their schema on a sample of documents. The backend processes the sample, returns results, accepts feedback, and refines prompts.

**Independent Test**: Backend processes sample subset, calls LLM for each variable, parses responses, accepts user flags for incorrect extractions, analyzes corrections, and updates prompts.

**Dependencies**: US2 complete (requires prompt generation)

**Tasks**:

- [X] T050 [US3] Create backend/src/schemas/document.py with DocumentCreate, Document, DocumentDetail Pydantic schemas
- [X] T051 [US3] Create backend/src/schemas/processing.py with JobCreate, ProcessingJob, JobDetail, Extraction Pydantic schemas
- [X] T052 [US3] Create backend/src/services/document_processor.py with parse_pdf(file), parse_docx(file), parse_txt(file) functions using PyMuPDF and python-docx
- [X] T053 [US3] Create backend/src/api/routes/documents.py with POST /api/v1/projects/{projectId}/documents endpoint (upload document with multipart/form-data)
- [X] T054 [US3] Implement GET /api/v1/projects/{projectId}/documents endpoint (list documents) in backend/src/api/routes/documents.py
- [X] T055 [US3] Implement DELETE /api/v1/documents/{documentId} endpoint (delete document) in backend/src/api/routes/documents.py
- [X] T056 [US3] Create backend/src/services/llm_client.py with LangChain ChatOpenAI integration and PydanticOutputParser for structured extraction
- [X] T057 [US3] Implement retry logic with exponential backoff (max 3 retries) in backend/src/services/llm_client.py
- [X] T058 [US3] Create backend/src/services/extraction_service.py with extract_value(document, variable, prompt) function that calls LLM
- [X] T059 [US3] Create backend/src/api/routes/processing.py with POST /api/v1/projects/{projectId}/jobs endpoint (create processing job for sample)
- [X] T060 [US3] Implement job processing logic in backend/src/services/job_manager.py to process sample documents synchronously (MVP: use FastAPI BackgroundTasks)
- [X] T061 [US3] Create backend/src/schemas/feedback.py with FeedbackCreate, Feedback Pydantic schemas and POST /api/v1/extractions/{extractionId}/feedback endpoint in backend/src/api/routes/processing.py

**Acceptance Criteria**:
1. ✅ Sample job created with 10 document IDs
2. ✅ LLM called for each variable with correct prompt
3. ✅ Extracted value and confidence score stored
4. ✅ Feedback accepted and prompt updated based on corrections
5. ✅ Re-running sample uses new prompt version

**Validation**: Sample processing works end-to-end, feedback loop updates prompts

---

## Phase 6: User Story 4 - Full Batch Processing

**Goal**: Run asynchronous batch processing with progress tracking and error handling

**User Story**: US4 - A researcher processes all documents after validating schema. The backend runs asynchronous batch processing with progress tracking and error handling.

**Independent Test**: Backend creates batch job for all documents, processes asynchronously, tracks progress, logs errors, continues despite failures, and notifies on completion.

**Dependencies**: US3 complete (requires extraction service)

**Tasks**:

- [X] T062 [US4] Implement GET /api/v1/projects/{projectId}/jobs endpoint (list jobs) in backend/src/api/routes/processing.py
- [X] T063 [US4] Implement GET /api/v1/jobs/{jobId} endpoint (get job status with progress and recent logs) in backend/src/api/routes/processing.py
- [X] T064 [US4] Implement DELETE /api/v1/jobs/{jobId} endpoint (cancel job) in backend/src/api/routes/processing.py
- [X] T065 [US4] Update POST /api/v1/projects/{projectId}/jobs endpoint to support FULL job type (all documents) in backend/src/api/routes/processing.py
- [X] T066 [US4] Implement progress tracking in backend/src/services/job_manager.py (update job.progress field as documents complete)
- [X] T067 [US4] Implement error logging in backend/src/services/job_manager.py (create ProcessingLog entries for errors)
- [X] T068 [US4] Implement error resilience in backend/src/services/job_manager.py (continue processing after individual failures, mark failed documents)
- [X] T069 [US4] Implement job cancellation logic in backend/src/services/job_manager.py (set status=CANCELLED, stop processing)
- [X] T070 [US4] Update job processing to be asynchronous using FastAPI BackgroundTasks in backend/src/services/job_manager.py
- [X] T071 [US4] Implement GET /api/v1/jobs/{jobId}/results endpoint (return extractions with optional minConfidence filter) in backend/src/api/routes/processing.py
- [X] T072 [US4] Add job status transition validation (PENDING → PROCESSING → COMPLETE/FAILED) in backend/src/models/processing_job.py

**Acceptance Criteria**:
1. ✅ Full processing job created with status PROCESSING
2. ✅ Progress updates stored (documents completed, percentage)
3. ✅ Errors logged and processing continues with next document
4. ✅ Job status updates to COMPLETE when done
5. ✅ Frontend can poll for progress updates

**Validation**: Full batch processing works asynchronously, progress tracking accurate, error handling robust

---

## Phase 7: User Story 5 - Data Aggregation & Export

**Goal**: Aggregate extractions and generate export files in desired formats

**User Story**: US5 - A researcher exports processed data in desired format. The backend aggregates extractions, structures dataset, and generates export file with metadata.

**Independent Test**: Backend retrieves all extractions for project, structures data in wide/long format, includes optional metadata (confidence scores, source text), and generates CSV/Excel/JSON.

**Dependencies**: US4 complete (requires completed extractions)

**Tasks**:

- [X] T073 [US5] Create backend/src/schemas/export.py with ExportConfig Pydantic schema (format, includeConfidence, includeSourceText, minConfidence)
- [X] T074 [US5] Create backend/src/services/export_service.py with aggregate_extractions(project_id) function using pandas
- [X] T075 [US5] Implement CSV wide format export (1 row per document, columns = variables) in backend/src/services/export_service.py
- [X] T076 [US5] Implement CSV long format export (1 row per extraction) in backend/src/services/export_service.py
- [X] T077 [US5] Implement Excel export using openpyxl in backend/src/services/export_service.py
- [X] T078 [US5] Implement JSON export in backend/src/services/export_service.py
- [X] T079 [US5] Implement optional confidence scores inclusion in backend/src/services/export_service.py
- [X] T080 [US5] Implement optional source text inclusion in backend/src/services/export_service.py
- [X] T081 [US5] Create backend/src/api/routes/exports.py with POST /api/v1/projects/{projectId}/export endpoint (generate export file, return download URL)

**Acceptance Criteria**:
1. ✅ Backend returns dataset with columns=variables, rows=documents
2. ✅ CSV wide format has 1 row per document
3. ✅ CSV long format has 1 row per extraction
4. ✅ Confidence scores included when requested
5. ✅ Source text included when requested

**Validation**: All export formats work correctly, optional metadata inclusion works

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Final polish, validation, testing, and documentation

**Dependencies**: All user stories (US1-US5) complete

**Tasks**:

- [X] T082 [P] Implement request validation for all endpoints using Pydantic in backend/src/schemas/
- [X] T083 [P] Implement RFC 7807 error format for all API errors in backend/src/api/middleware.py
- [X] T084 [P] Add database indexes for frequently queried fields per data-model.md in Alembic migration
- [X] T085 [P] Create backend/tests/conftest.py with pytest fixtures (test_db, mock_llm, sample_project)
- [X] T086 [P] Write API tests for project and variable CRUD in backend/tests/api/test_projects.py and backend/tests/api/test_variables.py
- [X] T087 [P] Write service tests for prompt generation in backend/tests/services/test_prompt_generator.py
- [X] T088 Run full test suite with pytest and verify >80% coverage in backend/
- [X] T089 Create deployment documentation in backend/README.md with Docker setup and Railway/Render deployment instructions

**Validation**: Tests pass, coverage >80%, API documentation complete, deployment ready

---

## Dependencies & Execution Flow

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (US4) → Phase 7 (US5) → Phase 8 (Polish)
```

**Dependency Justification**:
- **US1 → US2**: Prompt generation requires Variable model from US1
- **US2 → US3**: Sample processing requires prompts from US2
- **US3 → US4**: Full processing reuses extraction logic from US3
- **US4 → US5**: Export requires completed extractions from US4

### Parallel Execution Opportunities

**Phase 2 - Foundational** (Tasks can run in parallel):
- T013-T021: All model files (different files, no dependencies)
- T025-T026: API dependencies and middleware (different files)

**Phase 3 - US1** (Sequential due to shared route files):
- T027-T028: Schema files (parallel)
- T029-T033: Project routes (sequential, same file)
- T034-T038: Variable routes (sequential, same file)

**Phase 8 - Polish** (Tasks can run in parallel):
- T082-T087: All different files, no dependencies

---

## MVP Scope

**Recommended MVP**: Complete all 5 user stories (US1-US5)

**Rationale**: All 5 user stories are marked P1 (MVP priority) and form a complete, end-to-end workflow. The backend is not functional without all stories implemented - each builds on the previous to deliver the complete data extraction pipeline.

**MVP Deliverables**:
1. ✅ Project and schema management (US1)
2. ✅ Prompt generation (US2)
3. ✅ Sample processing with feedback (US3)
4. ✅ Full batch processing (US4)
5. ✅ Data export in multiple formats (US5)

**Post-MVP Enhancements** (for future iterations):
- Authentication and authorization
- Arq + Redis for persistent job queue
- Advanced error recovery (circuit breakers)
- Performance optimizations (caching, connection pooling)
- Monitoring and observability (Sentry integration)

---

## Implementation Strategy

1. **Follow TDD approach**: Tasks are ordered to implement infrastructure first, then services, then API endpoints
2. **Incremental delivery**: Each phase builds on previous, enabling early testing
3. **Parallel where possible**: 47 tasks marked [P] can run in parallel within their phases
4. **Independent testing**: Each user story phase has clear acceptance criteria for independent validation
5. **MVP-first**: All P1 stories implemented before any P2/P3 enhancements

---

## Task Validation Checklist

- ✅ All 89 tasks follow strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- ✅ All user story phase tasks have [US#] labels (US1-US5)
- ✅ All parallel tasks marked with [P]
- ✅ All tasks have specific file paths
- ✅ Dependencies clearly documented
- ✅ Acceptance criteria defined for each user story phase
- ✅ MVP scope clearly identified

---

**Tasks Ready for Execution** - Proceed with `/speckit.implement`
