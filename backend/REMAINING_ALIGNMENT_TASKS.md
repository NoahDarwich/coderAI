# Remaining Frontend Alignment Tasks

This document lists the remaining tasks to achieve 100% frontend-backend alignment based on the analysis in FRONTEND_ALIGNMENT.md.

## ✅ Completed (Just Now)

- **T1**: Add LOCATION variable type to VariableType enum ✅
  - Files: `backend/src/models/variable.py`, `backend/src/services/prompt_generator.py`
  - Status: DONE - includes prompt generation and model config

---

## 🔧 Remaining High-Priority Tasks

### T2: Change Confidence Scale from 0-1 to 0-100

**Rationale:** Frontend expects 0-100 percentage scale, backend uses 0-1 decimal

**Files to modify:**
1. `backend/src/models/extraction.py` - Change `confidence` column type
2. `backend/src/schemas/processing.py` - Update Extraction schema validation
3. `backend/src/schemas/export.py` - Update export schemas
4. `backend/src/services/extraction_service.py` - Update LLM response parsing
5. `backend/src/services/prompt_generator.py` - Update all prompt examples (0.95 → 95)

**Implementation:**
```python
# In models/extraction.py
confidence = Column(Integer, nullable=True)  # 0-100 instead of Float

# In schemas/processing.py
confidence: Optional[int] = Field(None, ge=0, le=100, description="Confidence score (0-100)")

# In services/extraction_service.py - LLM parsing
# Multiply by 100 if LLM returns 0-1, or update prompts to request 0-100
```

**Estimated Time:** 2 hours

---

### T3: Add Flagging Support

**Rationale:** Frontend needs to flag/unflag extractions for review

**Step 3a: Update Extraction Model**
```python
# backend/src/models/extraction.py
class Extraction(Base):
    # ... existing fields ...
    flagged = Column(Boolean, nullable=False, default=False)
    review_notes = Column(Text, nullable=True)
```

**Step 3b: Create Migration**
```bash
cd backend
alembic revision --autogenerate -m "Add flagged and review_notes to extractions"
alembic upgrade head
```

**Step 3c: Update Extraction Schema**
```python
# backend/src/schemas/processing.py
class Extraction(BaseModel):
    # ... existing fields ...
    flagged: bool = False
    review_notes: Optional[str] = None
```

**Estimated Time:** 1.5 hours

---

### T4: Add Flag/Unflag Endpoint

**Rationale:** Frontend needs PUT `/api/v1/extractions/{id}/flag` endpoint

**Implementation:**
```python
# backend/src/schemas/processing.py
class FlagUpdate(BaseModel):
    """Schema for flagging/unflagging an extraction."""
    flagged: bool
    review_notes: Optional[str] = None

# backend/src/api/routes/processing.py
@router.put("/api/v1/extractions/{extraction_id}/flag", response_model=ExtractionSchema)
async def flag_extraction(
    extraction_id: UUID,
    flag_data: FlagUpdate,
    db: AsyncSession = Depends(get_db),
) -> ExtractionSchema:
    """
    Flag or unflag an extraction for review.

    Args:
        extraction_id: Extraction UUID
        flag_data: Flag status and optional notes
        db: Database session

    Returns:
        Updated extraction

    Raises:
        HTTPException: 404 if extraction not found
    """
    # Get extraction
    result = await db.execute(
        select(Extraction).where(Extraction.id == extraction_id)
    )
    extraction = result.scalar_one_or_none()

    if not extraction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction with id {extraction_id} not found",
        )

    # Update flag status
    extraction.flagged = flag_data.flagged
    extraction.review_notes = flag_data.review_notes

    await db.commit()
    await db.refresh(extraction)

    return ExtractionSchema.model_validate(extraction)
```

**Estimated Time:** 1 hour

---

### T5: Add Aggregated Results Endpoint

**Rationale:** Frontend expects GET `/api/v1/projects/{projectId}/results` to get all results grouped by document

