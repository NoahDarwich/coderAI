# Data Model: Backend Implementation

**Feature**: 002-backend-implementation
**Date**: 2025-11-26
**Updated**: 2026-02-10
**Source of Truth**: [CODERAI_REFERENCE.md](/CODERAI_REFERENCE.md) Section 3

---

## Entity Relationship Overview

```
User 1──N Project 1──N Variable 1──N Prompt
                   1──N Document 1──N DocumentChunk
                   1──N ProcessingJob 1──N Extraction 1──N ExtractionFeedback
                                     1──N ProcessingLog
```

---

## Core Entities

### 1. User

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique user identifier |
| `email` | VARCHAR | UNIQUE, NOT NULL | User email |
| `hashed_password` | VARCHAR | NOT NULL | Bcrypt hashed password |
| `created_at` | TIMESTAMP | NOT NULL | Registration timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

### 2. Project

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique project identifier |
| `user_id` | UUID | FK → User, indexed | Owner |
| `name` | VARCHAR(255) | NOT NULL | Project name |
| `description` | TEXT | NULL | Project description |
| `domain` | VARCHAR(255) | NULL | Domain context (e.g., "news articles") |
| `language` | VARCHAR(50) | DEFAULT 'English' | Document language |
| `unit_of_observation` | ENUM | NOT NULL | DOCUMENT or ENTITY |
| `entity_identification_pattern` | TEXT | NULL | For ENTITY type |
| `status` | ENUM | NOT NULL, DEFAULT 'CREATED' | Workflow status |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

**Status enum**: CREATED, SCHEMA_DEFINED, SAMPLE_COMPLETE, PROCESSING, COMPLETE

**RLS**: Filtered by `user_id = current_setting('app.current_user_id')::uuid`

### 3. Variable

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique variable identifier |
| `project_id` | UUID | FK → Project | Parent project |
| `name` | VARCHAR(255) | NOT NULL | Column name in export |
| `display_name` | VARCHAR(255) | NULL | Human-readable name |
| `type` | ENUM | NOT NULL | TEXT, NUMBER, DATE, CATEGORY, BOOLEAN |
| `instructions` | TEXT | NOT NULL | Natural language extraction instructions |
| `classification_rules` | JSONB | NULL | Categories/rules for CATEGORY type |
| `confidence_threshold` | FLOAT | DEFAULT 0.7 | Minimum confidence to accept |
| `if_uncertain` | ENUM | DEFAULT 'FLAG' | NULL, SKIP, FLAG |
| `if_multiple_values` | ENUM | DEFAULT 'FIRST' | FIRST, LAST, ALL, SUMMARIZE |
| `max_values` | INT | DEFAULT 1 | For wide-format multi-value export |
| `default_value` | TEXT | NULL | Default if not found |
| `validation_rules` | JSONB | NULL | min, max, pattern, allowed_values |
| `depends_on` | JSONB | NULL | Conditional logic referencing other variables |
| `order` | INT | NOT NULL | Display/processing sequence |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

### 4. Prompt (versioned, auto-generated)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique prompt identifier |
| `variable_id` | UUID | FK → Variable | Parent variable |
| `version` | INT | NOT NULL | Prompt version (1-indexed) |
| `system_prompt` | TEXT | NOT NULL | Full LLM prompt |
| `model` | VARCHAR(50) | NOT NULL | Model name (e.g., "gpt-4o") |
| `temperature` | FLOAT | NOT NULL | LLM temperature |
| `max_tokens` | INT | NOT NULL | Max output tokens |
| `response_schema` | JSONB | NOT NULL | Expected output JSON schema |
| `is_active` | BOOLEAN | DEFAULT true | Whether this version is active |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |

**Index**: `(variable_id, version)` composite

### 5. Document

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique document identifier |
| `project_id` | UUID | FK → Project | Parent project |
| `filename` | VARCHAR(500) | NOT NULL | Original filename |
| `content_type` | VARCHAR(50) | NOT NULL | MIME type |
| `raw_text` | TEXT | NOT NULL | Extracted text content |
| `chunk_count` | INT | DEFAULT 0 | Number of chunks (if chunked) |
| `word_count` | INT | NOT NULL | Word count |
| `status` | ENUM | NOT NULL, DEFAULT 'UPLOADED' | Processing status |
| `error_message` | TEXT | NULL | Error details if FAILED |
| `created_at` | TIMESTAMP | NOT NULL | Upload timestamp |

**Status enum**: UPLOADED, PARSED, READY, FAILED

