# Data Model: Backend Implementation

**Feature**: 002-backend-implementation
**Date**: 2025-11-26
**Status**: Phase 1 Design

## Entity Relationship Diagram

```
┌─────────────────┐
│    Project      │
│─────────────────│
│ id (PK, UUID)   │◄──────┐
│ name            │       │
│ scale           │       │
│ language        │       │
│ domain          │       │
│ status          │       │
│ created_at      │       │
│ updated_at      │       │
└─────────────────┘       │
         ▲                │
         │                │
         │ 1              │
         │                │
         │ N              │
┌─────────────────────────┴─────┐
│        Variable               │
│───────────────────────────────│
│ id (PK, UUID)                 │◄──────┐
│ project_id (FK)               │       │
│ name                          │       │
│ type                          │       │
│ instructions                  │       │
│ classification_rules (JSONB)  │       │
│ order                         │       │
│ created_at                    │       │
│ updated_at                    │       │
└───────────────────────────────┘       │
         ▲                              │
         │                              │
         │ 1                            │
         │                              │
         │ N                            │
┌─────────────────────────────────────┬─┘
│            Prompt                   │
│─────────────────────────────────────│
│ id (PK, UUID)                       │
│ variable_id (FK)                    │
│ prompt_text                         │
│ model_config (JSONB)                │
│ version                             │
│ created_at                          │
└─────────────────────────────────────┘


┌─────────────────┐
│    Project      │
│─────────────────│
│ id (PK, UUID)   │◄──────┐
└─────────────────┘       │
         ▲                │
         │                │
         │ 1              │
         │                │
         │ N              │
┌─────────────────────────┴─────┐
│        Document               │
│───────────────────────────────│
│ id (PK, UUID)                 │
│ project_id (FK)               │
│ name                          │
│ content                       │
│ content_type                  │
│ size_bytes                    │
│ uploaded_at                   │
└───────────────────────────────┘


┌─────────────────┐
│    Project      │
│─────────────────│
│ id (PK, UUID)   │◄──────┐
└─────────────────┘       │
         ▲                │
         │ 1              │
         │                │
         │ N              │
┌─────────────────────────┴─────┐
│      ProcessingJob            │
│───────────────────────────────│
│ id (PK, UUID)                 │◄──────┐
│ project_id (FK)               │       │
│ job_type                      │       │
│ status                        │       │
│ document_ids (JSONB)          │       │
│ progress                      │       │
│ started_at                    │       │
│ completed_at                  │       │
└───────────────────────────────┘       │
         ▲                              │
         │                              │
         │ 1                            │
         │                              │
         │ N                            │
┌─────────────────────────────────────┬─┘
│          Extraction                 │
│─────────────────────────────────────│
│ id (PK, UUID)                       │
│ job_id (FK)                         │
│ document_id (FK)                    │
│ variable_id (FK)                    │
│ value                               │
│ confidence                          │
│ source_text                         │
│ created_at                          │
└─────────────────────────────────────┘
         ▲
         │
         │ 1
         │
         │ N
┌─────────────────────────────────────┐
│      ExtractionFeedback             │
│─────────────────────────────────────│
│ id (PK, UUID)                       │
│ extraction_id (FK)                  │
│ is_correct                          │
│ user_comment                        │
│ created_at                          │
└─────────────────────────────────────┘


┌─────────────────────────────────────┐
│      ProcessingJob                  │
│─────────────────────────────────────│
│ id (PK, UUID)                       │◄──────┐
└─────────────────────────────────────┘       │
         ▲                                    │
         │ 1                                  │
         │                                    │
         │ N                                  │
┌─────────────────────────────────────────────┴──┐
│          ProcessingLog                         │
│────────────────────────────────────────────────│
│ id (PK, UUID)                                  │
│ job_id (FK)                                    │
│ document_id (FK, nullable)                     │
│ variable_id (FK, nullable)                     │
│ log_level                                      │
│ message                                        │
│ created_at                                     │
└────────────────────────────────────────────────┘
```

---

## Entity Definitions

### 1. Project

Represents a research project with metadata and configuration.

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique project identifier |
| `name` | VARCHAR(255) | NOT NULL | Project name (user-defined) |
| `scale` | ENUM('SMALL', 'LARGE') | NOT NULL | Project scale |
| `language` | VARCHAR(50) | DEFAULT 'en' | Source document language (ISO 639-1) |
| `domain` | VARCHAR(255) | NULL | Domain context (e.g., "political science") |
| `status` | ENUM('CREATED', 'SCHEMA_DEFINED', 'SAMPLE_TESTING', 'READY', 'PROCESSING', 'COMPLETE', 'ERROR') | NOT NULL, DEFAULT 'CREATED' | Project workflow status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `status` (for filtering by status)
- Index on `created_at` (for sorting by recency)

