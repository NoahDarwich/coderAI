# AI Agent Reference: Adaptive Corpus Processing Pipeline

## Purpose

This document defines how coderAI's backend processes user-uploaded document corpora through a configurable extraction and enrichment pipeline. The system ingests documents in multiple formats, processes each document through auto-generated LLM assistants (powered by LangChain) to extract and classify structured data, and stores enriched results in PostgreSQL via SQLAlchemy 2.0.

Each project is **user-configurable** — users define their own domain, extraction targets, and variables through the frontend UI. The system auto-generates optimized LLM assistant configurations from these definitions.

---

## Architecture Decisions

These decisions were made during the discovery phase and govern the implementation:

| Area | Decision | Rationale |
|---|---|---|
| **Domain** | User-configurable per project | Each project defines its own domain, entities, and extraction targets |
| **Integration** | Refactor existing backend | Align current FastAPI backend to pipeline architecture |
| **Ingestion formats** | All common formats | CSV, JSON, PDF, Parquet, plain text, database dumps |
| **Assistant config** | Auto-generated from variables | System generates prompts, schemas, and model configs from user-defined variables |
| **DB layer** | SQLAlchemy 2.0 + Alembic | Already in place, provides ORM and migration support |
| **Job queue** | TBD | To be decided based on scaling needs |
| **LLM provider** | LangChain 0.3+ | Multi-provider abstraction supporting OpenAI, Anthropic, local models |
| **Duplicate detection** | Deferred (v2) | Not needed for initial release |
| **External APIs** | Deferred (v2) | Geocoding, entity resolution, etc. deferred |
| **Export** | CSV + Excel with filtering | Full export with metadata and quality metrics |
| **Variable definition** | UI-driven | Users define variables through the frontend wizard |

---

## 1. User-Configurable Pipeline

Unlike a fixed-domain system, coderAI allows each project to define its own extraction pipeline. The user provides:

### 1.1 Project Context (Step 1)
- **Document type**: What kind of files (PDF invoices, Word contracts, news articles, etc.)
- **Domain**: Industry or subject area
- **Language**: Document language(s)
- **Scale**: Small/experimental vs. large corpus

### 1.2 Unit of Observation (Step 2)
- **What each row represents**: Document-level, entity-level, or custom
- **Rows per document**: One or multiple
- **Entity identification pattern**: How to identify each entity (if multi-row)

### 1.3 Extraction Variables (Step 3)
Users define variables through the UI wizard. Each variable includes:
- **Variable name**: Column name in final dataset
- **Variable type**: TEXT, NUMBER, DATE, CATEGORY, BOOLEAN
- **Extraction instructions**: Natural language description of what to extract
- **Classification rules**: Categories/scales (for CATEGORY type)
- **Uncertainty handling**: Confidence threshold, multi-value strategy
- **Edge cases**: Missing field behavior, validation rules, defaults

### 1.4 Auto-Generated Assistant Configuration
From each variable definition, the system automatically generates:
- **System prompt**: Incorporating project context, unit of observation, variable instructions
- **Model configuration**: Temperature, max_tokens based on variable type and precision needs
- **Response format**: JSON schema matching the variable type
- **Prompt version**: Tracked for iterative refinement via feedback

---

## 2. System Architecture

The pipeline operates within the existing FastAPI backend structure, using SQLAlchemy 2.0 ORM models and Alembic migrations.

### 2.1 Data Flow

```
Documents (multi-format)
    ↓
Ingestion & Parsing (PDF, DOCX, CSV, JSON, Parquet, TXT)
    ↓
Processing Queue (per-document status tracking)
    ↓
Stage 1: Extraction (identify records per document)
    ↓
Stage 2: Enrichment (LLM assistants per variable)
    ↓
Stage 3: Post-Processing (validation, normalization)
    ↓
Stage 4: Storage (atomic per-document transaction)
    ↓
Export (CSV, Excel with filtering and metadata)
```

### 2.2 Database Models (SQLAlchemy 2.0)

