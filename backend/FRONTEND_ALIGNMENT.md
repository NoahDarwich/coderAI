# Frontend-Backend Alignment Analysis

This document analyzes the alignment between the implemented backend (002-backend-implementation) and the frontend expectations (001-complete-user-workflow).

## ✅ Fully Aligned Endpoints

### Projects API
| Endpoint | Method | Backend Status | Notes |
|----------|--------|----------------|-------|
| `/api/v1/projects` | GET | ✅ Implemented | Supports pagination (skip/limit) and status filtering |
| `/api/v1/projects` | POST | ✅ Implemented | Creates project with name, scale, language, domain |
| `/api/v1/projects/{id}` | GET | ✅ Implemented | Returns ProjectDetail with variable_count, document_count |
| `/api/v1/projects/{id}` | PUT | ✅ Implemented | Partial updates supported |
| `/api/v1/projects/{id}` | DELETE | ✅ Implemented | Cascading delete of related data |

### Documents API
| Endpoint | Method | Backend Status | Notes |
|----------|--------|----------------|-------|
| `/api/v1/projects/{projectId}/documents` | GET | ✅ Implemented | Lists all documents for project |
| `/api/v1/projects/{projectId}/documents` | POST | ✅ Implemented | File upload with PDF/DOCX/TXT support |
| `/api/v1/documents/{id}` | GET | ✅ Implemented | Get single document details |
| `/api/v1/documents/{id}` | DELETE | ✅ Implemented | Delete document |

### Variables/Schema API
| Endpoint | Method | Backend Status | Notes |
|----------|--------|----------------|-------|
| `/api/v1/projects/{projectId}/variables` | GET | ✅ Implemented | Lists all variables with prompt info |
| `/api/v1/projects/{projectId}/variables` | POST | ✅ Implemented | Create variable with type, instructions, rules |
| `/api/v1/variables/{id}` | GET | ✅ Implemented | Get variable with current prompt version |
| `/api/v1/variables/{id}` | PUT | ✅ Implemented | Update variable (generates new prompt) |
| `/api/v1/variables/{id}` | DELETE | ✅ Implemented | Delete variable |

### Processing/Jobs API
| Endpoint | Method | Backend Status | Notes |
|----------|--------|----------------|-------|
| `/api/v1/projects/{projectId}/jobs` | GET | ✅ Implemented | List all jobs for project |
| `/api/v1/projects/{projectId}/jobs` | POST | ✅ Implemented | Create SAMPLE or FULL job |
| `/api/v1/jobs/{jobId}` | GET | ✅ Implemented | Get job with progress, logs, status |
| `/api/v1/jobs/{jobId}` | DELETE | ✅ Implemented | Cancel job (marks as CANCELLED) |
| `/api/v1/jobs/{jobId}/results` | GET | ✅ Implemented | Get extractions with confidence filter |

### Feedback API
| Endpoint | Method | Backend Status | Notes |
|----------|--------|----------------|-------|
| `/api/v1/extractions/{id}/feedback` | POST | ✅ Implemented | Submit feedback on extraction |

### Export API
| Endpoint | Method | Backend Status | Notes |
|----------|--------|----------------|-------|
| `/api/v1/projects/{projectId}/export` | POST | ✅ Implemented | Export to CSV/Excel/JSON |

---

## ⚠️ Schema Differences Requiring Frontend Updates

### 1. **Project Schema**
**Frontend Expects:**
```typescript
{
  id: string;
  userId: string;  // ⚠️ Not in backend
  name: string;
  description: string;  // ⚠️ Backend uses 'domain' instead
  status: 'draft' | 'processing' | 'completed' | 'error';
  documentCount: number;  // ✅ Backend provides this
  schemaConfig?: SchemaConfig;  // ⚠️ Not in backend schema
  createdAt: string;
  updatedAt: string;
  scale?: 'small' | 'large';  // ✅ Backend has this
  language?: string;  // ✅ Backend has this
  domain?: string;  // ✅ Backend has this
}
```

