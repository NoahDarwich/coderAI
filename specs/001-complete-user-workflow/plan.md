# Implementation Plan: Complete User Workflow (5 Steps)

**Branch**: `001-complete-user-workflow` | **Date**: 2025-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-complete-user-workflow/spec.md`

**Note**: This plan implements the complete 5-step user workflow defined in USER_WORKFLOW.md as the Phase 1 MVP (Frontend + Mock Data).

## Summary

Implement the complete end-to-end user workflow for the Research Automation Tool, covering all 5 steps from project creation through data export. This is a frontend-only implementation (Phase 1) using Next.js 15, React 19, TypeScript, and mock data. The workflow enables researchers to extract structured data from documents through an intuitive, step-by-step interface without requiring technical expertise.

**Technical Approach**: Build complete UI pages for each workflow step using shadcn/ui components, Tailwind CSS styling, and a mock data service layer that simulates backend responses. All user interactions will work with realistic mock data, validating the UX before Phase 2 backend integration.

## Technical Context

**Language/Version**: TypeScript 5.6+ with Next.js 15 (App Router), React 19
**Primary Dependencies**: Next.js 15, React 19, TypeScript 5.6, Tailwind CSS 4.0, shadcn/ui, Zustand (state management), TanStack Query (data fetching), TanStack Table (data grids)
**Storage**: Mock data in TypeScript files (`src/mocks/`), browser localStorage for persistence across sessions (Phase 1 only)
**Testing**: Vitest for component tests, manual testing for workflow validation, NO E2E tests (Phase 1)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge), desktop-first responsive design (768px+ for full features)
**Project Type**: Web application (frontend only for Phase 1)
**Performance Goals**: < 2 seconds initial page load, < 100ms UI interaction feedback, < 3 seconds time-to-interactive
**Constraints**: Frontend-only (no real backend), mock data must be realistic and cover edge cases, WCAG 2.1 AA accessibility compliance
**Scale/Scope**: 5 major workflow pages, 20-30 React components, ~5000 lines of TypeScript code, deployment to Vercel

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

**I. UI-First Design:**
- [x] All features align with Phase 1 scope (Frontend + Mock Data) - Complete frontend implementation with no backend dependencies
- [x] Mock data strategy defined for this feature - Mock API service layer in `src/services/mockApi.ts` with typed responses
- [x] Service layer abstraction identified - All components use `src/services/api.ts` interface, easy swap to real API in Phase 2

**II. User Experience Excellence:**
- [x] Accessibility requirements identified (WCAG 2.1 AA) - Keyboard navigation, screen reader support, ARIA labels, color contrast
- [x] Error states and loading states planned - Every async operation has loading spinner, error boundaries for each page
- [x] Mobile responsiveness considerations documented - Responsive layouts for 768px+, mobile-friendly interactions

**III. Rapid Iteration:**
- [x] shadcn/ui components identified for use - Button, Card, Dialog, Form, Input, Select, Table, Tabs, Toast, Progress, Badge
- [x] Technical debt acceptable for Phase 1 documented - Hardcoded mock data OK, simplified state (no complex global state), no optimization
- [x] Phase 2 integration points noted - All API calls marked with `// TODO(Phase 2): Replace with real API`, typed interfaces ready

**IV. User Workflow Fidelity:**
- [x] Feature maps to specific USER_WORKFLOW.md steps (1-5) - Implements ALL 5 steps exactly as specified
- [x] Does NOT introduce features outside the 5-step workflow - No extra features, strict adherence to USER_WORKFLOW.md
- [x] Navigation flow aligns with workflow progression - Linear progression through steps 1→2→3→4→5, back navigation allowed
- [x] Workflow design principles applied:
  - Clarity over cleverness - Simple labels, tooltips, inline help
  - Progress visibility - Progress indicator showing current step (1 of 5)
  - Reversibility - Back buttons, edit capabilities at review stage
  - Asynchronous awareness - Background processing with status updates
  - Data transparency - Show document counts, processing progress, confidence scores

### User Workflow Mapping

**Primary Workflow Step(s):** All steps 1-5 (complete implementation)

**Workflow Compliance:**
- **Step 1 (Project Setup & Document Input)**: `/projects/new` page with project form, scale selector, document uploader (drag-and-drop), document list view
- **Step 2 (Schema Definition Wizard)**: `/projects/[id]/schema` page with multi-step wizard form for variable definition (NOT chat interface)
- **Step 3 (Schema Review & Confirmation)**: `/projects/[id]/schema/review` page with table preview, edit/delete/reorder actions, confirmation button
- **Step 4 (Processing - Sample & Full)**: `/projects/[id]/process` page with sample testing section (Phase A) and full processing section (Phase B) with real-time progress
- **Step 5 (Results & Export)**: `/projects/[id]/results` page with sortable/filterable data table, export configuration modal