The pipeline uses the existing data model with these key tables:

**Project** — User's research project with metadata and domain context
- Stores project-level configuration (domain, language, unit of observation)
- Status tracks workflow progression (CREATED → SCHEMA_DEFINED → PROCESSING → COMPLETE)

**Variable** — User-defined extraction target
- Stores variable definition with type, instructions, classification rules
- Linked to auto-generated Prompt records

**Prompt** — Auto-generated LLM prompt for a variable (versioned)
- Generated from variable definition + project context
- Stores model configuration (model, temperature, max_tokens)
- Version history supports feedback-driven refinement

**Document** — Uploaded/ingested document
- Stores parsed text content from any supported format
- Tracks content type, size, upload timestamp

**ProcessingJob** — Batch processing job (sample or full)
- Tracks status, progress, document IDs
- Supports SAMPLE and FULL job types

**Extraction** — Single extracted value per (document, variable) pair
- Stores value, confidence score, source text
- Links to job, document, and variable

**ExtractionFeedback** — User feedback on extraction quality
- Drives prompt refinement loop

**ProcessingLog** — Audit trail for processing events

---

## 3. Pipeline Stages

### Stage 1: Extraction

**Purpose:** Identify distinct records/entities within a single document based on the unit of observation.

**Behavior by unit type:**
- **Document-level** (one row per document): Extract all variables once per document. No separate extraction step needed.
- **Entity-level** (multiple rows per document): Use an extraction assistant to identify distinct entities, then extract variables for each entity.

**Auto-generated extraction assistant:**
- System prompt incorporates: document type, domain, language, entity identification pattern
- Response format: JSON array of extracted text segments
- Temperature: 0.1-0.2 for consistency
- Generated via LangChain with structured output parsing

### Stage 2: Enrichment

**Purpose:** Extract structured fields from each record using auto-generated LLM assistants.

**Pattern:**
- One assistant per variable (auto-generated from variable definition)
- Assistants run sequentially on each record
- Each assistant receives the extracted text and returns a typed JSON value
- Results are merged into a single extraction record

**Auto-generated assistant configuration:**
```python
{
    "variable_id": "uuid",
    "model": "gpt-4o",  # or configured via LangChain
    "temperature": 0.15,  # lower for high-precision variables
    "top_p": 0.25,
    "system_prompt": """
        You are extracting data from {document_type} documents
        in the {domain} domain, written in {language}.

        Unit of observation: {unit_of_observation}

        Extract: {variable_name} (type: {variable_type})
        Instructions: {user_instructions}

        Uncertainty handling:
        - Confidence threshold: {confidence_threshold}
        - If uncertain: {if_uncertain_action}
        - If multiple values: {multiple_values_action}

        Rules:
        - Return null for any field where the information is not explicitly stated
        - Do not infer or fabricate information
        - Include confidence score (0.0-1.0)
        - Include source text excerpt

        Output format: {json_schema}
    """,
    "response_format": {
        "type": "json_schema",
        "schema": {
            # auto-generated from variable type
        }
    }
}
```

### Stage 3: Post-Processing (Non-AI)

**Purpose:** Apply deterministic transformations after LLM extraction.

**Operations:**
- Date normalization (convert various formats to ISO 8601)
- Type coercion (ensure NUMBER variables are numeric, etc.)
- Default value population (from variable edge case config)
- Validation against user-defined rules (min/max, allowed values, regex)
- Confidence score validation (0.0-1.0 range)

### Stage 4: Database Storage

**Purpose:** Atomically save all extractions for a document.

**Pattern (SQLAlchemy):**
```python
async with db.begin() as session:
    for extraction in extractions:
        session.add(Extraction(
            job_id=job.id,
            document_id=doc.id,
            variable_id=var.id,
            value=extraction.value,
            confidence=extraction.confidence,
            source_text=extraction.source_text,
        ))
    job.progress = calculate_progress(completed, total)
    # if any insert fails, entire transaction rolls back
```

---

## 4. Document Ingestion

