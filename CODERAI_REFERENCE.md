# CoderAI: Production Reference Document

## Overview

CoderAI is a multi-tenant SaaS platform that transforms unstructured documents into structured datasets using LLM-powered extraction. Users upload document corpora, define extraction variables through an AI-assisted wizard, iterate on a sample, then run full extraction and export results.

**Core value proposition**: Researchers and analysts can convert qualitative text (news articles, reports, contracts) into quantitative datasets without manual coding or requiring native language speakers.

---

## 1. Product Vision

### 1.1 Target Users
- Academic researchers analyzing large document corpora
- Analysts processing multilingual content
- Anyone needing structured data from unstructured text

### 1.2 Core Workflow
```
Upload Documents → Define Variables (AI-assisted) → Sample Run → Review & Refine → Full Run → Export
```

### 1.3 Key Differentiators
- **AI co-pilot throughout**: Agent suggests variables, refines prompts based on feedback
- **Sample-first iteration**: Test on N documents before committing to full corpus
- **User-defined unit of observation**: Document-level or entity-level extraction
- **Multilingual**: No native speaker required

---

## 2. Architecture Overview

### 2.1 High-Level Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                  │
│                     React + TypeScript                              │
│    Project Wizard │ Variable Builder │ Review UI │ Export           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           API LAYER                                 │
│                     FastAPI (async)                                 │
│         REST Endpoints │ WebSocket (job status) │ Auth              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│      JOB QUEUE           │    │      DATABASE            │
│   Redis + ARQ Workers    │    │   PostgreSQL + RLS       │
│                          │    │                          │
│  • Document processing   │    │  • Projects, Variables   │
│  • LLM extraction        │    │  • Documents, Extractions│
│  • Prompt refinement     │    │  • Jobs, Feedback        │
└──────────────────────────┘    └──────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        LLM LAYER                                    │
│              LangChain (OpenAI primary, multi-provider ready)       │
│                                                                     │
│   Co-pilot Agent │ Extraction Assistants │ Prompt Refinement        │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| API Framework | FastAPI (async) | Native async, automatic OpenAPI docs, Pydantic validation |
| Database | PostgreSQL | JSONB for flexible schemas, RLS for multi-tenancy |
| ORM | SQLAlchemy 2.0 async | Industry standard, Alembic migrations |
| Job Queue | ARQ + Redis | Async-native (matches FastAPI), lightweight, fast |
| LLM Framework | LangChain 0.3+ | Multi-provider abstraction, structured output parsing |
| Real-time Updates | WebSocket or SSE | Job progress without polling |
| Multi-tenancy | Row-Level Security | Database-enforced isolation, defense in depth |
| Frontend | React + TypeScript | Component reusability, type safety |

### 2.3 Repository Structure