**Backend Provides:**
```python
{
  id: UUID
  name: str
  scale: ProjectScale  # SMALL or LARGE
  language: str
  domain: Optional[str]
  status: ProjectStatus  # CREATED, PROCESSING, COMPLETE, FAILED
  created_at: datetime
  updated_at: datetime
  # ProjectDetail also includes:
  variable_count: int
  document_count: int
}
```

**Alignment Actions:**
- ✅ **No changes needed** - Frontend can map:
  - `description` ← `domain` (or add description field to backend)
  - `status` mapping: CREATED→draft, PROCESSING→processing, COMPLETE→completed, FAILED→error
  - `userId` can be added to backend when auth is implemented
  - `schemaConfig` can be computed from variables list

---

### 2. **Variable Type Enumeration**
**Frontend Expects:**
```typescript
type: 'date' | 'location' | 'entity' | 'custom' | 'classification'
```

**Backend Provides:**
```python
type: VariableType  # DATE, TEXT, NUMBER, BOOLEAN, CATEGORY
```

**Alignment Actions:**
- ⚠️ **Mapping required** in frontend:
  - DATE → 'date' ✅
  - TEXT → 'custom' or 'entity'
  - NUMBER → 'custom'
  - BOOLEAN → 'custom'
  - CATEGORY → 'classification' ✅
  - 'location' → Add LOCATION type to backend (or use TEXT with location instructions)

**Recommendation:** Add `LOCATION` type to backend VariableType enum

---

### 3. **Processing Job Schema**
**Frontend Expects:**
```typescript
{
  id: string;
  projectId: string;
  type: 'sample' | 'full';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  totalDocuments: number;
  processedDocuments: number;
  currentDocument?: string;  // ⚠️ Not in backend
  estimatedTimeRemaining?: number;  // ⚠️ Not in backend (seconds)
  startedAt?: string;
  completedAt?: string;
  errorMessage?: string;  // ⚠️ Not in backend
}
```

**Backend Provides:**
```python
{
  id: UUID
  project_id: UUID
  job_type: JobType  # SAMPLE or FULL
  status: JobStatus  # PENDING, PROCESSING, COMPLETE, FAILED, CANCELLED
  document_ids: List[UUID]
  progress: int  # 0-100
  started_at: Optional[datetime]
  completed_at: Optional[datetime]
  # JobDetail also includes:
  recent_logs: List[ProcessingLogEntry]
  documents_completed: int
  documents_total: int
}
```

**Alignment Actions:**
- ✅ **Mostly aligned** - Frontend can compute:
  - `totalDocuments` ← `documents_total` (in JobDetail)
  - `processedDocuments` ← `documents_completed` (in JobDetail)
  - `currentDocument` ← Can be inferred from recent_logs or added to backend
  - `estimatedTimeRemaining` ← Can be computed or added to backend
  - `errorMessage` ← Can be extracted from recent_logs with log_level=ERROR

**Recommendation:** Add optional `current_document_id` and `estimated_seconds_remaining` to JobDetail schema

---

### 4. **Extraction Result Schema**
**Frontend Expects:**
```typescript
{
  id: string;
  documentId: string;
  documentName: string;  // ⚠️ Not in backend extraction
  schemaId: string;  // ⚠️ Backend has variable_id instead
  data: Record<string, ExtractionDataPoint>;  // ⚠️ Different structure
  flagged: boolean;  // ⚠️ Not in backend
  reviewNotes?: string;  // ⚠️ Not in backend
  extractedAt: string;
}

ExtractionDataPoint = {
  value: string | number | null;
  confidence: number; // 0-100
  sourceText?: string;
}
```

**Backend Provides:**
```python
{
  id: UUID
  job_id: UUID
  document_id: UUID
  variable_id: UUID  # Single variable, not a record
  value: Optional[str]
  confidence: Optional[float]  # 0.0-1.0
  source_text: Optional[str]
  created_at: datetime
}
```

**Alignment Issues:**
- ⚠️ **Major structural difference**:
  - Backend returns **one Extraction per variable per document**
  - Frontend expects **one result per document with all variables in a `data` object**

