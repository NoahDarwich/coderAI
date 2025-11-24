# Tasks: Complete User Workflow (5 Steps)

**Input**: Design documents from `/specs/001-complete-user-workflow/`
**Prerequisites**: plan.md (✓), spec.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

**Tests**: NOT requested in feature specification - manual testing only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Workflow Mapping**: Each phase maps to user workflow steps from USER_WORKFLOW.md (Steps 1-5) to ensure features align with the canonical user journey.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend-only**: All paths in `frontend/src/`
- Paths shown below use Next.js 15 App Router structure

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize Next.js project and install all dependencies

- [X] T001 Create Next.js 15 project in frontend/ directory with TypeScript, Tailwind CSS, App Router
- [X] T002 Install core dependencies: zustand, @tanstack/react-query, @tanstack/react-table, react-dropzone, zod, react-hook-form, @hookform/resolvers, date-fns
- [X] T003 [P] Initialize shadcn/ui with default configuration (style: Default, base color: Slate)
- [X] T004 [P] Install shadcn/ui components: button, card, dialog, form, input, select, table, tabs, toast, progress, badge, dropdown-menu, separator
- [X] T005 [P] Configure TypeScript with strict mode in tsconfig.json
- [X] T006 [P] Configure Tailwind CSS in tailwind.config.ts (include all src paths)
- [X] T007 Create directory structure: app/(dashboard), components/{ui,workflow,layout}, lib, services, types, mocks, store in frontend/src/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core TypeScript types, mock data, and service layer that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 [P] Create Project type in frontend/src/types/project.ts
- [X] T009 [P] Create Document type in frontend/src/types/document.ts
- [X] T010 [P] Create Schema and Variable types in frontend/src/types/schema.ts
- [X] T011 [P] Create ExtractionResult and ExtractedValue types in frontend/src/types/extraction.ts
- [X] T012 [P] Create ProcessingJob and ProcessingLog types in frontend/src/types/processing.ts
- [X] T013 [P] Create ExportConfig and ExportResult types in frontend/src/types/export.ts
- [X] T014 [P] Create API response wrapper types in frontend/src/types/api.ts
- [X] T015 Create types/index.ts exporting all types from frontend/src/types/
- [X] T016 [P] Create mock projects data (5 projects, various states) in frontend/src/mocks/mockProjects.ts
- [X] T017 [P] Create mock documents data (20+ documents, PDF/DOCX/TXT) in frontend/src/mocks/mockDocuments.ts
- [X] T018 [P] Create mock schemas data (2 schemas, different variable types) in frontend/src/mocks/mockSchemas.ts
- [X] T019 [P] Create mock extraction results (5 results, various confidence scores) in frontend/src/mocks/mockExtractions.ts
- [X] T020 [P] Create mock processing jobs (3 jobs, various statuses) in frontend/src/mocks/mockProcessingJobs.ts
- [X] T021 Create mock data README documenting all mock data in frontend/src/mocks/README.md
- [X] T022 Implement Projects API in frontend/src/services/newMockApi.ts (list, get, create, update, delete)
- [X] T023 Implement Documents API in frontend/src/services/newMockApi.ts (list, get, upload, delete, getContent)
- [X] T024 Implement Schema API in frontend/src/services/newMockApi.ts (get, save, confirm, addVariable, updateVariable, deleteVariable, reorderVariables)
- [X] T025 Implement Processing API in frontend/src/services/newMockApi.ts (startSample, startFull, getJob, cancelJob)
- [X] T026 Implement Results API in frontend/src/services/newMockApi.ts (list, get, flag)
- [X] T027 Implement Export API in frontend/src/services/newMockApi.ts (generate, download)
- [X] T028 Create API interface wrapper in frontend/src/services/api.ts (exports api object)
- [X] T029 [P] Create projectStore with Zustand in frontend/src/store/projectStore.ts
- [X] T030 [P] Create workflowStore with Zustand in frontend/src/store/workflowStore.ts
- [X] T031 [P] Create schemaWizardStore with Zustand in frontend/src/store/schemaWizardStore.ts
- [X] T032 [P] Create utility functions in frontend/src/lib/utils.ts (cn, formatDate, etc.)
- [X] T033 [P] Create Zod validation schemas in frontend/src/lib/validations.ts
- [X] T034 [P] Create WorkflowProgress component in frontend/src/components/layout/WorkflowProgress.tsx
- [X] T035 [P] Create ErrorBoundary component in frontend/src/components/layout/ErrorBoundary.tsx
- [X] T036 Create dashboard layout in frontend/src/app/(dashboard)/layout.tsx with navigation

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Project Setup & Document Input (Priority: P1) 🎯 MVP