```
coderai/
├── backend/
│   ├── app/
│   │   ├── api/                    # FastAPI routes
│   │   │   ├── routes/
│   │   │   │   ├── projects.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── variables.py
│   │   │   │   ├── jobs.py
│   │   │   │   └── export.py
│   │   │   └── deps.py             # Dependencies (auth, db session, tenant)
│   │   │
│   │   ├── core/                   # Configuration, security
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── db/                     # Database layer
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── session.py          # Async session factory
│   │   │   └── rls.py              # Row-level security setup
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── document_processor.py
│   │   │   ├── extraction_service.py
│   │   │   ├── prompt_generator.py
│   │   │   ├── feedback_analyzer.py
│   │   │   └── export_service.py
│   │   │
│   │   ├── agents/                 # LLM agent logic
│   │   │   ├── copilot.py          # Setup assistant
│   │   │   ├── extractor.py        # Extraction assistants
│   │   │   └── refiner.py          # Prompt refinement
│   │   │
│   │   ├── workers/                # ARQ background tasks
│   │   │   ├── tasks.py
│   │   │   └── worker_settings.py
│   │   │
│   │   └── main.py                 # FastAPI app entry
│   │
│   ├── migrations/                 # Alembic
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/               # API clients
│   │   └── types/
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## 3. Data Model

### 3.1 Core Entities

**User**
- id (UUID, PK)
- email (unique)
- hashed_password
- created_at, updated_at

**Project**
- id (UUID, PK)
- user_id (FK → User, indexed)
- name
- description
- domain (e.g., "news articles", "legal contracts")
- language (e.g., "Arabic", "English", "Mixed")
- unit_of_observation (ENUM: DOCUMENT, ENTITY)
- entity_identification_pattern (nullable, for ENTITY type)
- status (ENUM: CREATED, SCHEMA_DEFINED, SAMPLE_COMPLETE, PROCESSING, COMPLETE)
- created_at, updated_at

**Variable**
- id (UUID, PK)
- project_id (FK → Project)
- name (column name in export)
- display_name
- type (ENUM: TEXT, NUMBER, DATE, CATEGORY, BOOLEAN)
- instructions (natural language extraction instructions)
- classification_rules (JSONB, for CATEGORY type)
- confidence_threshold (float, default 0.7)
- if_uncertain (ENUM: NULL, SKIP, FLAG)
- if_multiple_values (ENUM: FIRST, LAST, ALL, SUMMARIZE)
- max_values (int, for wide-format export, e.g., 3 → col_1, col_2, col_3)
- default_value (nullable)
- validation_rules (JSONB: min, max, pattern, allowed_values)
- depends_on (JSONB: conditional logic referencing other variables)
- order (int, for display/processing sequence)
- created_at, updated_at

**Prompt** (versioned, auto-generated)
- id (UUID, PK)
- variable_id (FK → Variable)
- version (int)
- system_prompt (text)
- model (e.g., "gpt-4o")
- temperature (float)
- max_tokens (int)
- response_schema (JSONB)
- is_active (bool)
- created_at

**Document**
- id (UUID, PK)
- project_id (FK → Project)
- filename
- content_type (MIME)
- raw_text (extracted text)
- chunk_count (int, if chunked)
- word_count (int)
- status (ENUM: UPLOADED, PARSED, READY, FAILED)
- error_message (nullable)
- created_at

**DocumentChunk** (for large documents)
- id (UUID, PK)
- document_id (FK → Document)
- chunk_index (int)
- text (chunk content)
- token_count (int)
- overlap_previous (int, tokens overlapping with previous chunk)

**ProcessingJob**
- id (UUID, PK)
- project_id (FK → Project)
- type (ENUM: SAMPLE, FULL)
- status (ENUM: PENDING, RUNNING, PAUSED, COMPLETED, FAILED)
- document_ids (UUID[], documents to process)
- progress (int, 0-100)
- documents_processed (int)
- documents_failed (int)
- consecutive_failures (int)
- started_at, completed_at
- created_at

**Extraction** (one per document × variable, or per entity × variable)
- id (UUID, PK)
- job_id (FK → ProcessingJob)
- document_id (FK → Document)
- variable_id (FK → Variable)
- entity_index (int, nullable, for entity-level extraction)
- entity_text (text, nullable, the identified entity)
- value (JSONB, supports multi-value)
- confidence (float, 0.0-1.0)
- source_text (text, excerpt used for extraction)
- prompt_version (int)
- status (ENUM: EXTRACTED, VALIDATED, FLAGGED, FAILED)
- error_message (nullable)
- created_at

**ExtractionFeedback**
- id (UUID, PK)
- extraction_id (FK → Extraction)
- feedback_type (ENUM: CORRECT, INCORRECT, PARTIALLY_CORRECT)
- corrected_value (JSONB, nullable)
- user_note (text, nullable)
- created_at

**ProcessingLog** (audit trail)
- id (UUID, PK)
- job_id (FK → ProcessingJob)
- document_id (FK → Document, nullable)
- event_type (ENUM: JOB_STARTED, DOC_STARTED, DOC_COMPLETED, DOC_FAILED, JOB_COMPLETED, etc.)
- message (text)
- metadata (JSONB)
- created_at

### 3.2 Row-Level Security

All tenant-scoped tables include `user_id` (directly or via FK chain). PostgreSQL RLS policies enforce isolation:

```sql
-- Example policy on projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON projects
    USING (user_id = current_setting('app.current_user_id')::uuid);