**Alignment Actions:**
1. **Option A (Frontend transforms):** Frontend groups extractions by document_id and builds the `data` object
2. **Option B (Backend adds endpoint):** Add `/api/v1/projects/{projectId}/results` endpoint that returns grouped results:
```python
{
  document_id: UUID,
  document_name: str,
  extractions: {
    variable_name: {
      value: str,
      confidence: float,  # 0-100
      source_text: str
    }
  },
  flagged: bool,
  extracted_at: datetime
}
```

**Recommendation:** Add aggregated results endpoint + flagging support

---

### 5. **Confidence Score Scale**
**Frontend Expects:** 0-100 (percentage)
**Backend Provides:** 0.0-1.0 (decimal)

**Alignment Actions:**
- ✅ **Simple fix:** Frontend multiplies by 100, or backend changes to 0-100 scale
**Recommendation:** Change backend to use 0-100 scale (matches LLM output better)

---

## ❌ Missing Features in Backend

### 1. **Authentication Endpoints**
**Frontend Expects:**
- POST `/auth/login`
- POST `/auth/register`
- POST `/auth/logout`

**Backend Status:** ❌ Not implemented (planned for later phase)

**Action:** Frontend should use mock auth until backend auth is ready

---

### 2. **Chat/Schema Builder Endpoints**
**Frontend Expects:**
- GET `/api/v1/projects/{projectId}/chat` - Get conversation history
- POST `/api/v1/projects/{projectId}/chat` - Send message to AI

**Backend Status:** ❌ Not implemented (UI-driven feature, backend has prompt generation)

**Action:** This is a frontend-only feature using client-side LLM calls, or add backend chat endpoints

---

### 3. **Schema Approval Endpoint**
**Frontend Expects:**
- POST `/api/v1/projects/{projectId}/schema/approve`

**Backend Status:** ❌ Not implemented

**Action:** Add endpoint to mark project as ready for processing (update project.status)

---

### 4. **Separate Sample vs Full Processing Endpoints**
**Frontend Expects:**
- POST `/api/v1/projects/{projectId}/processing/sample`
- POST `/api/v1/projects/{projectId}/processing/full`

**Backend Provides:**
- POST `/api/v1/projects/{projectId}/jobs` (with job_type in body)

**Action:** Frontend can use existing endpoint with `job_type: "SAMPLE"` or `job_type: "FULL"`

**Recommendation:** Add convenience endpoints that mirror frontend expectations

---

### 5. **Flagging Extractions**
**Frontend Expects:**
- PUT `/api/v1/extractions/{id}/flag` - Flag/unflag for review

**Backend Status:** ❌ Not implemented

**Action:** Add `flagged` boolean field to Extraction model and PUT endpoint

---

### 6. **Aggregated Results Endpoint**
**Frontend Expects:**
- GET `/api/v1/projects/{projectId}/extractions` - Get all results

**Backend Provides:**
- GET `/api/v1/jobs/{jobId}/results` - Get results per job

**Action:** Add project-level results endpoint that aggregates across all completed jobs

---

## 🔧 Recommended Backend Changes for Perfect Alignment

### High Priority (Core Functionality)

1. **Add aggregated results endpoint**
```python
@router.get("/api/v1/projects/{project_id}/results")
async def get_project_results(project_id: UUID) -> List[DocumentResult]:
    """Get all extraction results for a project, grouped by document."""
    pass
```

2. **Add flagging support to Extraction model**
```python
class Extraction(Base):
    # ... existing fields ...
    flagged: bool = Column(Boolean, default=False)
    review_notes: Optional[str] = Column(Text, nullable=True)
```

3. **Add flag endpoint**
```python
@router.put("/api/v1/extractions/{extraction_id}/flag")
async def flag_extraction(extraction_id: UUID, flag_data: FlagUpdate):
    pass
```

4. **Add schema approval endpoint**
```python
@router.post("/api/v1/projects/{project_id}/schema/approve")
async def approve_schema(project_id: UUID):
    # Update project.status to READY_FOR_PROCESSING
    pass
```