**Goal**: Enable users to create projects and upload documents

**Workflow Step**: Step 1 (Project Setup & Document Input)

**Independent Test**: User can create a project, select scale (small/large), upload documents via drag-and-drop, see document list with count, and proceed to next step.

### Implementation for User Story 1

- [X] T037 [P] [US1] Create ProjectSetupForm component in frontend/src/components/workflow/step1/ProjectSetupForm.tsx
- [X] T038 [P] [US1] Create DocumentUploader component with react-dropzone in frontend/src/components/workflow/step1/DocumentUploader.tsx
- [X] T039 [P] [US1] Create DocumentList component in frontend/src/components/workflow/step1/DocumentList.tsx
- [X] T040 [US1] Create projects list page in frontend/src/app/(dashboard)/projects/page.tsx
- [X] T041 [US1] Create new project page with ProjectSetupForm in frontend/src/app/(dashboard)/projects/new/page.tsx
- [X] T042 [US1] Create project overview page in frontend/src/app/(dashboard)/projects/[id]/page.tsx
- [X] T043 [US1] Create document upload page in frontend/src/app/(dashboard)/projects/[id]/documents/page.tsx
- [X] T044 [US1] Add error states and loading states to all US1 components
- [X] T045 [US1] Add ARIA labels and keyboard navigation to ProjectSetupForm
- [X] T046 [US1] Add ARIA labels and keyboard navigation to DocumentUploader
- [ ] T047 [US1] Test document upload flow manually (drag-and-drop, file selection, delete)
- [ ] T048 [US1] Test project creation with localStorage persistence

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Schema Definition Wizard (Priority: P1) 🎯 MVP

**Goal**: Enable users to define extraction schema through multi-step wizard

**Workflow Step**: Step 2 (Schema Definition Wizard)

**Independent Test**: User can navigate wizard to define variables (name, type, extraction instructions, classification rules), add multiple variables, edit/delete/reorder them, and see AI suggestions.

### Implementation for User Story 2

- [X] T049 [P] [US2] Create VariableForm component in frontend/src/components/workflow/step2/VariableForm.tsx
- [X] T050 [P] [US2] Create WizardNavigation component in frontend/src/components/workflow/step2/WizardNavigation.tsx
- [X] T051 [US2] Create SchemaWizard container component in frontend/src/components/workflow/step2/SchemaWizard.tsx
- [X] T052 [US2] Implement wizard state management in schemaWizardStore (add, update, delete, reorder variables)
- [X] T053 [US2] Create schema wizard page in frontend/src/app/(dashboard)/projects/[id]/schema/page.tsx
- [X] T054 [US2] Implement variable type selector with validation (text, number, date, category, boolean)
- [X] T055 [US2] Implement classification rules input for categorical variables
- [X] T056 [US2] Implement mock AI suggestions based on variable name and type
- [X] T057 [US2] Add progress indicator showing "N variables defined"
- [X] T058 [US2] Add error states and loading states to wizard components
- [X] T059 [US2] Add ARIA labels and keyboard navigation to VariableForm
- [ ] T060 [US2] Add ARIA labels and keyboard navigation to wizard navigation (Back, Next, Add Another)
- [ ] T061 [US2] Test wizard flow manually (add variables, navigate back, edit, delete)
- [ ] T062 [US2] Test wizard state persistence across page refreshes

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Schema Review & Confirmation (Priority: P1) 🎯 MVP

**Goal**: Enable users to review and confirm schema before processing

**Workflow Step**: Step 3 (Schema Review & Confirmation)

**Independent Test**: User can view complete schema as table preview, see all variables with types and rules, edit any variable, delete variables, reorder via drag-and-drop, and approve for processing.

### Implementation for User Story 3

