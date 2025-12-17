---

description: "UI Alignment Tasks - Frontend-Workflow Gap Fixes"
---

# Tasks: UI Alignment & Backend Integration

**Input**: Frontend-workflow alignment analysis and backend API specifications
**Context**: Align existing frontend implementation with USER_WORKFLOW.md requirements and backend APIs
**Target**: Complete alignment for production-ready MVP

**Tests**: Not required for UI alignment tasks - manual testing sufficient

**Organization**: Tasks grouped by user story to maintain independent testability

**Workflow Mapping**: Each phase maps to USER_WORKFLOW.md steps (Steps 1-5)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for frontend, `backend/src/` for backend
- All paths are absolute from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: API client infrastructure and type alignment

- [ ] T001 Create real API client base in frontend/src/services/realApi.ts
- [ ] T002 [P] Create API type mappers in frontend/src/lib/mappers/apiMappers.ts
- [ ] T003 [P] Add backend type definitions in frontend/src/types/backend.ts
- [ ] T004 Configure API base URL and environment variables in frontend/.env.local

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core type system and mapping infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story alignment can proceed until type system is unified

- [ ] T005 Update Project type to align with backend schema in frontend/src/types/project.ts
- [ ] T006 [P] Update Variable type to support backend VariableType enum in frontend/src/types/schema.ts
- [ ] T007 [P] Update ExtractionResult type to support backend extraction structure in frontend/src/types/extraction.ts
- [ ] T008 [P] Update ProcessingJob type to align with backend JobDetail schema in frontend/src/types/processing.ts
- [ ] T009 Create status mapper (CREATED→draft, PROCESSING→processing, etc.) in frontend/src/lib/mappers/statusMapper.ts
- [ ] T010 Create variable type mapper (DATE→date, CATEGORY→classification, etc.) in frontend/src/lib/mappers/variableTypeMapper.ts
- [ ] T011 Create confidence score transformer (0-1 to 0-100) in frontend/src/lib/mappers/confidenceMapper.ts
- [ ] T012 Implement extraction results aggregator (group by document) in frontend/src/lib/mappers/extractionAggregator.ts

**Checkpoint**: Type system unified - user story UI updates can now proceed in parallel

---

## Phase 3: User Story 1 - Project Setup & Document Input (Priority: P1) 🎯 MVP

**Goal**: Align project creation and document upload with backend APIs

**Workflow Step**: Step 1 (Project Setup & Document Input)

**Independent Test**: User can create project via real API, upload documents to backend, see document list from backend

### Implementation for User Story 1

- [ ] T013 [P] [US1] Add language and domain fields to ProjectSetupForm in frontend/src/components/projects/ProjectSetupForm.tsx
- [ ] T014 [P] [US1] Update project creation to call POST /api/v1/projects in frontend/src/app/(dashboard)/projects/new/page.tsx
- [ ] T015 [US1] Replace mock document upload with real POST /api/v1/projects/{id}/documents in frontend/src/app/(dashboard)/projects/[id]/documents/page.tsx
- [ ] T016 [US1] Update document list to fetch from GET /api/v1/projects/{id}/documents in frontend/src/components/workflow/step1/DocumentList.tsx
- [ ] T017 [US1] Update document delete to call DELETE /api/v1/documents/{id} in frontend/src/components/workflow/step1/DocumentList.tsx
- [ ] T018 [US1] Add file upload progress tracking using backend upload status in frontend/src/components/workflow/step1/DocumentUploader.tsx
- [ ] T019 [US1] Add cloud folder connection UI (Google Drive placeholder) in frontend/src/components/workflow/step1/CloudConnector.tsx (NEW FILE)
- [ ] T020 [US1] Add document grid view toggle option in frontend/src/app/(dashboard)/projects/[id]/documents/page.tsx

**Checkpoint**: Project creation and document upload fully functional with backend

---

## Phase 4: User Story 2 - Schema Definition Wizard (Priority: P1) 🎯 MVP

**Goal**: Align schema wizard with backend variable types and API

**Workflow Step**: Step 2 (Schema Definition Wizard)