**Implementation:**
```python
# backend/src/schemas/processing.py
class ExtractionDataPoint(BaseModel):
    """Single extraction value with metadata."""
    value: Optional[str]
    confidence: int = Field(ge=0, le=100)
    source_text: Optional[str]

class DocumentResult(BaseModel):
    """Aggregated extraction results for a single document."""
    document_id: UUID
    document_name: str
    data: Dict[str, ExtractionDataPoint]  # variable_name -> data point
    flagged: bool = False
    extracted_at: datetime

class ProjectResults(BaseModel):
    """All extraction results for a project."""
    project_id: UUID
    results: List[DocumentResult]
    total_documents: int
    total_extractions: int

# backend/src/api/routes/processing.py
@router.get("/api/v1/projects/{project_id}/results", response_model=ProjectResults)
async def get_project_results(
    project_id: UUID,
    min_confidence: Optional[int] = Query(None, ge=0, le=100),
    flagged_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> ProjectResults:
    """
    Get all extraction results for a project, grouped by document.

    Args:
        project_id: Project UUID
        min_confidence: Optional minimum confidence filter (0-100)
        flagged_only: Only return flagged results
        db: Database session

    Returns:
        Aggregated project results
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Get all extractions for project (join with documents and variables)
    query = (
        select(Extraction, Document, Variable)
        .join(Document, Extraction.document_id == Document.id)
        .join(Variable, Extraction.variable_id == Variable.id)
        .where(Document.project_id == project_id)
    )

    # Apply filters
    if min_confidence is not None:
        query = query.where(Extraction.confidence >= min_confidence)
    if flagged_only:
        query = query.where(Extraction.flagged == True)

    query = query.order_by(Document.name, Variable.order)

    result = await db.execute(query)
    rows = result.all()

    # Group by document
    documents_map = {}
    for extraction, document, variable in rows:
        doc_id = str(document.id)

        if doc_id not in documents_map:
            documents_map[doc_id] = {
                "document_id": document.id,
                "document_name": document.name,
                "data": {},
                "flagged": False,
                "extracted_at": extraction.created_at,
            }

        # Add extraction to document
        documents_map[doc_id]["data"][variable.name] = ExtractionDataPoint(
            value=extraction.value,
            confidence=extraction.confidence,
            source_text=extraction.source_text,
        )

        # If any extraction is flagged, mark document as flagged
        if extraction.flagged:
            documents_map[doc_id]["flagged"] = True

    # Convert to list
    results = [
        DocumentResult(**doc_data)
        for doc_data in documents_map.values()
    ]

    return ProjectResults(
        project_id=project_id,
        results=results,
        total_documents=len(results),
        total_extractions=len(rows),
    )
```

**Estimated Time:** 3 hours

---

### T6: Add Schema Approval Endpoint

**Rationale:** Frontend needs POST `/api/v1/projects/{projectId}/schema/approve` to mark schema ready

**Implementation:**
```python
# backend/src/models/project.py - Add new status
class ProjectStatus(str, enum.Enum):
    CREATED = "CREATED"
    SCHEMA_APPROVED = "SCHEMA_APPROVED"  # NEW
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

# backend/src/api/routes/projects.py
@router.post("/api/v1/projects/{project_id}/schema/approve", status_code=status.HTTP_204_NO_CONTENT)
async def approve_schema(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Approve project schema and mark ready for processing.

    Args:
        project_id: Project UUID
        db: Database session

    Raises:
        HTTPException: 404 if project not found
        HTTPException: 400 if no variables defined
    """
    # Get project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Verify variables exist
    result = await db.execute(
        select(func.count(Variable.id)).where(Variable.project_id == project_id)
    )
    variable_count = result.scalar_one()

    if variable_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot approve schema: no variables defined",
        )

    # Update status
    project.status = ProjectStatus.SCHEMA_APPROVED
    await db.commit()
```

**Estimated Time:** 1 hour

---

### T7: Add Convenience Processing Endpoints

**Rationale:** Frontend expects separate `/processing/sample` and `/processing/full` endpoints