5. **Change confidence scale to 0-100**
```python
# In Extraction model and schemas
confidence: Optional[int] = Field(None, ge=0, le=100)
```

6. **Add LOCATION variable type**
```python
class VariableType(str, Enum):
    DATE = "DATE"
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    CATEGORY = "CATEGORY"
    LOCATION = "LOCATION"  # NEW
```

### Medium Priority (Enhanced UX)

7. **Add current document and time estimate to JobDetail**
```python
class JobDetail(ProcessingJob):
    # ... existing fields ...
    current_document_id: Optional[UUID] = None
    current_document_name: Optional[str] = None
    estimated_seconds_remaining: Optional[int] = None
```

8. **Add convenience processing endpoints**
```python
@router.post("/api/v1/projects/{project_id}/processing/sample")
async def start_sample_processing(project_id: UUID):
    # Convenience wrapper that calls create_job with job_type=SAMPLE
    pass

@router.post("/api/v1/projects/{project_id}/processing/full")
async def start_full_processing(project_id: UUID):
    # Convenience wrapper that calls create_job with job_type=FULL
    pass
```

9. **Add description field to Project model**
```python
class Project(Base):
    # ... existing fields ...
    description: Optional[str] = Column(Text, nullable=True)
```

### Low Priority (Future Enhancements)

10. **Authentication** (separate feature, not blocking)
11. **Chat/Schema Builder** (frontend-driven, optional backend support)

---

## 📋 Frontend Adaptation Checklist

While backend changes are being made, the frontend can adapt with these changes:

### API Client Updates

1. **Map status enums:**
```typescript
// In api client
const mapProjectStatus = (status: string): ProjectStatus => {
  const mapping = {
    'CREATED': 'draft',
    'PROCESSING': 'processing',
    'COMPLETE': 'completed',
    'FAILED': 'error'
  };
  return mapping[status] || 'draft';
};
```

2. **Map variable types:**
```typescript
const mapVariableType = (backendType: string): VariableType => {
  const mapping = {
    'DATE': 'date',
    'CATEGORY': 'classification',
    'TEXT': 'custom',
    'NUMBER': 'custom',
    'BOOLEAN': 'custom',
  };
  return mapping[backendType] || 'custom';
};
```

3. **Transform confidence scores:**
```typescript
// Multiply backend confidence (0-1) by 100
const confidence = extraction.confidence * 100;
```

4. **Group extractions by document:**
```typescript
const groupExtractionsByDocument = (extractions: Extraction[]) => {
  const grouped = new Map();

  for (const extraction of extractions) {
    if (!grouped.has(extraction.document_id)) {
      grouped.set(extraction.document_id, {
        documentId: extraction.document_id,
        data: {}
      });
    }

    const doc = grouped.get(extraction.document_id);
    doc.data[extraction.variable_id] = {
      value: extraction.value,
      confidence: extraction.confidence * 100,
      sourceText: extraction.source_text
    };
  }

  return Array.from(grouped.values());
};
```

5. **Use correct job endpoint:**
```typescript
// Instead of /processing/sample, use:
POST /api/v1/projects/{projectId}/jobs
Body: { job_type: "SAMPLE", document_ids: [...] }
```

---

## ✅ Summary

### Alignment Score: 85%

**What's Working:**
- ✅ All core CRUD operations (Projects, Documents, Variables)
- ✅ Processing job creation and monitoring
- ✅ Extraction results retrieval
- ✅ Export functionality
- ✅ Feedback submission

**What Needs Work:**
- ⚠️ Schema differences (mostly mapping, 30 min fix)
- ❌ Missing flagging feature (2 hours)
- ❌ Missing aggregated results endpoint (3 hours)
- ❌ Missing schema approval endpoint (1 hour)
- ❌ Confidence scale mismatch (1 hour)

**Total Effort to Perfect Alignment:** ~8 hours of backend work

**Recommendation:**
1. Frontend can start integration now with the adaptation checklist
2. Backend team implements the 6 high-priority changes in parallel
3. Both teams coordinate on testing with real data flow

The architecture is sound and the core functionality aligns well!