**Validation Rules:**
- `name` must be 1-255 characters
- `language` must be valid ISO 639-1 code (or null)
- `status` transitions must follow workflow:
  ```
  CREATED → SCHEMA_DEFINED → SAMPLE_TESTING → READY → PROCESSING → COMPLETE
                                                                  → ERROR
  ```

**Relationships:**
- One-to-many with `Variable` (project has multiple variables)
- One-to-many with `Document` (project has multiple documents)
- One-to-many with `ProcessingJob` (project has multiple jobs)

---

### 2. Variable

Represents a single extraction variable defined by the user.

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique variable identifier |
| `project_id` | UUID | FK, NOT NULL | Reference to parent project |
| `name` | VARCHAR(255) | NOT NULL | Variable name (becomes column header) |
| `type` | ENUM('TEXT', 'NUMBER', 'DATE', 'CATEGORY', 'BOOLEAN') | NOT NULL | Variable data type |
| `instructions` | TEXT | NOT NULL | Natural language extraction instructions |
| `classification_rules` | JSONB | NULL | Classification categories/rules (for CATEGORY type) |
| `order` | INTEGER | NOT NULL | Display order in schema (1-indexed) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `project_id`
- Composite index on `(project_id, order)` (for ordered retrieval)

**Validation Rules:**
- `name` must be 1-255 characters, alphanumeric + underscores (valid Python identifier)
- `instructions` must be 10-5000 characters
- `classification_rules` required if `type = CATEGORY`, null otherwise
- `order` must be unique within project (enforced at application layer)

**Classification Rules Format (JSONB):**
```json
{
  "categories": ["protest", "riot", "demonstration"],
  "allow_multiple": false,
  "allow_other": true
}
```

**Relationships:**
- Many-to-one with `Project`
- One-to-many with `Prompt` (variable has multiple prompt versions)
- One-to-many with `Extraction` (variable has multiple extractions)

---

### 3. Prompt

Represents a generated LLM prompt for a variable (with versioning).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique prompt identifier |
| `variable_id` | UUID | FK, NOT NULL | Reference to parent variable |
| `prompt_text` | TEXT | NOT NULL | Full LLM prompt (with template variables filled) |
| `model_config` | JSONB | NOT NULL | LLM configuration (model, temperature, max_tokens) |
| `version` | INTEGER | NOT NULL | Prompt version (1-indexed) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `variable_id`
- Composite index on `(variable_id, version)` (for version retrieval)

**Validation Rules:**
- `prompt_text` must be 50-10000 characters
- `version` must be unique within variable (enforced at application layer)
- `version` auto-increments (1, 2, 3, ...) on each update

**Model Config Format (JSONB):**
```json
{
  "model": "gpt-4",
  "temperature": 0.2,
  "max_tokens": 1000,
  "top_p": 1.0
}
```

**Relationships:**
- Many-to-one with `Variable`

---

### 4. Document

