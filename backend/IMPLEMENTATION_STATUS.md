# Backend Implementation Status

**Last Updated**: 2026-02-10
**Branch**: `master`
**Source of Truth**: [CODERAI_REFERENCE.md](/CODERAI_REFERENCE.md)

---

## Current State

The backend has existing code under `backend/src/` that was built before the current architecture was defined in CODERAI_REFERENCE.md. This code needs to be **restructured and realigned**.

### What Exists (under backend/src/)

| Layer | Files | Status |
|-------|-------|--------|
| **Models** | 9 SQLAlchemy models | Need expansion: User + DocumentChunk missing; Variable, Document, Extraction need new fields |
| **Schemas** | 7 Pydantic modules | Need updates for new fields |
| **Routes** | 5 route modules | Need restructuring for new directory layout |
| **Services** | 7 services | Need refactoring: LangChain-only LLM, pipeline stages, post-processing |
| **Core** | config, database, logging | Need auth, security, exceptions, RLS |
| **Workers** | Empty `__init__.py` | Need ARQ worker implementation |
| **Agents** | Does not exist | Need co-pilot, extractor, refiner modules |

### Key Gaps vs. CODERAI_REFERENCE.md

1. **Directory structure**: Currently `backend/src/` → needs `backend/app/`
2. **No User model or auth**: JWT auth and multi-tenancy not implemented
3. **No DocumentChunk model**: Large document chunking not supported
4. **No ARQ workers**: Using FastAPI BackgroundTasks instead of ARQ + Redis
5. **No Row-Level Security**: No multi-tenancy isolation
6. **No WebSocket**: No real-time job progress
7. **No agents directory**: Co-pilot, extractor, refiner not implemented
8. **Wrong LLM client**: Job manager uses OpenAI SDK directly instead of LangChain
9. **No post-processing stage**: LLM output goes straight to DB without validation
10. **No entity-level extraction**: Only document-level supported
11. **No circuit breaker**: Basic retry only
12. **Variable model incomplete**: Missing display_name, if_uncertain, if_multiple_values, max_values, default_value, depends_on
13. **Extraction model incomplete**: Missing entity_index, entity_text, prompt_version, status enum

---

## Development Phases (from CODERAI_REFERENCE.md Section 13)

### Phase 1: Foundation (MVP)
- [ ] Project CRUD
- [ ] Document upload + parsing (PDF, TXT)
- [ ] Variable definition (manual)
- [ ] Basic extraction pipeline (sequential)
- [ ] Export to CSV
- [ ] Single-user (no auth)

### Phase 2: Core Features
- [ ] Authentication + multi-tenancy (JWT + RLS)
- [ ] Entity-level extraction
- [ ] Sample → Feedback → Full run workflow
- [ ] Job queue with ARQ + Redis
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
- [ ] External API enrichment
- [ ] Multi-model support
- [ ] Team collaboration

---

## Next Steps

1. **Restructure directory**: Move `backend/src/` → `backend/app/`
2. **Update models**: Add User, DocumentChunk; expand Variable, Document, Extraction
3. **Implement ARQ**: Replace BackgroundTasks with ARQ + Redis workers
4. **Add auth**: JWT auth middleware + RLS setup
5. **Fix LLM pipeline**: Wire through LangChain, add post-processing stage
6. **Add agents**: Create co-pilot, extractor, refiner modules