**Independent Test**: User can create variables via wizard, backend generates prompts, variables persist correctly

### Implementation for User Story 2

- [ ] T021 [P] [US2] Add LOCATION variable type option to VariableForm in frontend/src/components/workflow/step2/VariableForm.tsx
- [ ] T022 [P] [US2] Update classification rules to use Dict[str, Any] format in frontend/src/components/workflow/step2/VariableForm.tsx
- [ ] T023 [US2] Replace mock variable creation with POST /api/v1/projects/{id}/variables in frontend/src/components/workflow/step2/SchemaWizard.tsx
- [ ] T024 [US2] Update variable edit to call PUT /api/v1/variables/{id} in frontend/src/components/workflow/step2/SchemaWizard.tsx
- [ ] T025 [US2] Update variable delete to call DELETE /api/v1/variables/{id} in frontend/src/components/workflow/step2/SchemaWizard.tsx
- [ ] T026 [US2] Fetch variables from GET /api/v1/projects/{id}/variables on wizard load in frontend/src/components/workflow/step2/SchemaWizard.tsx
- [ ] T027 [US2] Display backend-generated prompt suggestions in AI suggestion area in frontend/src/components/workflow/step2/VariableForm.tsx

**Checkpoint**: Schema wizard creates real variables with backend prompt generation

---

## Phase 5: User Story 3 - Schema Review & Confirmation (Priority: P1) 🎯 MVP

**Goal**: Add schema approval endpoint integration and enhance review UI

**Workflow Step**: Step 3 (Schema Review & Confirmation)

**Independent Test**: User can review schema, see backend-generated prompts, approve schema for processing

### Implementation for User Story 3

- [ ] T028 [P] [US3] Add drag-and-drop reordering implementation in frontend/src/components/workflow/step3/SchemaTable.tsx
- [ ] T029 [P] [US3] Display variable order field and allow reordering in frontend/src/components/workflow/step3/SchemaTable.tsx
- [ ] T030 [US3] Add expandable prompt preview showing backend prompt in frontend/src/components/workflow/step3/SchemaTable.tsx
- [ ] T031 [US3] Implement schema approval via POST /api/v1/projects/{id}/schema/approve in frontend/src/app/(dashboard)/projects/[id]/schema/review/page.tsx
- [ ] T032 [US3] Add table preview mode showing column headers in frontend/src/components/workflow/step3/SchemaPreviewTable.tsx (NEW FILE)

**Checkpoint**: Schema review shows accurate backend data and approves via API

---

## Phase 6: User Story 4 - Sample Testing & Full Processing (Priority: P1) 🎯 MVP

**Goal**: Connect processing UI to backend job system and real-time updates

**Workflow Step**: Step 4 (Processing - Sample & Full)

**Independent Test**: User can run sample processing, see real results, approve and run full processing with real-time progress

### Implementation for User Story 4

- [ ] T033 [P] [US4] Replace sample processing with POST /api/v1/projects/{id}/processing/sample in frontend/src/components/workflow/step4/SampleTesting.tsx
- [ ] T034 [P] [US4] Replace full processing with POST /api/v1/projects/{id}/processing/full in frontend/src/components/workflow/step4/FullProcessing.tsx
- [ ] T035 [US4] Implement job status polling via GET /api/v1/jobs/{id} in frontend/src/components/workflow/step4/FullProcessing.tsx
- [ ] T036 [US4] Display real-time logs from backend JobDetail.recent_logs in frontend/src/components/workflow/step4/ProcessingLog.tsx
- [ ] T037 [US4] Show current document being processed from backend in frontend/src/components/workflow/step4/FullProcessing.tsx
- [ ] T038 [US4] Add job cancellation UI calling DELETE /api/v1/jobs/{id} in frontend/src/components/workflow/step4/FullProcessing.tsx
- [ ] T039 [US4] Fetch sample results from GET /api/v1/jobs/{id}/results in frontend/src/components/workflow/step4/SampleTesting.tsx
- [ ] T040 [US4] Transform backend extractions to frontend format using aggregator in frontend/src/components/workflow/step4/SampleTesting.tsx
- [ ] T041 [US4] Add extraction feedback UI (correct/incorrect flags) in frontend/src/components/workflow/step4/SampleResultsTable.tsx (NEW FILE)

