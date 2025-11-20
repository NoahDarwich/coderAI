# Tasks: Research Automation Tool - Phase 1 Frontend MVP

**Input**: Design documents from root directory and `.specify/`
**Prerequisites**: plan.md, MVP-SPEC.md, API-SPECIFICATION.md, TECH-STACK-DECISION.md, FRONTEND-DESIGN.md

**Tests**: Tests are NOT explicitly requested in the MVP spec. This task list focuses on implementation only.

**Organization**: Tasks are grouped by feature/page to enable incremental delivery of working UI components with mock data.

## Format: `- [ ] [ID] [P?] [Feature] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Feature]**: Which feature/page this task belongs to
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` for all application code
- **Project structure**: Next.js 15 App Router with TypeScript

---

## Phase 1: Project Setup & Configuration

**Purpose**: Initialize Next.js project with all required dependencies and tooling

- [X] T001 Create Next.js 15 project with TypeScript and App Router in frontend/
- [X] T002 [P] Configure Tailwind CSS 4.0 in frontend/tailwind.config.ts
- [X] T003 [P] Setup TypeScript strict mode in frontend/tsconfig.json
- [X] T004 [P] Install and initialize shadcn/ui CLI in frontend/
- [X] T005 [P] Install core dependencies (Zustand, TanStack Query, React Hook Form, Zod) in frontend/package.json
- [X] T006 [P] Create project folder structure (app/, components/, lib/, types/) in frontend/src/
- [X] T007 [P] Setup globals.css with Tailwind imports in frontend/src/styles/globals.css
- [X] T008 [P] Configure environment variables template in frontend/.env.example

**Checkpoint**: ✅ COMPLETE - Project structure created, builds successfully with zero errors

---

## Phase 2: Core Infrastructure (Foundational)

**Purpose**: Base components, types, and utilities that ALL features depend on

**⚠️ CRITICAL**: No feature implementation can begin until this phase is complete

- [X] T009 Define core TypeScript types in frontend/src/lib/types/api.ts (User, Project, Document, Schema, ExtractionResult, Job)
- [X] T010 [P] Define additional TypeScript types in frontend/src/lib/types/project.ts
- [X] T011 [P] Define additional TypeScript types in frontend/src/lib/types/document.ts
- [X] T012 [P] Define additional TypeScript types in frontend/src/lib/types/extraction.ts
- [X] T013 Create utility functions in frontend/src/lib/utils/validation.ts (form validation, file type checking)
- [X] T014 [P] Create formatting utilities in frontend/src/lib/utils/formatting.ts (date, file size, numbers)
- [X] T015 [P] Create export utilities in frontend/src/lib/utils/export.ts (CSV generation)
- [X] T016 Install shadcn/ui components: button, input, card, table in frontend/src/components/ui/
- [X] T017 [P] Install shadcn/ui components: dialog, dropdown-menu, badge in frontend/src/components/ui/
- [X] T018 [P] Install shadcn/ui components: tooltip, slider, checkbox in frontend/src/components/ui/
- [X] T019 [P] Install shadcn/ui components: tabs, sonner, label in frontend/src/components/ui/
- [X] T020 Create root layout component in frontend/src/app/layout.tsx
- [X] T021 Create shared Header component in frontend/src/components/layout/Header.tsx
- [X] T022 [P] Create shared Footer component in frontend/src/components/layout/Footer.tsx
- [X] T023 [P] Create shared Sidebar component in frontend/src/components/layout/Sidebar.tsx (for project navigation)

**Checkpoint**: ✅ COMPLETE - Foundation ready - feature pages can now be built

---

## Phase 3: Mock Data Service Layer

**Purpose**: Create mock data and service layer for Phase 1 (frontend-only operation)

**Goal**: Enable all UI features to work with realistic mock data before backend integration

- [X] T024 Create mock project data in frontend/src/mocks/projects.ts (5 sample projects with varying states)
- [X] T025 [P] Create mock document data in frontend/src/mocks/documents.ts (20 sample documents)
- [X] T026 [P] Create mock conversation data in frontend/src/mocks/conversations.ts (predefined chat flow)
- [X] T027 [P] Create mock schema data in frontend/src/mocks/schema.ts (generated schema examples)
- [X] T028 [P] Create mock extraction results data in frontend/src/mocks/results.ts (100 extraction results)
- [X] T029 Create mockApi service in frontend/src/services/mockApi.ts (implements API interface with mock data)
- [X] T030 Create API service abstraction in frontend/src/services/api.ts (imports mockApi for Phase 1)

**Checkpoint**: ✅ COMPLETE - Mock data service ready for component integration

---

## Phase 4: Landing & Authentication Pages

**Purpose**: User registration and login (no backend auth in Phase 1, just UI)

**Goal**: User can access landing page and "authenticate" to dashboard

**Independent Test**: Navigate to landing page → login → redirect to dashboard

- [X] T031 Create landing page in frontend/src/app/page.tsx (hero, CTA to dashboard)
- [X] T032 [P] Create auth layout in frontend/src/app/(auth)/layout.tsx
- [X] T033 Create login page in frontend/src/app/(auth)/login/page.tsx
- [X] T034 [P] Create register page in frontend/src/app/(auth)/register/page.tsx
- [X] T035 Create auth store with Zustand in frontend/src/lib/store/authStore.ts (mock authentication)
- [X] T036 Create login form component in frontend/src/components/auth/LoginForm.tsx
- [X] T037 [P] Create register form component in frontend/src/components/auth/RegisterForm.tsx
- [X] T038 Add route protection middleware in frontend/src/middleware.ts

**Checkpoint**: Auth flow complete - users can "login" and access protected routes

---

## Phase 5: Dashboard & Project Management

**Purpose**: Project list and project creation

**Goal**: User can view projects, create new projects, and navigate to project detail pages

**Independent Test**: View project list → create new project → delete project → navigate to project

- [X] T039 Create dashboard layout in frontend/src/app/(dashboard)/layout.tsx
- [X] T040 Create projects list page in frontend/src/app/(dashboard)/projects/page.tsx
- [X] T041 Create project store with Zustand in frontend/src/lib/store/projectStore.ts
- [X] T042 Create ProjectCard component in frontend/src/components/projects/ProjectCard.tsx
- [X] T043 [P] Create ProjectList component in frontend/src/components/projects/ProjectList.tsx
- [X] T044 [P] Create NewProjectDialog component in frontend/src/components/projects/NewProjectDialog.tsx
- [X] T045 [P] Create DeleteProjectDialog component in frontend/src/components/projects/DeleteProjectDialog.tsx
- [X] T046 Create project API client in frontend/src/lib/api/projects.ts (TanStack Query hooks)
- [X] T047 Create empty state component in frontend/src/components/projects/EmptyState.tsx

**Checkpoint**: Dashboard functional - users can manage projects

---

## Phase 6: Document Upload & Management

**Purpose**: Upload and manage documents for a project

**Goal**: User can upload documents (PDF, DOCX, TXT), view document list, preview documents, delete documents

**Independent Test**: Navigate to documents page → upload files → view list → delete files

- [X] T048 Create project detail layout in frontend/src/app/(dashboard)/projects/[id]/layout.tsx
- [X] T049 Create documents page in frontend/src/app/(dashboard)/projects/[id]/documents/page.tsx
- [X] T050 Create DocumentUploader component in frontend/src/components/documents/DocumentUploader.tsx (drag & drop)
- [X] T051 Create DocumentList component in frontend/src/components/documents/DocumentList.tsx
- [X] T052 [P] Create DocumentCard component in frontend/src/components/documents/DocumentCard.tsx
- [X] T053 [P] Create DocumentPreview component in frontend/src/components/documents/DocumentPreview.tsx
- [X] T054 Create documents API client in frontend/src/lib/api/documents.ts (TanStack Query hooks)
- [X] T055 Create useDocuments hook in frontend/src/lib/hooks/useDocuments.ts
- [X] T056 Add file validation logic in frontend/src/lib/utils/validation.ts (file type, size checks)
- [X] T057 Create upload progress indicator component in frontend/src/components/documents/UploadProgress.tsx

**Checkpoint**: ✅ COMPLETE - Document management complete - users can upload and manage documents

---

## Phase 7: Conversational Schema Builder (Chat Interface)

**Purpose**: Define extraction schema through conversational AI interface

**Goal**: User has natural conversation with AI to define what data to extract, sees schema preview update in real-time

**Independent Test**: Navigate to schema page → answer AI questions → see schema build → approve schema

- [X] T058 Create schema page in frontend/src/app/(dashboard)/projects/[id]/schema/page.tsx
- [X] T059 Create chat store with Zustand in frontend/src/lib/store/chatStore.ts
- [X] T060 Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx
- [X] T061 Create MessageBubble component in frontend/src/components/chat/MessageBubble.tsx
- [X] T062 [P] Create ChatInput component in frontend/src/components/chat/ChatInput.tsx
- [X] T063 [P] Create TypingIndicator component in frontend/src/components/chat/TypingIndicator.tsx
- [X] T064 Create SchemaPreview component in frontend/src/components/chat/SchemaPreview.tsx (sidebar)
- [X] T065 Create VariableCard component in frontend/src/components/chat/VariableCard.tsx (displays extracted variables)
- [X] T066 Create schema API client in frontend/src/lib/api/schema.ts (TanStack Query hooks)
- [X] T067 Create useChat hook in frontend/src/lib/hooks/useChat.ts
- [X] T068 Implement markdown rendering for AI messages in MessageBubble component
- [X] T069 Add suggestion buttons component in frontend/src/components/chat/SuggestionButtons.tsx
- [X] T070 Create ApproveSchemaButton component in frontend/src/components/chat/ApproveSchemaButton.tsx

**Checkpoint**: ✅ COMPLETE - Schema builder complete - users can define extraction schema through conversation

---

## Phase 8: Results Viewer & Data Table

**Purpose**: View extracted data with confidence scores, filter/sort, flag errors

**Goal**: User can view extraction results in table format, sort/filter by confidence, flag items for review, view source text

**Independent Test**: Navigate to results page → view data table → sort by confidence → click row to see details → flag item

- [X] T071 Create results page in frontend/src/app/(dashboard)/projects/[id]/results/page.tsx
- [X] T072 Create ExtractionPreview component in frontend/src/components/results/ExtractionPreview.tsx (main table)
- [X] T073 Create DataTable component using TanStack Table in frontend/src/components/results/DataTable.tsx
- [X] T074 Create ConfidenceIndicator component in frontend/src/components/results/ConfidenceIndicator.tsx (colored dots)
- [X] T075 [P] Create ConfidenceBadge component in frontend/src/components/results/ConfidenceBadge.tsx
- [X] T076 [P] Create FilterControls component in frontend/src/components/results/FilterControls.tsx
- [X] T077 Create ResultDetailModal component in frontend/src/components/results/ResultDetailModal.tsx (row details)
- [X] T078 Create SourceTextView component in frontend/src/components/results/SourceTextView.tsx (shows source quote)
- [X] T079 Create extraction API client in frontend/src/lib/api/extraction.ts (TanStack Query hooks)
- [X] T080 Create useExtractions hook (integrated in extraction.ts)
- [X] T081 Add table sorting logic in DataTable component
- [X] T082 Add table filtering logic in DataTable component
- [X] T083 Add row selection logic for bulk operations in DataTable component
- [X] T084 Create FlagButton component in frontend/src/components/results/FlagButton.tsx

**Checkpoint**: ✅ COMPLETE - Results viewer complete - users can review extracted data

---

## Phase 9: Export Configuration & Download

**Purpose**: Configure export options and download CSV

**Goal**: User can configure CSV export (wide/long format, include confidence scores, filter by confidence), preview export, download CSV

**Independent Test**: Navigate to export page → configure options → see preview update → download CSV

- [ ] T085 Create export page in frontend/src/app/(dashboard)/projects/[id]/export/page.tsx
- [ ] T086 Create ExportConfig component in frontend/src/components/export/ExportConfig.tsx (options panel)
- [ ] T087 Create ExportPreview component in frontend/src/components/export/ExportPreview.tsx (preview table)
- [ ] T088 Create FormatSelector component in frontend/src/components/export/FormatSelector.tsx (wide vs long)
- [ ] T089 [P] Create ExportOptions component in frontend/src/components/export/ExportOptions.tsx (checkboxes)
- [ ] T090 [P] Create DownloadButton component in frontend/src/components/export/DownloadButton.tsx
- [ ] T091 Create export API client in frontend/src/lib/api/export.ts (TanStack Query hooks)
- [ ] T092 Implement CSV generation logic in frontend/src/lib/utils/export.ts
- [ ] T093 Add browser download trigger in DownloadButton component
- [ ] T094 Create export success toast notification

**Checkpoint**: Export flow complete - users can download CSV exports

---

## Phase 10: Processing Progress & Real-time Updates (Mock)

**Purpose**: Show processing progress for sample testing and full extraction

**Goal**: User sees real-time progress updates (mocked in Phase 1), estimated completion time, current document

**Independent Test**: Start sample/full extraction → see progress bar update → see completion notification

- [ ] T095 Create processing page in frontend/src/app/(dashboard)/projects/[id]/process/page.tsx
- [ ] T096 Create ProcessingProgress component in frontend/src/components/processing/ProcessingProgress.tsx
- [ ] T097 Create ProgressBar component in frontend/src/components/processing/ProgressBar.tsx
- [ ] T098 [P] Create ProcessingStats component in frontend/src/components/processing/ProcessingStats.tsx
- [ ] T099 [P] Create CurrentDocumentIndicator component in frontend/src/components/processing/CurrentDocumentIndicator.tsx
- [ ] T100 Create mock WebSocket simulation in frontend/src/lib/hooks/useWebSocket.ts (simulates updates)
- [ ] T101 Add start/pause/cancel controls in ProcessingProgress component
- [ ] T102 Create completion notification with redirect to results

**Checkpoint**: Processing UI complete - users can monitor extraction progress

---

## Phase 11: Navigation & User Flow Integration

**Purpose**: Connect all pages with navigation, ensure smooth user flow

**Goal**: User can navigate through entire workflow: create project → upload docs → define schema → view results → export

**Independent Test**: Complete full user journey from project creation to CSV download

- [ ] T103 Update Sidebar component with project navigation links (Documents, Schema, Results, Export)
- [ ] T104 Add breadcrumb navigation in frontend/src/components/layout/Breadcrumbs.tsx
- [ ] T105 Create project status indicator in frontend/src/components/projects/ProjectStatus.tsx
- [ ] T106 Add "Next Step" CTAs on each page (Documents → Schema → Test → Process → Results → Export)
- [ ] T107 Create workflow stepper component in frontend/src/components/layout/WorkflowStepper.tsx
- [ ] T108 Add route transitions and loading states
- [ ] T109 Create 404 Not Found page in frontend/src/app/not-found.tsx
- [ ] T110 [P] Create error boundary in frontend/src/app/error.tsx

**Checkpoint**: Full user flow functional - complete end-to-end journey possible

---

## Phase 12: Responsive Design & Accessibility

**Purpose**: Ensure UI works on all screen sizes and meets accessibility standards

**Goal**: Site is responsive (desktop, tablet, mobile) and WCAG 2.1 AA compliant

**Independent Test**: Test on different screen sizes, keyboard navigation, screen reader

- [ ] T111 [P] Make landing page responsive (mobile, tablet, desktop)
- [ ] T112 [P] Make dashboard responsive with mobile-friendly project cards
- [ ] T113 [P] Make document uploader responsive with touch-friendly drag & drop
- [ ] T114 [P] Make chat interface responsive with full-width on mobile
- [ ] T115 [P] Make data table responsive with horizontal scroll on mobile
- [ ] T116 [P] Make export page responsive with stacked layout on mobile
- [ ] T117 Add keyboard navigation support (Tab, Shift+Tab, Enter, Escape)
- [ ] T118 Add ARIA labels to all interactive elements
- [ ] T119 Add focus indicators to all focusable elements
- [ ] T120 Ensure color contrast meets WCAG AA standards (4.5:1 for text)
- [ ] T121 Add skip-to-content link for screen readers
- [ ] T122 Test with screen reader (NVDA/JAWS)

**Checkpoint**: Responsive and accessible - works on all devices and for all users

---

## Phase 13: Performance Optimization

**Purpose**: Optimize bundle size, loading speed, and runtime performance

**Goal**: Lighthouse score > 90, initial load < 2 seconds

**Independent Test**: Run Lighthouse audit, check bundle size, test loading speed

- [ ] T123 [P] Implement code splitting for heavy components (DataTable, ChatInterface)
- [ ] T124 [P] Add lazy loading for modal dialogs
- [ ] T125 [P] Optimize images with Next.js Image component
- [ ] T126 [P] Add loading skeletons for all data-fetching components
- [ ] T127 Implement prefetching for navigation links
- [ ] T128 Add React.memo to prevent unnecessary re-renders in list components
- [ ] T129 Optimize TanStack Query cache settings
- [ ] T130 Add compression for CSV exports
- [ ] T131 Run Lighthouse audit and fix issues
- [ ] T132 Verify bundle size < 500KB (gzipped)

**Checkpoint**: Performance optimized - fast load times and smooth interactions

---

## Phase 14: Polish & Documentation

**Purpose**: Final UI polish, error handling, and documentation

**Goal**: Production-ready frontend with complete documentation

**Independent Test**: Complete user testing session, verify all features work smoothly

- [ ] T133 [P] Add error handling for all API calls
- [ ] T134 [P] Add loading states for all async operations
- [ ] T135 [P] Add success/error toast notifications throughout app
- [ ] T136 [P] Polish UI with consistent spacing and typography
- [ ] T137 Add helpful tooltips for complex features
- [ ] T138 Create README.md with setup instructions in frontend/README.md
- [ ] T139 Document mock data structure in frontend/src/mocks/README.md
- [ ] T140 Create Phase 2 integration guide (how to swap mock API for real API)
- [ ] T141 List all TODO(Phase 2) items in PHASE2-NOTES.md
- [ ] T142 Add inline code comments for complex logic
- [ ] T143 Manual testing of full user flow (end-to-end)
- [ ] T144 Fix any bugs discovered during testing

**Checkpoint**: Frontend MVP complete and production-ready

---

## Phase 15: Deployment

**Purpose**: Deploy frontend to Vercel

**Goal**: Live, publicly accessible frontend application

**Independent Test**: Access deployed URL, verify all features work in production

- [ ] T145 Create Vercel account and connect GitHub repository
- [ ] T146 Configure build settings in vercel.json
- [ ] T147 Set environment variables in Vercel dashboard
- [ ] T148 Deploy to production
- [ ] T149 Test deployed site (all features)
- [ ] T150 [P] Setup custom domain (optional)
- [ ] T151 Configure automatic deployments from main branch
- [ ] T152 Add deployment status badge to README

**Checkpoint**: Frontend deployed and accessible at public URL

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)**: No dependencies - start immediately
2. **Foundational (Phase 2)**: Depends on Setup - BLOCKS all feature development
3. **Mock Data (Phase 3)**: Depends on Foundational types
4. **All Feature Phases (4-10)**: Depend on Foundational + Mock Data
   - Can proceed in parallel or sequentially in order
5. **Navigation (Phase 11)**: Depends on all feature pages being complete
6. **Responsive/A11y (Phase 12)**: Depends on all UI components being built
7. **Performance (Phase 13)**: Depends on all features being implemented
8. **Polish (Phase 14)**: Depends on all features being complete
9. **Deployment (Phase 15)**: Final phase

### Feature Page Dependencies

- **Auth (Phase 4)**: Depends on Foundational, Mock Data
- **Dashboard (Phase 5)**: Depends on Foundational, Mock Data, Auth
- **Documents (Phase 6)**: Depends on Foundational, Mock Data, Dashboard
- **Schema (Phase 7)**: Depends on Foundational, Mock Data, Dashboard (independent of Documents)
- **Results (Phase 8)**: Depends on Foundational, Mock Data, Dashboard
- **Export (Phase 9)**: Depends on Foundational, Mock Data, Results
- **Processing (Phase 10)**: Depends on Foundational, Mock Data

### Within Each Phase

- Tasks marked [P] can run in parallel
- Tasks without [P] have sequential dependencies within their feature
- Complete all tasks in a phase before moving to next phase for clean checkpoints

### Parallel Opportunities

**Setup Phase:**
```bash
# Can run in parallel:
T002 + T003 + T004 + T005 + T006 + T007 + T008
```

**Foundational Phase:**
```bash
# Type definitions in parallel:
T010 + T011 + T012