- [X] T063 [P] [US3] Create SchemaTable component in frontend/src/components/workflow/step3/SchemaTable.tsx
- [X] T064 [P] [US3] Create VariableEditor component (edit modal) in frontend/src/components/workflow/step3/VariableEditor.tsx
- [X] T065 [US3] Create SchemaReview container component in frontend/src/components/workflow/step3/SchemaReview.tsx
- [X] T066 [US3] Create schema review page in frontend/src/app/(dashboard)/projects/[id]/schema/review/page.tsx
- [X] T067 [US3] Implement table preview with column headers from schema
- [X] T068 [US3] Implement expandable variable details (type, extraction rules, classification rules)
- [X] T069 [US3] Implement edit action that returns to wizard at specific variable
- [X] T070 [US3] Implement delete variable action with confirmation dialog
- [X] T071 [US3] Implement drag-and-drop column reordering with @dnd-kit or react-beautiful-dnd
- [X] T072 [US3] Implement "Confirm and Proceed" button with schema confirmation
- [X] T073 [US3] Add error states and loading states to review components
- [ ] T074 [US3] Add ARIA labels and keyboard navigation to SchemaTable
- [ ] T075 [US3] Test schema review flow manually (view, edit, delete, reorder, confirm)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Sample Testing & Full Processing (Priority: P1) 🎯 MVP

**Goal**: Enable sample testing then full processing with real-time progress

**Workflow Step**: Step 4 (Processing - Sample & Full)

**Independent Test**: User can run sample extraction on 10-20 documents, view results in table format, flag errors, optionally refine schema, then run full processing with progress tracking.

### Implementation for User Story 4

- [X] T076 [P] [US4] Create SampleTesting component in frontend/src/components/workflow/step4/SampleTesting.tsx
- [X] T077 [P] [US4] Create FullProcessing component in frontend/src/components/workflow/step4/FullProcessing.tsx
- [X] T078 [P] [US4] Create ProcessingLog component in frontend/src/components/workflow/step4/ProcessingLog.tsx
- [X] T079 [US4] Create processing page in frontend/src/app/(dashboard)/projects/[id]/process/page.tsx
- [X] T080 [US4] Implement sample size selector (10-20 documents)
- [X] T081 [US4] Implement mock sample processing with setTimeout simulation
- [X] T082 [US4] Implement sample results table with confidence indicators (🟢 🟡 🔴)
- [X] T083 [US4] Implement cell flagging (checkmark/X buttons for correct/incorrect)
- [X] T084 [US4] Implement "Refine Schema" button (returns to wizard)
- [X] T085 [US4] Implement "Approve for Full Processing" button
- [X] T086 [US4] Implement mock full processing with setTimeout and progress updates
- [X] T087 [US4] Implement real-time processing log with document names, timestamps, status
- [X] T088 [US4] Implement progress bar (overall percentage)
- [ ] T089 [US4] Implement background processing (state persists when user navigates away)
- [X] T090 [US4] Implement toast notification on processing completion
- [X] T091 [US4] Implement error handling (log errors, continue processing other documents)
- [X] T092 [US4] Add error states and loading states to processing components
- [ ] T093 [US4] Add ARIA labels and keyboard navigation to processing controls
- [ ] T094 [US4] Test sample processing flow manually (select size, run, review, flag, refine)
- [ ] T095 [US4] Test full processing flow manually (approve, watch progress, navigate away, return, completion)

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Results Review & Export (Priority: P1) 🎯 MVP

**Goal**: Enable users to review results and export to CSV

**Workflow Step**: Step 5 (Results & Export)

**Independent Test**: User can view complete results in sortable/filterable table, see confidence scores, filter by confidence threshold, select export format (CSV wide/long), configure export options, and download file.

### Implementation for User Story 5