```

The API layer sets `app.current_user_id` at the start of each request via SQLAlchemy event listener.

---

## 4. Pipeline Stages

### 4.1 Document Ingestion

**Supported formats (v1)**: PDF, DOCX, TXT, HTML

**Processing flow**:
1. User uploads file(s)
2. System detects format, extracts raw text
3. Text is cleaned (normalize whitespace, remove headers/footers for PDFs)
4. Word count calculated
5. If > threshold (e.g., 5000 words or 10 pages), document is chunked
6. Status set to READY

**Chunking strategy**:
- Use semantic chunking (respect paragraph/section boundaries)
- Target chunk size: 2000-3000 tokens
- Overlap: 200-300 tokens (10-15%)
- Store chunks in DocumentChunk table
- For extraction, process all chunks and merge results (deduplicate entities)

**Libraries**:
- PDF: PyMuPDF (fast, handles most cases)
- DOCX: python-docx
- HTML: BeautifulSoup
- Chunking: LangChain RecursiveCharacterTextSplitter or custom semantic splitter

### 4.2 Variable Definition (AI Co-pilot)

The co-pilot agent assists users in defining their extraction schema.

**Co-pilot capabilities**:
1. **Suggest variables**: Based on document type and domain, propose relevant variables
2. **Refine instructions**: Improve user-written instructions for clarity
3. **Suggest classification rules**: For CATEGORY variables, propose categories based on sample content
4. **Validate dependencies**: Check that conditional logic is consistent

**Conversation pattern**:
```
User: I'm analyzing news articles about protests in the Middle East
Co-pilot: Based on your domain, I suggest these variables:
  - event_date (DATE): When the protest occurred
  - location (TEXT): City and country
  - participant_count (NUMBER): Estimated number of participants
  - event_type (CATEGORY): Type of collective action
  - actors (TEXT): Organizations or groups involved

Would you like me to add these, or would you prefer to define your own?
```

**Co-pilot is guided, not autonomous**: It suggests, user decides. New prompt versions only saved when user explicitly confirms.

### 4.3 Extraction Stage

**For document-level extraction**:
1. Load document text (or iterate through chunks)
2. For each variable, call the auto-generated extraction assistant
3. Merge results into single extraction record per document

**For entity-level extraction**:
1. Run entity identification assistant first (identify distinct entities per document)
2. For each identified entity, run variable extraction assistants
3. Store one extraction record per entity × variable

**Extraction assistant prompt structure**:
```
SYSTEM:
You are extracting structured data from {document_type} documents
in the {domain} domain, written in {language}.

Unit of observation: {unit_description}

Extract: {variable_name} (type: {variable_type})
Instructions: {user_instructions}

{conditional_logic if depends_on}

Rules:
- Return null if information is not explicitly stated
- Do not infer or fabricate
- Include confidence score (0.0-1.0)
- Include source text excerpt (max 200 chars)

{classification_rules if CATEGORY}

Output JSON schema:
{response_schema}
```

**Model parameters by variable type**:
| Type | Temperature | Rationale |
|------|-------------|-----------|
| BOOLEAN | 0.1 | Binary, needs consistency |
| CATEGORY | 0.1 | Must match predefined categories |
| DATE | 0.15 | Structured but some interpretation |
| NUMBER | 0.15 | Structured but some interpretation |
| TEXT | 0.2 | More flexibility for summarization |

### 4.4 Post-Processing

Deterministic transformations after LLM extraction:

1. **Type coercion**: Ensure NUMBER is numeric, DATE is ISO 8601, etc.
2. **Validation**: Apply user-defined rules (min/max, regex, allowed values)
3. **Default values**: Populate if null and default specified
4. **Confidence check**: Flag if below threshold
5. **Multi-value handling**: Apply strategy (first, all, summarize)

### 4.5 Storage

Atomic per-document transaction:
- All extractions for a document saved together
- If any extraction fails validation, document marked as FAILED
- Job progress updated after each document
- Commit after each document (enables resumability)

---

## 5. Background Job System

### 5.1 Why ARQ over Celery

- **Async-native**: FastAPI is async, ARQ is async — no bridging
- **Lightweight**: Simpler setup, fewer moving parts
- **Performance**: 7x faster than RQ for I/O-bound tasks
- **Redis-backed**: Already using Redis, no additional infrastructure

### 5.2 Job Types

**extraction_job**: Process documents for a project
- Input: job_id
- Behavior: Iterate documents, extract all variables, update progress
- Failure handling: Log error, mark document as FAILED, continue (up to N consecutive failures)

**prompt_refinement_job**: Analyze feedback and update prompts
- Input: variable_id, feedback_ids
- Behavior: Analyze patterns, generate improved prompt, save as new version

**export_job**: Generate CSV/Excel files
- Input: project_id, format, options
- Behavior: Aggregate extractions, generate file, store in object storage

### 5.3 Job Lifecycle

```
PENDING → RUNNING → COMPLETED
                  ↘ FAILED
          ↓
        PAUSED (user-initiated or N consecutive failures)