# Utilities in parallel:
T014 + T015

# shadcn/ui installs in parallel:
T017 + T018 + T019

# Layout components in parallel:
T022 + T023
```

**Mock Data Phase:**
```bash
# All mock files in parallel:
T025 + T026 + T027 + T028
```

**Feature Development:**
- Different developers can work on different feature phases (4-10) in parallel
- Within each feature, components marked [P] can be built in parallel

---

## Implementation Strategy

### MVP First Approach (Recommended)

**Week 1-2: Foundation**
1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: Mock Data
→ Checkpoint: Can start building features

**Week 3-4: Core Features**
4. Complete Phase 4: Auth
5. Complete Phase 5: Dashboard
6. Complete Phase 6: Documents
→ Checkpoint: Users can create projects and upload documents

**Week 5-6: AI Features**
7. Complete Phase 7: Schema Builder (chat)
8. Complete Phase 8: Results Viewer
→ Checkpoint: Core extraction workflow UI complete

**Week 7-8: Export & Integration**
9. Complete Phase 9: Export
10. Complete Phase 10: Processing
11. Complete Phase 11: Navigation
→ Checkpoint: Full user flow functional

**Week 9: Polish & Deploy**
12. Complete Phase 12: Responsive/A11y
13. Complete Phase 13: Performance
14. Complete Phase 14: Polish
15. Complete Phase 15: Deployment
→ Checkpoint: Production deployment complete

### Parallel Team Strategy

With 3 developers:
1. All: Complete Setup + Foundational + Mock Data together (Week 1-2)
2. Split after Foundational:
   - Dev A: Auth + Dashboard (Phase 4-5)
   - Dev B: Documents + Schema (Phase 6-7)
   - Dev C: Results + Export (Phase 8-9)
3. Integrate: Navigation + Polish together (Week 8-9)

---

## Parallel Execution Examples

### Example 1: Foundational Phase Components
```bash
# Launch all layout components together:
Task: "Create shared Header component in frontend/src/components/layout/Header.tsx"
Task: "Create shared Footer component in frontend/src/components/layout/Footer.tsx"
Task: "Create shared Sidebar component in frontend/src/components/layout/Sidebar.tsx"
```

### Example 2: Results Page Components
```bash
# Launch all result components together:
Task: "Create ConfidenceBadge component in frontend/src/components/results/ConfidenceBadge.tsx"
Task: "Create FilterControls component in frontend/src/components/results/FilterControls.tsx"
```

### Example 3: Responsive Design
```bash
# Launch all responsive tasks together:
Task: "Make landing page responsive (mobile, tablet, desktop)"
Task: "Make dashboard responsive with mobile-friendly project cards"
Task: "Make document uploader responsive with touch-friendly drag & drop"
Task: "Make chat interface responsive with full-width on mobile"
Task: "Make data table responsive with horizontal scroll on mobile"
Task: "Make export page responsive with stacked layout on mobile"
```

---

## Notes

- **Mock Data**: All features use mock data in Phase 1. Backend integration is Phase 2.
- **Tests**: Not included in MVP - manual testing only
- **[P] marker**: Tasks can run in parallel (different files, no blocking dependencies)
- **Checkpoints**: Validate at each checkpoint before proceeding
- **Commits**: Commit after each completed task or logical group
- **TypeScript**: Strict mode enabled - fix all type errors before proceeding
- **Phase 2 Prep**: Document all areas that need backend integration with TODO(Phase 2) comments

---

## Success Metrics

**Definition of Done (Phase 1):**
- ✅ All 152 tasks complete
- ✅ User can complete full workflow with mock data
- ✅ Site loads in < 2 seconds (Lighthouse > 90)
- ✅ Responsive on desktop, tablet, mobile
- ✅ TypeScript compiles with 0 errors
- ✅ Keyboard accessible
- ✅ Deployed to Vercel with public URL

**Ready for Phase 2:**
- ✅ All Phase 1 tasks complete
- ✅ TypeScript interfaces documented
- ✅ Mock API service layer clearly abstracted
- ✅ All TODO(Phase 2) items cataloged
- ✅ Integration guide written
- ✅ Live demo available for user feedback

---

**Task List Status:** READY FOR EXECUTION
**Last Updated:** January 19, 2025
**Total Tasks:** 152 tasks across 15 phases
**Estimated Effort:** 2-3 weeks (1 developer, full-time) or 3-4 weeks with polish