The system supports all common document formats. Each format has a dedicated parser that extracts text content.

### Supported Formats

| Format | Parser | Notes |
|--------|--------|-------|
| **PDF** | PyMuPDF (fitz) | Handles text extraction, OCR fallback possible |
| **DOCX** | python-docx | Microsoft Word documents |
| **TXT** | Built-in | Plain text files |
| **CSV** | pandas | Each row can be treated as a document |
| **JSON** | Built-in / pandas | Structured data, configurable text field |
| **Parquet** | pyarrow + pandas | Columnar format for large datasets |

### Ingestion Pattern

```python
class DocumentProcessor:
    """Parse documents from any supported format into text content."""

    def parse(self, file: UploadFile) -> str:
        """Extract text content from uploaded file."""
        parser = self._get_parser(file.content_type)
        return parser.extract_text(file)

    def parse_bulk(self, file: UploadFile) -> list[dict]:
        """For CSV/JSON/Parquet: parse into multiple document records."""
        parser = self._get_parser(file.content_type)
        return parser.extract_records(file)
```

### Bulk Ingestion (CSV, JSON, Parquet)

For tabular formats, each row becomes a separate document:
- User maps a column to the text content field
- Additional columns become document metadata
- Supports batch creation of Document records

---

## 5. LLM Integration via LangChain

All LLM calls go through LangChain for provider abstraction and built-in retry logic.

### Client Pattern

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

class LLMClient:
    """LangChain-based LLM client with retry and structured output."""

    def __init__(self, config: Settings):
        self.default_llm = ChatOpenAI(
            model=config.default_model,
            api_key=config.openai_api_key,
        )

    async def extract(
        self,
        prompt_text: str,
        document_text: str,
        model_config: dict,
        response_schema: dict,
    ) -> dict:
        """Call LLM with auto-generated prompt and parse structured response."""
        llm = self._get_llm(model_config)
        parser = JsonOutputParser(pydantic_object=response_schema)
        chain = prompt | llm | parser
        return await chain.ainvoke({"document_text": document_text})

    def _get_llm(self, config: dict):
        return ChatOpenAI(
            model=config.get("model", "gpt-4o"),
            temperature=config.get("temperature", 0.15),
            max_tokens=config.get("max_tokens", 1000),
        )
```

### Retry Logic

- Max 3 retries with exponential backoff (via LangChain built-in or tenacity)
- Handle: API errors, rate limits, malformed responses, timeouts
- On final failure: log error, mark extraction as failed, continue with next

### Provider Flexibility

LangChain enables switching providers without code changes:
- OpenAI (default): `ChatOpenAI`
- Anthropic: `ChatAnthropic`
- Local models: `ChatOllama`
- Azure OpenAI: `AzureChatOpenAI`

Configuration is per-project or global via environment variables.

---

## 6. Code Structure

Maps to the existing backend structure:

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── projects.py        # Project CRUD endpoints
│   │   │   ├── variables.py       # Variable definition endpoints
│   │   │   ├── documents.py       # Document upload + bulk ingestion
│   │   │   ├── processing.py      # Job creation, status, results
│   │   │   └── exports.py         # Export generation endpoints
│   │   ├── dependencies.py        # FastAPI dependencies (DB session)
│   │   └── middleware.py          # CORS, error handling, logging
│   ├── core/
│   │   ├── config.py              # Settings (env vars, DB URLs, API keys)
│   │   ├── database.py            # SQLAlchemy async engine and session
│   │   └── logging.py             # Structured logging
│   ├── models/
│   │   ├── base.py                # Base model with common fields
│   │   ├── project.py             # Project ORM model
│   │   ├── variable.py            # Variable ORM model
│   │   ├── document.py            # Document ORM model
│   │   ├── extraction.py          # Extraction ORM model (prompt.py included)
│   │   ├── extraction_feedback.py # Feedback ORM model
│   │   └── processing_log.py      # Processing log ORM model
│   ├── schemas/
│   │   ├── base.py                # Pydantic base schemas
│   │   ├── project.py             # Project request/response schemas
│   │   ├── variable.py            # Variable schemas
│   │   ├── processing.py          # Job and extraction schemas
│   │   └── export.py              # Export request/response schemas
│   ├── services/
│   │   ├── prompt_generator.py    # Auto-generate assistant configs from variables
│   │   ├── llm_client.py          # LangChain LLM integration
│   │   ├── document_processor.py  # Multi-format document parsing
│   │   ├── extraction_service.py  # Pipeline orchestration per document
│   │   ├── feedback_analyzer.py   # Analyze feedback, refine prompts
│   │   ├── job_manager.py         # Job creation and progress tracking
│   │   └── export_service.py      # Dataset aggregation and file generation
│   ├── workers/
│   │   └── processing_worker.py   # Background job processing
│   └── main.py                    # FastAPI app initialization
├── alembic/                       # Database migrations
├── tests/                         # Test suite
└── requirements.txt               # Python dependencies
```