```

**Resumability**:
- Jobs can be paused and resumed
- On resume, skip already-processed documents
- Track `documents_processed` and `consecutive_failures`

### 5.4 Worker Configuration

```python
class WorkerSettings:
    functions = [extraction_job, prompt_refinement_job, export_job]
    redis_settings = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)
    max_jobs = 10  # Concurrent jobs per worker
    job_timeout = 3600  # 1 hour max per job
    keep_result = 3600  # Keep results for 1 hour
    retry_jobs = True
    max_tries = 3
```

### 5.5 Rate Limiting & Cost Control

- **Per-project token budget**: Track tokens used, pause job if budget exceeded
- **LLM call rate limiting**: Max N requests/minute to avoid API throttling
- **Queue throttling**: If queue depth > threshold, reject new jobs with 429

---

## 6. AI Agent Architecture

### 6.1 Agent Types

**Co-pilot Agent** (setup assistant)
- Helps define project context
- Suggests variables based on document type and domain
- Refines variable instructions
- Explains tradeoffs (precision vs recall, etc.)

**Extraction Assistants** (per-variable)
- Auto-generated from variable definition
- Stateless, single-purpose
- Versioned prompts

**Refinement Agent** (prompt improvement)
- Analyzes feedback patterns
- Suggests prompt modifications
- User approves changes

### 6.2 Agent Conversation State

Co-pilot conversations are **stateful within a session**:
- Store conversation history in session (Redis or DB)
- Context includes: project metadata, current variables, sample documents
- Clear on session end or explicit reset

Extraction assistants are **stateless**:
- Each call is independent
- Full context passed in each request

### 6.3 Prompt Refinement Loop

```
User flags extraction as incorrect
       ↓
User optionally provides correction + note
       ↓
System queues refinement job
       ↓
Refinement agent analyzes:
  - What was extracted vs what was expected
  - User note (if provided)
  - Pattern across multiple feedback items
       ↓
Agent suggests prompt changes (2-3 options)
       ↓
User selects preferred option
       ↓
New prompt version created (is_active = true)
       ↓
Optional: Re-run sample with new prompt
```

---

## 7. API Design

### 7.1 Core Endpoints

**Projects**
- `POST /projects` - Create project
- `GET /projects` - List user's projects
- `GET /projects/{id}` - Get project details
- `PATCH /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

**Documents**
- `POST /projects/{id}/documents` - Upload documents (multipart)
- `GET /projects/{id}/documents` - List documents
- `GET /documents/{id}` - Get document details + text
- `DELETE /documents/{id}` - Delete document

**Variables**
- `POST /projects/{id}/variables` - Create variable
- `GET /projects/{id}/variables` - List variables
- `PATCH /variables/{id}` - Update variable
- `DELETE /variables/{id}` - Delete variable
- `POST /variables/{id}/generate-prompt` - Regenerate prompt

**Jobs**
- `POST /projects/{id}/jobs` - Start extraction job (sample or full)
- `GET /jobs/{id}` - Get job status + progress
- `POST /jobs/{id}/pause` - Pause job
- `POST /jobs/{id}/resume` - Resume job
- `DELETE /jobs/{id}` - Cancel job

**Extractions**
- `GET /projects/{id}/extractions` - List extractions (paginated, filterable)
- `GET /extractions/{id}` - Get single extraction
- `POST /extractions/{id}/feedback` - Submit feedback