**Rationale:** This implementation delivers the complete core value proposition: enabling researchers to extract structured data through an intuitive workflow. By implementing all 5 steps, users can experience the full journey and provide feedback on the complete UX before backend development begins.

## Project Structure

### Documentation (this feature)

```text
specs/001-complete-user-workflow/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (created)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
└── contracts/           # Phase 1 output (to be generated)
    └── mock-api.yaml    # Mock API contract matching future real API
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/                           # Next.js 15 App Router
│   │   ├── (auth)/                    # Auth routes (Phase 2)
│   │   ├── (dashboard)/
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx           # Projects list (dashboard)
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx       # Project overview
│   │   │   │       ├── documents/
│   │   │   │       │   └── page.tsx   # Step 1: Document upload
│   │   │   │       ├── schema/
│   │   │   │       │   ├── page.tsx   # Step 2: Schema wizard
│   │   │   │       │   └── review/
│   │   │   │       │       └── page.tsx # Step 3: Schema review
│   │   │   │       ├── process/
│   │   │   │       │   └── page.tsx   # Step 4: Sample & full processing
│   │   │   │       └── results/
│   │   │   │           └── page.tsx   # Step 5: Results & export
│   │   │   └── layout.tsx             # Dashboard layout with nav
│   │   ├── layout.tsx                 # Root layout
│   │   └── page.tsx                   # Landing page
│   ├── components/
│   │   ├── ui/                        # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── progress.tsx
│   │   │   └── badge.tsx
│   │   ├── workflow/                  # Workflow-specific components
│   │   │   ├── step1/
│   │   │   │   ├── ProjectSetupForm.tsx
│   │   │   │   ├── DocumentUploader.tsx
│   │   │   │   └── DocumentList.tsx
│   │   │   ├── step2/
│   │   │   │   ├── SchemaWizard.tsx
│   │   │   │   ├── VariableForm.tsx
│   │   │   │   └── WizardNavigation.tsx
│   │   │   ├── step3/
│   │   │   │   ├── SchemaReview.tsx
│   │   │   │   ├── SchemaTable.tsx
│   │   │   │   └── VariableEditor.tsx
│   │   │   ├── step4/
│   │   │   │   ├── SampleTesting.tsx
│   │   │   │   ├── FullProcessing.tsx
│   │   │   │   └── ProcessingLog.tsx
│   │   │   └── step5/
│   │   │       ├── ResultsTable.tsx
│   │   │       ├── ExportModal.tsx
│   │   │       └── ConfidenceFilter.tsx
│   │   └── layout/
│   │       ├── DashboardNav.tsx
│   │       ├── WorkflowProgress.tsx  # Shows "Step 2 of 5"
│   │       └── ErrorBoundary.tsx
│   ├── lib/
│   │   ├── utils.ts                   # Utility functions
│   │   └── validations.ts             # Form validation schemas (Zod)
│   ├── services/
│   │   ├── api.ts                     # API interface (used by components)
│   │   └── mockApi.ts                 # Mock implementation (Phase 1)
│   ├── types/
│   │   ├── api.ts                     # API response types
│   │   ├── project.ts                 # Project entity types
│   │   ├── document.ts                # Document entity types
│   │   ├── schema.ts                  # Schema & Variable types
│   │   ├── extraction.ts              # Extraction & Results types
│   │   └── export.ts                  # Export config types
│   ├── mocks/
│   │   ├── projects.ts                # Mock project data
│   │   ├── documents.ts               # Mock document data
│   │   ├── schemas.ts                 # Mock schema data
│   │   ├── extractions.ts             # Mock extraction results
│   │   └── README.md                  # Mock data documentation
│   └── store/                         # Zustand stores
│       ├── projectStore.ts            # Project state
│       └── workflowStore.ts           # Workflow progress state
├── public/
│   └── sample-documents/              # Sample PDFs for demo
├── tests/
│   └── components/                    # Component tests (Vitest)
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

**Structure Decision**: Frontend-only web application structure. Using Next.js 15 App Router with organized component structure grouped by workflow step. Mock data service layer (`mockApi.ts`) will be swapped for real API service (`realApi.ts`) in Phase 2 by changing a single import in `api.ts`.

## Complexity Tracking

> **No violations** - This implementation aligns completely with Phase 1 constitution principles:
> - Frontend-only with mock data ✓
> - No backend dependencies ✓
> - Uses approved tech stack (Next.js, React, shadcn/ui) ✓
> - Implements exact USER_WORKFLOW.md steps ✓
> - No features outside 5-step workflow ✓