### Module Responsibilities

**prompt_generator.py** — Auto-generates LLM configurations
- Takes Variable + Project as input
- Generates system prompt with full context (domain, language, unit of observation)
- Selects model parameters based on variable type and precision needs
- Creates versioned Prompt records
- Rebuilds prompts when variables are updated or feedback is incorporated

**llm_client.py** — LangChain integration
- Provider-agnostic LLM calls via LangChain
- Structured output parsing with JSON schemas
- Retry logic with exponential backoff
- Rate limiting to prevent quota exhaustion

**document_processor.py** — Multi-format ingestion
- PDF text extraction (PyMuPDF)
- DOCX parsing (python-docx)
- CSV/JSON/Parquet bulk ingestion (pandas/pyarrow)
- Plain text support
- Document chunking for large documents (>10 pages or >5000 words)

**extraction_service.py** — Pipeline orchestrator
- Runs extraction → enrichment → post-processing → storage per document
- Calls LLM for each (document, variable) pair using auto-generated prompts
- Handles entity-level extraction (multiple records per document)
- Tracks progress and logs events

**feedback_analyzer.py** — Prompt refinement
- Analyzes user corrections to identify error patterns
- Updates prompts based on feedback (creates new version)
- Supports re-running samples with improved prompts

**export_service.py** — Data export
- Aggregates extractions into pandas DataFrame
- Wide format (1 row per unit of observation, columns = variables)
- Long format (1 row per extraction)
- Optional confidence scores and source text columns
- Generates CSV and Excel files
- Includes codebook (variable definitions) and quality metrics

---

## 7. Environment & Dependencies

### 7.1 Required Environment Variables

```
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
OPENAI_API_KEY=<openai_api_key>
REDIS_URL=redis://localhost:6379  # optional, for job queue
ALLOWED_ORIGINS=http://localhost:3000
DEBUG=True
LOG_LEVEL=INFO
```

### 7.2 Python Dependencies

```
# Web framework
fastapi>=0.100
uvicorn[standard]
pydantic>=2.0
pydantic-settings

# Database
sqlalchemy>=2.0
asyncpg
alembic

# LLM integration
langchain>=0.3
langchain-openai
openai

# Document processing
PyMuPDF          # PDF parsing
python-docx      # DOCX parsing
pandas           # CSV/JSON/Parquet + export
pyarrow          # Parquet support
openpyxl         # Excel export

# Utilities
python-dotenv
tqdm
tenacity         # retry logic
python-multipart # file uploads
```

---

## 8. Key Implementation Patterns

### 8.1 Resumable Processing Queue

```python
async def process_job(job_id: UUID, db: AsyncSession):
    job = await db.get(ProcessingJob, job_id)
    documents = await get_documents(job.document_ids, db)

    for i, document in enumerate(documents):
        try:
            records = await extract(document, job.project)
            for record in records:
                await enrich(record, job.project.variables)
                post_process(record)
            await save_extractions(db, job, document, records)
            job.progress = int((i + 1) / len(documents) * 100)
            await db.commit()
        except Exception as e:
            await log_error(db, job, document, str(e))
            continue  # continue with next document
```