**Checkpoint**: Processing runs with real backend, shows live progress, displays actual extraction results

---

## Phase 7: User Story 5 - Results Review & Export (Priority: P1) 🎯 MVP

**Goal**: Display aggregated results from backend and enable real export

**Workflow Step**: Step 5 (Results & Export)

**Independent Test**: User can view all extraction results, filter by confidence, export to CSV via backend

### Implementation for User Story 5

- [ ] T042 [P] [US5] Fetch results from GET /api/v1/projects/{id}/results in frontend/src/app/(dashboard)/projects/[id]/results/page.tsx
- [ ] T043 [P] [US5] Transform aggregated backend results to frontend format in frontend/src/app/(dashboard)/projects/[id]/results/page.tsx
- [ ] T044 [US5] Update confidence scores from 0-1 to 0-100 scale in frontend/src/components/workflow/step5/ResultsTable.tsx
- [ ] T045 [US5] Add flagging UI (flag button per row) in frontend/src/components/workflow/step5/ResultsTable.tsx
- [ ] T046 [US5] Implement flag/unflag via PUT /api/v1/extractions/{id}/flag in frontend/src/components/workflow/step5/FlagButton.tsx (NEW FILE)
- [ ] T047 [US5] Add filter by flagged extractions in frontend/src/components/workflow/step5/ConfidenceFilter.tsx
- [ ] T048 [US5] Replace CSV generation with POST /api/v1/projects/{id}/export in frontend/src/components/workflow/step5/ExportModal.tsx
- [ ] T049 [US5] Add Excel and JSON export format options in frontend/src/components/workflow/step5/ExportModal.tsx
- [ ] T050 [US5] Add export flagged-only option in frontend/src/components/workflow/step5/ExportModal.tsx

**Checkpoint**: Results page displays real backend data, flagging works, export generates real files

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories and production readiness

- [ ] T051 [P] Add API error handling with user-friendly messages in frontend/src/lib/errors/apiErrorHandler.ts
- [ ] T052 [P] Add loading states for all API calls in frontend/src/hooks/useApiLoading.ts
- [ ] T053 [P] Add retry logic for failed API requests in frontend/src/services/realApi.ts
- [ ] T054 [P] Update environment configuration for production in frontend/.env.production
- [ ] T055 [P] Add API response caching for project/document lists in frontend/src/lib/cache/apiCache.ts
- [ ] T056 Remove or flag all mock API usage with console warnings in frontend/src/services/api.ts
- [ ] T057 Add backend health check on app initialization in frontend/src/app/layout.tsx
- [ ] T058 Update all error boundaries to handle API errors in frontend/src/components/layout/ErrorBoundary.tsx
- [ ] T059 Add workflow navigation validation (prevent skipping steps) in frontend/src/lib/validators/workflowValidator.ts
- [ ] T060 [P] Update README with API integration instructions in frontend/README.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Foundational
  - US2 (Phase 4): Can start after Foundational (independent)
  - US3 (Phase 5): Depends on US2 completion (needs variables to review)
  - US4 (Phase 6): Depends on US3 completion (needs approved schema)
  - US5 (Phase 7): Depends on US4 completion (needs processing results)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - only depends on Foundational
- **User Story 2 (P1)**: Independent - only depends on Foundational
- **User Story 3 (P1)**: Depends on US2 (must have variables to review)
- **User Story 4 (P1)**: Depends on US3 (must have approved schema)
- **User Story 5 (P1)**: Depends on US4 (must have processing results)

### Within Each User Story

- API integration tasks before UI update tasks
- Type transformations before data display
- CRUD operations in order: Read → Create → Update → Delete
- Core implementation before enhancement features

### Parallel Opportunities