- [X] T096 [P] [US5] Create ResultsTable component with TanStack Table in frontend/src/components/workflow/step5/ResultsTable.tsx
- [X] T097 [P] [US5] Create ExportModal component in frontend/src/components/workflow/step5/ExportModal.tsx
- [X] T098 [P] [US5] Create ConfidenceFilter component in frontend/src/components/workflow/step5/ConfidenceFilter.tsx
- [X] T099 [US5] Create results page in frontend/src/app/(dashboard)/projects/[id]/results/page.tsx
- [X] T100 [US5] Implement sortable table headers with TanStack Table
- [X] T101 [US5] Implement global filter/search functionality
- [X] T102 [US5] Implement confidence threshold filter (slider or input)
- [X] T103 [US5] Implement confidence indicators (🟢 high ≥85%, 🟡 medium 70-84%, 🔴 low <70%)
- [X] T104 [US5] Implement cell click to view source document text (modal)
- [X] T105 [US5] Implement data summary statistics (row count, completion %)
- [X] T106 [US5] Implement export configuration form (format: CSV wide/long, options: include confidence, include source text)
- [X] T107 [US5] Implement CSV generation for wide format (1 row per document)
- [X] T108 [US5] Implement CSV generation for long format (1 row per extracted field)
- [X] T109 [US5] Implement file download with Blob API
- [X] T110 [US5] Add error states and loading states to results components
- [ ] T111 [US5] Add ARIA labels and keyboard navigation to ResultsTable
- [ ] T112 [US5] Test results table manually (sort, filter, click cells, view source text)
- [ ] T113 [US5] Test export flow manually (configure format, options, download, verify CSV)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T114 [P] Create landing page in frontend/src/app/page.tsx
- [X] T115 [P] Create DashboardNav component in frontend/src/components/layout/DashboardNav.tsx
- [X] T116 [P] Update root layout in frontend/src/app/layout.tsx with fonts, metadata
- [ ] T117 Add loading.tsx files for automatic loading states in all route segments
- [ ] T118 Add error.tsx files for error boundaries in all route segments
- [ ] T119 Implement responsive layouts for tablet (768px) across all pages
- [ ] T120 Implement mobile-friendly interactions across all pages
- [ ] T121 Run accessibility audit with axe-devtools on all 5 workflow pages
- [ ] T122 Fix any WCAG 2.1 AA violations found in accessibility audit
- [ ] T123 Test keyboard navigation across entire workflow (Tab, Enter, Space, Escape)
- [ ] T124 Test screen reader compatibility (VoiceOver or NVDA) across entire workflow
- [ ] T125 Run TypeScript build (npm run build) and fix all errors
- [ ] T126 Test complete user workflow end-to-end manually (all 5 steps)
- [ ] T127 Verify localStorage persistence across page refreshes
- [ ] T128 Test error states for all API failures (mock errors)
- [ ] T129 Optimize bundle size (check with next build analyzer)
- [ ] T130 Deploy to Vercel and verify production build

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Should integrate with US1 (requires project to exist)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Should integrate with US2 (requires schema from wizard)
- **User Story 4 (P1)**: Can start after Foundational (Phase 2) - Should integrate with US3 (requires confirmed schema)
- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - Should integrate with US4 (requires processing results)

**Recommendation**: Implement sequentially (US1 → US2 → US3 → US4 → US5) for best integration testing.

### Within Each User Story

- Components marked [P] can run in parallel (different files)
- Page creation depends on components being ready
- Testing happens after all components and pages are complete
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (Phase 1) marked [P] can run in parallel
- All Foundational tasks (Phase 2) marked [P] can run in parallel
- Within each user story, all tasks marked [P] can run in parallel
- Components within a story can be built in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch all components for User Story 1 together:
Task: "Create ProjectSetupForm component in frontend/src/components/workflow/step1/ProjectSetupForm.tsx"
Task: "Create DocumentUploader component with react-dropzone in frontend/src/components/workflow/step1/DocumentUploader.tsx"
Task: "Create DocumentList component in frontend/src/components/workflow/step1/DocumentList.tsx"

# Then create pages that use these components:
Task: "Create projects list page in frontend/src/app/(dashboard)/projects/page.tsx"
Task: "Create new project page with ProjectSetupForm in frontend/src/app/(dashboard)/projects/new/page.tsx"
# etc.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy to Vercel for demo

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Test independently → Deploy
4. Add User Story 3 → Test independently → Deploy
5. Add User Story 4 → Test independently → Deploy
6. Add User Story 5 → Test independently → Deploy (Complete workflow!)
7. Phase 8: Polish → Final production deployment

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Components for User Story 1
   - Developer B: Components for User Story 2
   - Developer C: Components for User Story 3
3. Integrate stories sequentially (test US1, then add US2, then add US3, etc.)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **NO backend work** - all tasks are frontend only with mock data
- **NO tests requested** - manual testing only for Phase 1
- Verify TypeScript errors frequently (`npm run build`)
- Reference USER_WORKFLOW.md for exact UX requirements

---

## Summary Statistics

**Total Tasks**: 130
**Tasks by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 29 tasks
- Phase 3 (US1 - Project Setup): 12 tasks
- Phase 4 (US2 - Schema Wizard): 14 tasks
- Phase 5 (US3 - Schema Review): 13 tasks
- Phase 6 (US4 - Processing): 20 tasks
- Phase 7 (US5 - Results & Export): 18 tasks
- Phase 8 (Polish): 17 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel
**Independent Test Criteria**: Each user story (US1-US5) has explicit test criteria
**Suggested MVP Scope**: User Story 1 only (T001-T048) = 48 tasks
**Full 5-Step Workflow**: All tasks (T001-T130) = 130 tasks

**All tasks follow checklist format**: ✅ Verified
**All file paths included**: ✅ Verified
**Ready for implementation**: ✅ Yes