Represents an uploaded document to be processed.

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique document identifier |
| `project_id` | UUID | FK, NOT NULL | Reference to parent project |
| `name` | VARCHAR(500) | NOT NULL | Original filename |
| `content` | TEXT | NOT NULL | Extracted document text |
| `content_type` | ENUM('PDF', 'DOCX', 'TXT', 'CSV', 'JSON', 'PARQUET') | NOT NULL | Document file type (all common formats supported) |
| `size_bytes` | INTEGER | NOT NULL | File size in bytes |
| `uploaded_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Upload timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `project_id`
- Index on `uploaded_at` (for sorting by recency)

**Validation Rules:**
- `name` must be 1-500 characters
- `content` must be non-empty (extracted during upload)
- `size_bytes` max 10MB (enforced at API layer)

**Relationships:**
- Many-to-one with `Project`
- One-to-many with `Extraction` (document has multiple extractions)

---

### 5. ProcessingJob

Represents a batch processing job (sample or full).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique job identifier |
| `project_id` | UUID | FK, NOT NULL | Reference to parent project |
| `job_type` | ENUM('SAMPLE', 'FULL') | NOT NULL | Job type |
| `status` | ENUM('PENDING', 'PROCESSING', 'COMPLETE', 'FAILED', 'CANCELLED') | NOT NULL, DEFAULT 'PENDING' | Job status |
| `document_ids` | JSONB | NOT NULL | List of document IDs to process |
| `progress` | INTEGER | NOT NULL, DEFAULT 0 | Progress percentage (0-100) |
| `started_at` | TIMESTAMP | NULL | Job start timestamp |
| `completed_at` | TIMESTAMP | NULL | Job completion timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `project_id`
- Index on `status` (for filtering active jobs)

**Validation Rules:**
- `document_ids` must be non-empty array
- `progress` must be 0-100
- `status` transitions:
  ```
  PENDING → PROCESSING → COMPLETE
                      → FAILED
                      → CANCELLED (manual cancellation)
  ```

**Document IDs Format (JSONB):**
```json
["doc-uuid-1", "doc-uuid-2", "doc-uuid-3"]
```

**Relationships:**
- Many-to-one with `Project`
- One-to-many with `Extraction` (job has multiple extractions)
- One-to-many with `ProcessingLog` (job has multiple log entries)

---

### 6. Extraction

Represents a single extracted value from a document for a variable.

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique extraction identifier |
| `job_id` | UUID | FK, NOT NULL | Reference to parent job |
| `document_id` | UUID | FK, NOT NULL | Reference to source document |
| `variable_id` | UUID | FK, NOT NULL | Reference to variable definition |
| `value` | TEXT | NULL | Extracted value (null if extraction failed) |
| `confidence` | FLOAT | NULL, CHECK (0.0 <= confidence <= 1.0) | Confidence score (0.0-1.0) |
| `source_text` | TEXT | NULL | Document excerpt that generated extraction |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `job_id`
- Foreign key on `document_id`
- Foreign key on `variable_id`
- Composite index on `(document_id, variable_id)` (for dataset queries)
- Index on `confidence` (for filtering by confidence threshold)

**Validation Rules:**
- `value` can be null only if extraction failed (logged in `ProcessingLog`)
- `confidence` must be 0.0-1.0 if present
- `source_text` max 2000 characters (truncate if longer)

**Relationships:**
- Many-to-one with `ProcessingJob`
- Many-to-one with `Document`
- Many-to-one with `Variable`
- One-to-many with `ExtractionFeedback` (extraction has multiple feedback entries)

---

### 7. ExtractionFeedback

Represents user feedback on extraction quality (for prompt refinement).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique feedback identifier |
| `extraction_id` | UUID | FK, NOT NULL | Reference to extraction |
| `is_correct` | BOOLEAN | NOT NULL | Whether extraction is correct |
| `user_comment` | TEXT | NULL | Optional user comment (what's wrong) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Feedback timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `extraction_id`

**Validation Rules:**
- `user_comment` max 1000 characters

**Relationships:**
- Many-to-one with `Extraction`

---

### 8. ProcessingLog

Represents a log entry for processing events (debugging, error tracking).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique log identifier |
| `job_id` | UUID | FK, NOT NULL | Reference to parent job |
| `document_id` | UUID | FK, NULL | Reference to document (if applicable) |
| `variable_id` | UUID | FK, NULL | Reference to variable (if applicable) |
| `log_level` | ENUM('INFO', 'WARNING', 'ERROR') | NOT NULL | Log severity |
| `message` | TEXT | NOT NULL | Log message |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Log timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key on `job_id`
- Composite index on `(job_id, created_at)` (for chronological retrieval)

**Validation Rules:**
- `message` must be non-empty

**Relationships:**
- Many-to-one with `ProcessingJob`

---

## Data Flow

### 1. Project Creation → Schema Definition

```
Frontend POST /api/projects → Backend creates Project (status=CREATED)
Frontend POST /api/projects/{id}/variables → Backend creates Variable + Prompt (v1)
Project status updated to SCHEMA_DEFINED
```

### 2. Sample Processing

```
Frontend POST /api/projects/{id}/jobs (type=SAMPLE, document_ids=[...])
→ Backend creates ProcessingJob (status=PENDING)
→ Background worker picks up job (status=PROCESSING)
→ For each (document, variable):
    → Call LLM with Prompt.prompt_text
    → Parse response → Create Extraction
    → Log to ProcessingLog
→ Job status updated to COMPLETE
Frontend polls GET /api/jobs/{id} for progress updates
```

### 3. Feedback Loop → Prompt Refinement

```
Frontend sends feedback on extraction (POST /api/extractions/{id}/feedback)
→ Backend creates ExtractionFeedback
→ Analyze feedback (identify common errors)
→ Update Variable.instructions
→ Generate new Prompt (version++, new prompt_text)
Frontend re-runs sample with updated prompt
```

### 4. Full Processing → Export

```
Frontend POST /api/projects/{id}/jobs (type=FULL, document_ids=[all])
→ Same flow as sample processing, but all documents
Frontend POST /api/projects/{id}/export (format=CSV_WIDE, include_confidence=true)
→ Backend queries all Extractions for project
→ Aggregate into pandas DataFrame
→ Pivot to wide format
→ Generate CSV
→ Return file download URL
```

---

## State Transitions

### Project Status State Machine

```
CREATED
  ↓ (user defines first variable)