### 8.2 Auto-Generated Assistant Configuration

```python
def generate_assistant_config(variable: Variable, project: Project) -> dict:
    """Generate LLM assistant configuration from variable definition."""
    temperature = {
        VariableType.BOOLEAN: 0.1,
        VariableType.CATEGORY: 0.1,
        VariableType.DATE: 0.15,
        VariableType.NUMBER: 0.15,
        VariableType.TEXT: 0.2,
    }.get(variable.type, 0.15)

    return {
        "model": "gpt-4o",
        "temperature": temperature,
        "max_tokens": 1000,
        "system_prompt": build_prompt(variable, project),
        "response_format": build_schema(variable),
    }
```

### 8.3 Atomic Transaction Pattern (SQLAlchemy)

```python
async def save_extractions(
    db: AsyncSession,
    job: ProcessingJob,
    document: Document,
    extractions: list[dict],
):
    async with db.begin_nested():
        for ext in extractions:
            db.add(Extraction(
                job_id=job.id,
                document_id=document.id,
                variable_id=ext["variable_id"],
                value=ext["value"],
                confidence=ext["confidence"],
                source_text=ext["source_text"],
            ))
        job.records_extracted = (job.records_extracted or 0) + len(extractions)
    await db.commit()
```

---

## 9. Constraints & Principles

- **User-configurable**: Every project defines its own domain, variables, and extraction logic. No hardcoded schemas.
- **Auto-generated assistants**: LLM prompts and configs are generated from user definitions, not manually authored.
- **SQLAlchemy 2.0**: All database operations use async SQLAlchemy ORM. No raw SQL unless performance-critical.
- **LangChain abstraction**: All LLM calls go through LangChain for provider flexibility and built-in features.
- **Sequential per-document processing**: Process one document at a time. Simple, debuggable, and resumable.
- **Atomic transactions**: All extractions from one document are saved or none are.
- **Fail gracefully**: Log errors, mark documents as failed, continue processing. Stop only after N consecutive failures.
- **Low temperature, focused sampling**: Extraction assistants use low temperature (0.1-0.3) for consistent outputs.
- **No inference, no fabrication**: Assistants must only extract explicitly stated information.
- **Idempotent retry**: A failed document can be reprocessed without side effects.
- **Denormalized output**: Extraction results are stored flat for simple queries and export.

---

## 10. Deferred Features (v2)

The following features are designed but deferred to a future version:

### Duplicate Detection
- 2-phase detection: SQL pre-filter + LLM verification
- Union-Find clustering for transitive duplicate relationships
- Optional merged record creation via summarizer assistant
- Columns: `is_duplicate`, `duplicate_record_ids`, `merged_to`

### External API Enrichment
- Geocoding (Google Maps API) for location fields
- Entity resolution services
- Translation services
- Sentiment analysis

### Advanced Job Queue
- Redis-backed persistent queue (Celery, ARQ, or custom)
- Job priority and scheduling
- Multi-worker processing

---

## 11. Generation Checklist

When implementing the pipeline for a project, ensure:

1. **Variable → Assistant config**: Each variable auto-generates a complete assistant configuration
2. **Prompt includes full context**: Domain, language, document type, unit of observation, variable instructions, uncertainty handling
3. **Multi-format ingestion**: Document processor handles PDF, DOCX, TXT, CSV, JSON, Parquet
4. **Pipeline stages**: Extraction → Enrichment → Post-processing → Storage runs per document
5. **Atomic storage**: All extractions for a document saved in a single transaction
6. **Progress tracking**: Job progress updated after each document
7. **Error resilience**: Individual failures don't stop the pipeline
8. **Feedback loop**: User corrections update prompts (new version created)
9. **Export**: CSV + Excel with optional confidence scores, source text, and codebook
10. **Resumable**: Processing can stop and restart from where it left off