### 6. DocumentChunk (for large documents)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique chunk identifier |
| `document_id` | UUID | FK → Document | Parent document |
| `chunk_index` | INT | NOT NULL | Chunk sequence number |
| `text` | TEXT | NOT NULL | Chunk content |
| `token_count` | INT | NOT NULL | Token count |
| `overlap_previous` | INT | DEFAULT 0 | Overlapping tokens with previous chunk |

**Index**: `(document_id, chunk_index)` composite

### 7. ProcessingJob

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique job identifier |
| `project_id` | UUID | FK → Project | Parent project |
| `type` | ENUM | NOT NULL | SAMPLE or FULL |
| `status` | ENUM | NOT NULL, DEFAULT 'PENDING' | Job status |
| `document_ids` | UUID[] | NOT NULL | Documents to process |
| `progress` | INT | DEFAULT 0 | Progress percentage (0-100) |
| `documents_processed` | INT | DEFAULT 0 | Count of processed documents |
| `documents_failed` | INT | DEFAULT 0 | Count of failed documents |
| `consecutive_failures` | INT | DEFAULT 0 | Consecutive failure count (for auto-pause) |
| `started_at` | TIMESTAMP | NULL | Start timestamp |
| `completed_at` | TIMESTAMP | NULL | Completion timestamp |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |

**Status enum**: PENDING, RUNNING, PAUSED, COMPLETED, FAILED

### 8. Extraction

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique extraction identifier |
| `job_id` | UUID | FK → ProcessingJob | Parent job |
| `document_id` | UUID | FK → Document | Source document |
| `variable_id` | UUID | FK → Variable | Target variable |
| `entity_index` | INT | NULL | Entity index (for entity-level extraction) |
| `entity_text` | TEXT | NULL | Identified entity text |
| `value` | JSONB | NULL | Extracted value (supports multi-value) |
| `confidence` | FLOAT | NULL, CHECK 0.0-1.0 | Confidence score |
| `source_text` | TEXT | NULL | Document excerpt (max 200 chars) |
| `prompt_version` | INT | NOT NULL | Prompt version used |
| `status` | ENUM | NOT NULL, DEFAULT 'EXTRACTED' | Extraction status |
| `error_message` | TEXT | NULL | Error details if FAILED |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |

**Status enum**: EXTRACTED, VALIDATED, FLAGGED, FAILED

**Index**: `(document_id, variable_id)` composite for dataset queries

### 9. ExtractionFeedback

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique feedback identifier |
| `extraction_id` | UUID | FK → Extraction | Target extraction |
| `feedback_type` | ENUM | NOT NULL | CORRECT, INCORRECT, PARTIALLY_CORRECT |
| `corrected_value` | JSONB | NULL | User-provided correct value |
| `user_note` | TEXT | NULL | User comment (max 1000 chars) |
| `created_at` | TIMESTAMP | NOT NULL | Feedback timestamp |

### 10. ProcessingLog (audit trail)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique log identifier |
| `job_id` | UUID | FK → ProcessingJob | Parent job |
| `document_id` | UUID | FK → Document, NULL | Related document |
| `event_type` | ENUM | NOT NULL | Event category |
| `message` | TEXT | NOT NULL | Log message |
| `metadata` | JSONB | NULL | Additional structured data |
| `created_at` | TIMESTAMP | NOT NULL | Log timestamp |

**Event type enum**: JOB_STARTED, DOC_STARTED, DOC_COMPLETED, DOC_FAILED, JOB_COMPLETED, JOB_FAILED, JOB_PAUSED, JOB_RESUMED

---

## Row-Level Security

All tenant-scoped tables include `user_id` (directly or via FK chain). PostgreSQL RLS policies enforce isolation:

```sql
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON projects
    USING (user_id = current_setting('app.current_user_id')::uuid);
```

The API layer sets `app.current_user_id` at the start of each request via SQLAlchemy event listener.

---

## State Machines

### Project Status
```
CREATED → SCHEMA_DEFINED → SAMPLE_COMPLETE → PROCESSING → COMPLETE
```

### ProcessingJob Status
```
PENDING → RUNNING → COMPLETED
                  ↘ FAILED
         ↓
       PAUSED (user-initiated or N consecutive failures)
```

### Document Status
```
UPLOADED → PARSED → READY
                  ↘ FAILED
```

### Extraction Status
```
EXTRACTED → VALIDATED (user confirmed)
          ↘ FLAGGED (user flagged for review)
          ↘ FAILED (extraction error)
```