- All Setup tasks (T001-T004) can run in parallel
- All Foundational type updates (T005-T008) can run in parallel
- All Foundational mappers (T009-T012) can run in parallel
- Within US1: T013-T014 and T015-T017 can run in parallel
- Within US2: T021-T022 and T023-T026 can run in parallel
- Within US3: T028-T030 can run in parallel
- Within US4: T033-T034 can run in parallel
- Within US5: T042-T044 can run in parallel
- All Polish phase tasks (T051-T060) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch these tasks together after Foundational phase:
Task: "[US1] Add language and domain fields to ProjectSetupForm"
Task: "[US1] Update project creation to call POST /api/v1/projects"

# Then these together:
Task: "[US1] Replace mock document upload with real API"
Task: "[US1] Update document list to fetch from backend"
Task: "[US1] Update document delete to call DELETE endpoint"
```

---

## Implementation Strategy

### MVP First (Critical Path)

1. Complete Phase 1: Setup (API client infrastructure)
2. Complete Phase 2: Foundational (type system alignment)
3. Complete Phase 3: User Story 1 (basic project setup works)
4. **STOP and VALIDATE**: Test project creation and document upload with backend
5. Proceed through US2 → US3 → US4 → US5 sequentially

### Incremental Delivery

1. Setup + Foundational → API client ready
2. Add User Story 1 → Test independently → Users can create projects with backend
3. Add User Story 2 → Test independently → Users can define schema with backend
4. Add User Story 3 → Test independently → Users can approve schema
5. Add User Story 4 → Test independently → Users can process documents
6. Add User Story 5 → Test independently → **COMPLETE MVP** - full workflow functional
7. Polish phase → Production-ready

### Testing Checkpoints

After each user story phase:
1. Verify API calls are made correctly (check Network tab)
2. Verify data persists to backend (check via API directly)
3. Verify UI displays backend data correctly
4. Verify error states work (disconnect backend, check UI)
5. Verify all previous user stories still work

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for workflow alignment
- Each user story implements one step of USER_WORKFLOW.md
- Remove/deprecate mock API after real API integration is complete
- Backend must implement missing endpoints (schema approval, flagging, convenience endpoints) - see backend/REMAINING_ALIGNMENT_TASKS.md
- Confidence scale: Backend needs to change from 0-1 to 0-100 OR frontend transforms on read
- All tasks include exact file paths for immediate implementation
- NEW FILE markers indicate components that don't exist yet
- Stop at any checkpoint to validate story independently before proceeding

---

## Backend Prerequisites (Must be completed first)

**⚠️ These backend tasks BLOCK frontend implementation:**

From `backend/REMAINING_ALIGNMENT_TASKS.md`:

- [ ] **T2**: Change confidence scale from 0-1 to 0-100 (BLOCKS Phase 2, T011)
- [ ] **T3**: Add flagging support to Extraction model (BLOCKS US5, T045-T046)
- [ ] **T4**: Add flag/unflag endpoint (BLOCKS US5, T046)
- [ ] **T5**: Add aggregated results endpoint (BLOCKS US5, T042)
- [ ] **T6**: Add schema approval endpoint (BLOCKS US3, T031)
- [ ] **T7**: Add convenience processing endpoints (BLOCKS US4, T033-T034)

**Recommendation**: Complete backend tasks T2, T6, T7 before starting frontend alignment. Tasks T3-T5 can wait until Phase 7 (US5).

---

## Summary

- **Total Tasks**: 60 UI alignment tasks
- **Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phase
- **Critical Path**: Setup → Foundational → US1 → US2 → US3 → US4 → US5 → Polish
- **Estimated Effort**:
  - Setup: 2 hours
  - Foundational: 4 hours
  - User Story 1: 6 hours
  - User Story 2: 5 hours
  - User Story 3: 4 hours
  - User Story 4: 7 hours
  - User Story 5: 6 hours
  - Polish: 4 hours
  - **Total: ~38 hours** (assuming backend endpoints exist)

- **MVP Scope**: Phases 1-7 (T001-T050) = Core workflow functional
- **Production Ready**: All phases (T001-T060) = Polished, error-handled, production-ready

**Format Validation**: ✅ All 60 tasks follow the required checklist format with checkbox, ID, labels, and file paths