**Export**
- `POST /projects/{id}/export` - Start export job
- `GET /exports/{id}` - Get export status + download URL

**Co-pilot**
- `POST /projects/{id}/copilot/message` - Send message to co-pilot
- `POST /copilot/suggest-variables` - Get variable suggestions

### 7.2 Real-time Updates

**WebSocket endpoint**: `/ws/jobs/{job_id}`

Events:
- `progress`: `{ "documents_processed": 10, "total": 100, "percent": 10 }`
- `document_completed`: `{ "document_id": "...", "extractions": [...] }`
- `document_failed`: `{ "document_id": "...", "error": "..." }`
- `job_completed`: `{ "status": "COMPLETED", "summary": {...} }`
- `job_failed`: `{ "status": "FAILED", "error": "..." }`

---

## 8. Error Handling & Resilience

### 8.1 LLM Call Resilience

**Retry strategy** (via tenacity):
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Max retries: 5
- Retry on: rate limits (429), server errors (5xx), timeouts
- Don't retry on: invalid request (4xx), context too long

**Circuit breaker**:
- Open after 5 consecutive failures
- Half-open after 30 seconds
- Close after 3 successes
- When open, fail fast with user-friendly error

### 8.2 Job Failure Handling

**Per-document failure**:
- Log error with full context
- Mark document as FAILED
- Increment `consecutive_failures`
- Continue to next document

**Job-level failure**:
- If `consecutive_failures` > 10, pause job
- Alert user via notification
- Provide option to: resume, skip failed, abort

### 8.3 Data Integrity

