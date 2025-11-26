# Research: Backend Implementation for Data Extraction Workflow

**Feature**: 002-backend-implementation
**Date**: 2025-11-26
**Status**: Phase 0 Research Complete

## Research Questions

### 1. Background Job Processing: Celery vs Arq vs TaskIQ

**Decision**: **Arq** (with fallback to in-memory queue for MVP)

**Rationale:**
- **Arq Advantages**:
  - Native async/await support (matches FastAPI async patterns)
  - Simpler API than Celery (less configuration overhead)
  - Redis-backed with automatic retry and job persistence
  - Lower memory footprint than Celery
  - Better observability (job status, progress tracking built-in)

- **Celery Concerns**:
  - Heavyweight for our use case (requires RabbitMQ or Redis + more config)
  - Complex setup for async FastAPI integration
  - Overkill for our scale (100 concurrent projects, not 10,000)

- **MVP Simplification**:
  - Start with **in-memory queue** (Python's `asyncio.Queue` + background tasks)
  - Migrate to Arq + Redis when job persistence becomes critical
  - Avoids premature infrastructure complexity

**Alternatives Considered:**
- Celery: Too heavyweight, complex async integration
- TaskIQ: Less mature ecosystem, fewer examples
- FastAPI BackgroundTasks: No persistence, no retry logic, no progress tracking

---

### 2. LLM Orchestration: LangChain vs LlamaIndex vs Direct SDK

**Decision**: **LangChain** 0.3+ with OpenAI SDK

**Rationale:**
- **LangChain Advantages**:
  - Structured output parsing (Pydantic models from LLM responses)
  - Built-in retry logic with exponential backoff
  - Provider abstraction (easy to switch from OpenAI to Anthropic)
  - Prompt templating with variable substitution
  - Extensive documentation and community support

- **Direct SDK Concerns**:
  - Need to build retry logic, rate limiting, prompt templates manually
  - No structured output parsing (manual JSON parsing + validation)
  - Harder to switch LLM providers

- **LlamaIndex Concerns**:
  - Designed for RAG (retrieval augmented generation), not structured extraction
  - Overkill for our use case (we're not building search/retrieval)

**Implementation Approach**:
- Use `ChatOpenAI` with temperature=0.2 for deterministic extractions
- Use `PydanticOutputParser` for structured extraction responses
- Use `PromptTemplate` for variable substitution (project context, variable type, instructions)

**Alternatives Considered:**
- Direct OpenAI SDK: Too much custom code for retry/parsing/templating
- LlamaIndex: Not designed for structured extraction
- Anthropic SDK only: LangChain allows multi-provider strategy

---

### 3. Database Schema Design: ORM vs Query Builder vs Raw SQL

**Decision**: **SQLAlchemy 2.0 ORM** with Alembic migrations

**Rationale:**
- **SQLAlchemy 2.0 Advantages**:
  - Type-safe queries with modern async support
  - Automatic relationship loading (eager/lazy/joined)
  - Integration with Pydantic via `sqlmodel` patterns
  - Industry standard for Python ORMs

- **Alembic Advantages**:
  - Reversible migrations (rollback safety)
  - Auto-generation from model changes
  - Version control for schema evolution

- **Query Builder (SQLAlchemy Core) Concerns**:
  - More verbose than ORM for complex joins
  - Less type safety than ORM models

- **Raw SQL Concerns**:
  - No type safety, no auto-completion
  - Manual migration management
  - SQL injection risks if not careful

**Schema Design Principles:**
- Use UUIDs for primary keys (prevents ID guessing, distributed-friendly)
- Add `created_at` and `updated_at` timestamps to all tables
- Use enums for status fields (type-safe, prevents invalid states)
- Add indexes on foreign keys and frequently queried fields
- Use JSONB columns for flexible metadata (classification rules, model config)

**Alternatives Considered:**
- Raw SQL: Too error-prone, no migration safety
- Django ORM: Requires Django framework (too heavyweight)
- Tortoise ORM: Less mature than SQLAlchemy

---

### 4. Document Processing: PyPDF2 vs pdfplumber vs PyMuPDF

**Decision**: **PyMuPDF (fitz)** for PDF, **python-docx** for DOCX, **plain text** for TXT

**Rationale:**
- **PyMuPDF Advantages**:
  - Fastest PDF parsing (C-based, 10x faster than PyPDF2)
  - Accurate text extraction with layout preservation
  - Page-level extraction (useful for chunking large documents)
  - OCR support if needed (via Tesseract integration)

- **PyPDF2 Concerns**:
  - Slow for large documents
  - Inconsistent text extraction quality

- **pdfplumber Concerns**:
  - Slower than PyMuPDF
  - Table extraction focus (not needed for our use case)

**Chunking Strategy for Large Documents:**
- **Problem**: LLM context windows (e.g., GPT-4 = 128k tokens, ~96k words)
- **Solution**:
  - Chunk documents into 10-page segments (or ~5000 words)
  - Process each chunk separately with same prompt
  - Aggregate results (concatenate text extractions, average confidence scores)
  - Flag documents that exceed 100 pages for manual review

**Alternatives Considered:**
- PyPDF2: Too slow for production use
- Apache Tika (Java): Cross-language complexity, deployment overhead

---

### 5. API Response Format: REST vs GraphQL

**Decision**: **RESTful API** with JSON responses

**Rationale:**
- **REST Advantages**:
  - Simpler for frontend integration (Next.js fetch API, no GraphQL client needed)
  - Easier to cache (HTTP caching headers, CDN-friendly)
  - Better tooling (OpenAPI/Swagger docs auto-generation)
  - Matches frontend's existing service layer expectations

- **GraphQL Concerns**:
  - Over-fetching not a problem (our payloads are small)
  - Frontend doesn't need flexible querying (workflows are fixed)
  - Adds complexity (GraphQL schema, resolver logic, client library)

**API Design Standards:**
- Use HTTP verbs correctly (GET, POST, PUT, DELETE)
- Return proper status codes (200, 201, 400, 404, 422, 500)
- Use consistent error format (RFC 7807 Problem Details)
- Include pagination for list endpoints (offset/limit or cursor-based)
- Use camelCase in JSON responses (matches frontend TypeScript conventions)

**Alternatives Considered:**
- GraphQL: Overkill for our use case, adds client complexity
- gRPC: Not web-friendly, requires binary clients

---

### 6. Error Handling & Retry Logic

**Decision**: Exponential backoff with jitter, max 3 retries

**Implementation:**
```python
# Retry configuration for LLM calls
max_retries = 3
base_delay = 1.0  # seconds
max_delay = 10.0  # seconds

# Exponential backoff: delay = min(base_delay * 2^attempt + jitter, max_delay)
# Jitter: random(0, delay * 0.1) to prevent thundering herd
```

**Rationale:**
- **Exponential backoff**: Prevents overwhelming LLM API during outages
- **Jitter**: Prevents synchronized retries across multiple jobs
- **Max retries = 3**: Balances resilience vs. processing time (4 total attempts)
- **LangChain integration**: Use built-in retry decorators

**Error Categories:**
1. **Retryable Errors** (retry with backoff):
   - Network timeouts
   - LLM API rate limits (429)
   - LLM API temporary errors (503, 500)

2. **Non-Retryable Errors** (fail immediately):
   - Invalid API key (401)
   - Malformed request (400)
   - Content policy violation (from LLM)

3. **Parse Errors** (retry once, then fail):
   - LLM returns invalid JSON
   - Missing required fields in response

**Logging Strategy:**
- Log all retry attempts with context (document ID, variable ID, attempt number)
- Log final failures with full error stack trace
- Store errors in `processing_log` table for user visibility

---

### 7. Export File Generation: pandas vs manual CSV

**Decision**: **pandas** for data aggregation, **csv module** for simple exports

**Rationale:**
- **pandas Advantages**:
  - Easy pivot from long to wide format
  - Built-in CSV/Excel export
  - Efficient handling of 1000+ rows
  - Statistical summaries (completion %, confidence stats)

- **Manual CSV Concerns**:
  - Complex pivot logic for wide format
  - No native Excel support
  - Manual handling of special characters, encoding

**Export Format Specifications:**

**Wide Format (1 row per document):**
```
document_id, document_name, var1_value, var1_confidence, var2_value, var2_confidence, ...
doc-123, report.pdf, "protest", 0.92, "2024-01-15", 0.88, ...
```

**Long Format (1 row per extraction):**
```
document_id, document_name, variable_name, value, confidence, source_text
doc-123, report.pdf, "event_type", "protest", 0.92, "...excerpt..."
doc-123, report.pdf, "event_date", "2024-01-15", 0.88, "...excerpt..."
```

**Alternatives Considered:**
- Manual CSV writing: Too complex for pivot operations
- Polars: Faster than pandas but less mature ecosystem

---

### 8. Testing Strategy

**Decision**: Pytest with test database, 80% coverage target

**Test Layers:**

1. **Unit Tests** (`tests/services/`):
   - Test services in isolation (mock database, mock LLM)
   - Fast execution (< 1 second per test)
   - High coverage (90%+ for services)

2. **Integration Tests** (`tests/integration/`):
   - Test API + database together (real DB, mocked LLM)
   - Use pytest fixtures for test database setup/teardown
   - Medium execution time (< 5 seconds per test)

3. **Contract Tests** (`tests/api/`):
   - Test API request/response schemas
   - Validate OpenAPI spec matches implementation
   - Fast execution (< 1 second per test)

4. **End-to-End Tests** (future):
   - Test full workflow with real LLM (expensive, slow)
   - Run nightly, not on every commit
   - Use sample documents to minimize LLM costs

**Pytest Fixtures:**
```python
@pytest.fixture
def test_db():
    """Creates test database, runs migrations, tears down after test"""

@pytest.fixture
def mock_llm():
    """Mocks LangChain LLM to return predefined responses"""

@pytest.fixture
def sample_project():
    """Creates test project with 5 variables"""
```

**Coverage Target:**
- Overall: 80%
- Services: 90%
- API routes: 85%
- Models: 70% (simple CRUD, less critical)

**Alternatives Considered:**
- unittest: Less feature-rich than pytest (no fixtures, no parametrize)
- Manual testing only: Not sustainable for 50+ endpoints

---

## Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Web Framework** | FastAPI | 0.100+ | Async support, auto OpenAPI docs, Pydantic validation |
| **Database** | PostgreSQL | 15+ | JSONB support, reliability, ACID guarantees |
| **ORM** | SQLAlchemy | 2.0 | Industry standard, async support, type safety |
| **Migrations** | Alembic | 1.12+ | Reversible migrations, auto-generation |
| **Job Queue** | Arq (+ Redis) | 0.25+ | Async-native, simpler than Celery, Redis-backed |
| **LLM Client** | LangChain | 0.3+ | Structured output, retry logic, provider abstraction |
| **LLM Provider** | OpenAI | GPT-4 | Best structured extraction quality |
| **Document Parser** | PyMuPDF | 1.23+ | Fastest PDF parsing, accurate text extraction |
| **Data Processing** | pandas | 2.0+ | Efficient pivots, CSV/Excel export |
| **Testing** | pytest | 7.4+ | Fixtures, parametrize, async support |
| **HTTP Client** | httpx | 0.24+ | Async HTTP for external APIs |
| **Validation** | Pydantic | V2 | Request/response validation, type safety |
| **Deployment** | Docker | 20.10+ | Containerization for Railway/Render |

---

## Architecture Decisions

### 1. Service Layer Pattern

**Structure:**
```
API Routes → Services → Database Models
```

**Rationale:**
- **API Routes**: Handle HTTP concerns (request validation, response formatting)
- **Services**: Business logic (prompt generation, job orchestration)
- **Models**: Data persistence only

**Benefits:**
- Testable (mock services, not database)
- Reusable (services can be called from API or CLI)
- Maintainable (clear separation of concerns)

### 2. Async-First Architecture

**Decision**: Use `async/await` throughout (FastAPI, SQLAlchemy, LangChain)

**Rationale:**
- **Concurrency**: Handle 100+ concurrent requests without threads
- **I/O Efficiency**: Don't block on database or LLM API calls
- **Resource Efficiency**: Lower memory footprint than threads

**Implementation:**
```python
# All database queries are async
async def get_project(db: AsyncSession, project_id: str):
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()

# All LLM calls are async
async def extract_value(llm: ChatOpenAI, prompt: str):
    response = await llm.ainvoke(prompt)
    return parse_response(response)
```

### 3. Database Transaction Strategy

**Decision**: Use explicit transactions with rollback on error

**Pattern:**
```python
async with db.begin():
    project = Project(name="Test")
    db.add(project)
    # If error occurs here, entire transaction rolls back
    await db.flush()  # Get project.id before commit
    variable = Variable(project_id=project.id, name="var1")
    db.add(variable)
    # Commit happens automatically if no exception
```

**Rationale:**
- **Atomicity**: Related inserts/updates succeed or fail together
- **Data Integrity**: Prevent orphaned records (variables without projects)
- **Error Recovery**: Automatic rollback on exceptions

---

## Open Questions for Phase 1

1. **LLM Provider Fallback**: Should we support Anthropic Claude as fallback if OpenAI fails?
   - **Recommendation**: Defer to Phase 2. OpenAI has 99.9% uptime.

2. **Document Storage**: Store in database (BYTEA) or file system (S3)?
   - **Recommendation**: Database for MVP (simpler, < 1000 docs), migrate to S3 in Phase 2 if needed.

3. **Rate Limiting**: Limit API requests per user/project?
   - **Recommendation**: Not needed for MVP (single-tenant), add in Phase 2 with authentication.

4. **Caching**: Cache LLM responses for duplicate documents?
   - **Recommendation**: Defer to Phase 2. Extractions are context-dependent (schema changes invalidate cache).

5. **Monitoring**: Use Sentry for error tracking?
   - **Recommendation**: Yes, free tier sufficient for MVP. Critical for production debugging.

---

**Phase 0 Complete**: All NEEDS CLARIFICATION items resolved. Ready for Phase 1 (Design).