**Implementation:**
```python
# backend/src/api/routes/processing.py

@router.post(
    "/api/v1/projects/{project_id}/processing/sample",
    response_model=ProcessingJobSchema,
    status_code=status.HTTP_201_CREATED,
)
async def start_sample_processing(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ProcessingJobSchema:
    """
    Convenience endpoint to start sample processing (10 documents).

    Args:
        project_id: Project UUID
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Created job
    """
    # Get first 10 documents
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.uploaded_at)
        .limit(10)
    )
    documents = result.scalars().all()

    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents found for project",
        )

    document_ids = [doc.id for doc in documents]

    # Create job
    job_manager = JobManager(db)
    job = await job_manager.create_job(
        project_id=project_id,
        job_type=JobType.SAMPLE,
        document_ids=document_ids,
        background_tasks=background_tasks,
    )

    return ProcessingJobSchema.model_validate(job)


@router.post(
    "/api/v1/projects/{project_id}/processing/full",
    response_model=ProcessingJobSchema,
    status_code=status.HTTP_201_CREATED,
)
async def start_full_processing(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ProcessingJobSchema:
    """
    Convenience endpoint to start full processing (all documents).

    Args:
        project_id: Project UUID
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Created job
    """
    # Get all documents
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.uploaded_at)
    )
    documents = result.scalars().all()

    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents found for project",
        )

    document_ids = [doc.id for doc in documents]

    # Create job
    job_manager = JobManager(db)
    job = await job_manager.create_job(
        project_id=project_id,
        job_type=JobType.FULL,
        document_ids=document_ids,
        background_tasks=background_tasks,
    )

    return ProcessingJobSchema.model_validate(job)
```

**Estimated Time:** 1 hour

---

## 📊 Summary

| Task | Priority | Estimated Time | Status |
|------|----------|----------------|--------|
| T1: LOCATION variable type | High | 1h | ✅ DONE |
| T2: Confidence scale 0-100 | High | 2h | ⏳ TODO |
| T3: Flagging support (model) | High | 1.5h | ⏳ TODO |
| T4: Flag endpoint | High | 1h | ⏳ TODO |
| T5: Aggregated results | High | 3h | ⏳ TODO |
| T6: Schema approval | High | 1h | ⏳ TODO |
| T7: Convenience endpoints | Medium | 1h | ⏳ TODO |
| **TOTAL** | | **10.5 hours** | **10% done** |

---

## 🚀 Implementation Order

1. **T2** - Confidence scale change (affects all downstream features)
2. **T3 + T4** - Flagging support (model + endpoint together)
3. **T6** - Schema approval (simple, unblocks frontend workflow)
4. **T7** - Convenience endpoints (simple, improves UX)
5. **T5** - Aggregated results (most complex, do last)

---

## ✅ Testing Checklist

After implementing all tasks:

- [ ] All Python files compile without errors
- [ ] Database migration runs successfully
- [ ] All API endpoints return correct status codes
- [ ] Confidence scores are 0-100 in all responses
- [ ] Flagging works (flag/unflag/filter by flagged)
- [ ] Aggregated results group correctly by document
- [ ] Schema approval updates project status
- [ ] Sample processing selects first 10 documents
- [ ] Full processing selects all documents
- [ ] Export includes flagged field when requested

---

## 📝 Frontend Integration Notes

Once backend changes are complete, frontend needs to:

1. **Update API client** to use new endpoints
2. **Remove transformations** for confidence (already 0-100)
3. **Add flagging UI** (flag button, filter by flagged)
4. **Use aggregated results endpoint** instead of grouping manually
5. **Call schema approval** before processing
6. **Use convenience endpoints** for sample/full processing

---

## 🎯 Next Steps

1. Review this document with team
2. Create GitHub issues for each task
3. Assign tasks to developers
4. Implement in order listed above
5. Test each feature before moving to next
6. Update FRONTEND_ALIGNMENT.md when complete

**Total effort remaining: ~10 hours of focused development**