- All database writes in transactions
- Idempotent job processing (reprocessing same document overwrites, doesn't duplicate)
- Soft deletes for audit trail (optional)

---

## 9. Observability

### 9.1 Logging

**Structured JSON logging** with fields:
- `timestamp`, `level`, `message`
- `correlation_id` (per-request)
- `job_id`, `document_id`, `variable_id` (when applicable)
- `user_id`, `project_id`
- `duration_ms` (for operations)

### 9.2 Metrics (Prometheus)

- `coderai_documents_processed_total` (counter, labels: status)
- `coderai_extractions_total` (counter, labels: variable_type, status)
- `coderai_llm_calls_total` (counter, labels: model, status)
- `coderai_llm_call_duration_seconds` (histogram)
- `coderai_llm_tokens_used_total` (counter, labels: model, type)
- `coderai_job_queue_depth` (gauge)
- `coderai_extraction_confidence` (histogram)

### 9.3 Tracing

OpenTelemetry integration for:
- Request → Service → LLM call → Database chain
- Job execution traces
- Cross-service correlation

---

## 10. Security

### 10.1 Authentication

- JWT-based authentication
- Access tokens (short-lived, 15 min)
- Refresh tokens (long-lived, 7 days)
- Token stored in httpOnly cookie or Authorization header

### 10.2 Multi-tenancy Isolation

- Row-Level Security at database level
- API middleware sets tenant context
- Service layer never sees other tenants' data

### 10.3 Prompt Injection Prevention

User-defined instructions are sandboxed:
- Wrapped in clear delimiters
- System prompt explicitly instructs LLM to treat user content as data, not instructions
- Output validation (must match expected schema)

### 10.4 Secrets Management

- Environment variables for development
- AWS Secrets Manager or HashiCorp Vault for production
- API keys rotated regularly
- Audit log for key access

---

## 11. Export

### 11.1 Formats

- **CSV**: Standard, universal
- **Excel (.xlsx)**: With formatting, multiple sheets

### 11.2 Output Modes

**Wide format** (default):
- One row per unit of observation
- Columns: document_id, [variables], metadata

**Long format** (optional):
- One row per extraction
- Columns: document_id, variable_name, value, confidence, source_text

### 11.3 Multi-value Handling in Export

If variable allows multiple values and user chose ALL:
- Wide format: `variable_1`, `variable_2`, `variable_3` (up to max_values)
- Long format: Multiple rows

### 11.4 Metadata Columns (optional)

- `_confidence_{variable}`: Confidence score
- `_source_{variable}`: Source text excerpt
- `_prompt_version_{variable}`: Prompt version used

### 11.5 Codebook Export

Separate file with:
- Variable definitions
- Classification rules
- Quality metrics (avg confidence, % flagged, % null)

---

## 12. Deployment

### 12.1 Container Architecture

```yaml
services:
  api:
    image: coderai-api
    replicas: 2
    resources:
      limits: { cpu: "1", memory: "1Gi" }
    
  worker:
    image: coderai-worker
    replicas: 3  # Scale based on queue depth
    resources:
      limits: { cpu: "0.5", memory: "512Mi" }
    
  redis:
    image: redis:7-alpine
    
  postgres:
    image: postgres:16
```

### 12.2 Scaling Strategy

- **API**: Scale on CPU/request count
- **Workers**: Scale on queue depth (job latency)
- **Database**: Vertical scaling, read replicas for export queries

### 12.3 Health Checks

- `/health/live`: Process is running
- `/health/ready`: Database connected, Redis connected, LLM provider reachable

### 12.4 Graceful Shutdown

- Stop accepting new jobs
- Wait for in-progress extractions to complete (up to timeout)
- Checkpoint job progress
- Exit

---

## 13. Development Phases

### Phase 1: Foundation (MVP)
- [ ] Project CRUD
- [ ] Document upload + parsing (PDF, TXT)
- [ ] Variable definition (manual)
- [ ] Basic extraction pipeline (sequential)
- [ ] Export to CSV
- [ ] Single-user (no auth)

### Phase 2: Core Features
- [ ] Authentication + multi-tenancy
- [ ] Entity-level extraction
- [ ] Sample → Feedback → Full run workflow
- [ ] Job queue with ARQ
- [ ] Real-time progress (WebSocket)
- [ ] Excel export with codebook

### Phase 3: AI Co-pilot
- [ ] Variable suggestion
- [ ] Prompt refinement from feedback
- [ ] Guided setup wizard

### Phase 4: Scale & Polish
- [ ] Document chunking for large files
- [ ] Parallel processing
- [ ] Observability (metrics, tracing)
- [ ] Rate limiting + cost controls
- [ ] DOCX, HTML format support

### Phase 5: Advanced (v2)
- [ ] Duplicate detection
- [ ] External API enrichment (geocoding, etc.)
- [ ] Multi-model support
- [ ] Team collaboration

---

## 14. Constraints & Principles

1. **User-configurable**: No hardcoded schemas. Every project defines its own extraction logic.

2. **AI-assisted, human-controlled**: Agent suggests, user decides. No autonomous prompt changes.

3. **Sample-first**: Always validate on sample before full corpus.

4. **Atomic transactions**: All extractions for a document saved together or not at all.

5. **Resumable jobs**: Processing can pause and resume without data loss.

6. **Fail gracefully**: Individual document failures don't stop the pipeline.

7. **No fabrication**: LLM must only extract explicitly stated information.

8. **Low temperature**: Extraction uses temperature 0.1-0.2 for consistency.

9. **Idempotent**: Reprocessing produces same result (overwrites, not duplicates).

10. **Observable**: Every operation logged with correlation IDs.

---

## 15. Appendix: Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/coderai

# Redis
REDIS_URL=redis://localhost:6379

# LLM
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
LLM_MAX_RETRIES=5

# Auth
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# App
ENVIRONMENT=development|staging|production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000

# Limits
MAX_DOCUMENTS_PER_PROJECT=10000
MAX_FILE_SIZE_MB=50
LLM_RATE_LIMIT_PER_MINUTE=60
DEFAULT_TOKEN_BUDGET_PER_PROJECT=1000000
```

---

## 16. Appendix: Glossary

| Term | Definition |
|------|------------|
| **Unit of observation** | What each row represents in the final dataset (document or entity) |
| **Variable** | A single field to extract (column in output) |
| **Extraction** | One extracted value for a document × variable pair |
| **Prompt version** | A specific version of the auto-generated LLM prompt |
| **Sample run** | Extraction on a subset of documents for validation |
| **Full run** | Extraction on all documents in project |
| **Co-pilot** | AI assistant that helps define project and variables |
| **Chunking** | Splitting large documents into smaller pieces for processing |

---

*Document version: 1.0*
*Last updated: February 2026*