SCHEMA_DEFINED
  ↓ (user starts sample processing)
SAMPLE_TESTING
  ↓ (user approves sample results)
READY
  ↓ (user starts full processing)
PROCESSING
  ↓ (all documents processed successfully)
COMPLETE
  ↓ (error during processing)
ERROR ──→ can retry from PROCESSING
```

### ProcessingJob Status State Machine

```
PENDING
  ↓ (worker picks up job)
PROCESSING
  ↓ (all extractions complete)
COMPLETE
  ↓ (error during processing)
FAILED
  ↓ (user cancels job)
CANCELLED (terminal state)
```

---

## Database Schema SQL (PostgreSQL)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enums
CREATE TYPE project_scale AS ENUM ('SMALL', 'LARGE');
CREATE TYPE project_status AS ENUM ('CREATED', 'SCHEMA_DEFINED', 'SAMPLE_TESTING', 'READY', 'PROCESSING', 'COMPLETE', 'ERROR');
CREATE TYPE variable_type AS ENUM ('TEXT', 'NUMBER', 'DATE', 'CATEGORY', 'BOOLEAN');
CREATE TYPE content_type AS ENUM ('PDF', 'DOCX', 'TXT', 'CSV', 'JSON', 'PARQUET');
CREATE TYPE job_type AS ENUM ('SAMPLE', 'FULL');
CREATE TYPE job_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETE', 'FAILED', 'CANCELLED');
CREATE TYPE log_level AS ENUM ('INFO', 'WARNING', 'ERROR');

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    scale project_scale NOT NULL,
    language VARCHAR(50) DEFAULT 'en',
    domain VARCHAR(255),
    status project_status NOT NULL DEFAULT 'CREATED',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at);

-- Variables table
CREATE TABLE variables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type variable_type NOT NULL,
    instructions TEXT NOT NULL,
    classification_rules JSONB,
    "order" INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_variables_project_id ON variables(project_id);
CREATE INDEX idx_variables_project_order ON variables(project_id, "order");

-- Prompts table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    variable_id UUID NOT NULL REFERENCES variables(id) ON DELETE CASCADE,
    prompt_text TEXT NOT NULL,
    model_config JSONB NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_prompts_variable_id ON prompts(variable_id);
CREATE INDEX idx_prompts_variable_version ON prompts(variable_id, version);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_type content_type NOT NULL,
    size_bytes INTEGER NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_project_id ON documents(project_id);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at);

-- Processing Jobs table
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    job_type job_type NOT NULL,
    status job_status NOT NULL DEFAULT 'PENDING',
    document_ids JSONB NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_jobs_project_id ON processing_jobs(project_id);
CREATE INDEX idx_jobs_status ON processing_jobs(status);

-- Extractions table
CREATE TABLE extractions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    variable_id UUID NOT NULL REFERENCES variables(id) ON DELETE CASCADE,
    value TEXT,
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0),
    source_text TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_extractions_job_id ON extractions(job_id);
CREATE INDEX idx_extractions_document_id ON extractions(document_id);
CREATE INDEX idx_extractions_variable_id ON extractions(variable_id);
CREATE INDEX idx_extractions_doc_var ON extractions(document_id, variable_id);
CREATE INDEX idx_extractions_confidence ON extractions(confidence);

-- Extraction Feedback table
CREATE TABLE extraction_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    extraction_id UUID NOT NULL REFERENCES extractions(id) ON DELETE CASCADE,
    is_correct BOOLEAN NOT NULL,
    user_comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_extraction_id ON extraction_feedback(extraction_id);

-- Processing Logs table
CREATE TABLE processing_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    variable_id UUID REFERENCES variables(id) ON DELETE SET NULL,
    log_level log_level NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_logs_job_id ON processing_logs(job_id);
CREATE INDEX idx_logs_job_created ON processing_logs(job_id, created_at);
```

---

---

## Pipeline Architecture Notes

**Updated 2026-02-09**: Data model aligned with pipeline architecture from [ai_agent_reference.md](/ai_agent_reference.md):

- **Document content_type** expanded to support all common formats (PDF, DOCX, TXT, CSV, JSON, Parquet)
- **Prompt** records are auto-generated from Variable + Project context (not manually created)
- **LLM calls** go through LangChain for multi-provider abstraction
- **Export** produces CSV + Excel with filtering, codebook, and quality metrics
- **Deferred (v2)**: Duplicate detection columns (`is_duplicate`, `duplicate_record_ids`, `merged_to`) not included in v1

---

**Phase 1 Design Complete**: Data model defined with entity relationships, validation rules, and database schema.
