# Research: Complete User Workflow Implementation

**Feature**: 001-complete-user-workflow
**Date**: 2025-01-23
**Purpose**: Research best practices and patterns for implementing the 5-step user workflow in Next.js 15 with React 19

## Research Areas

### 1. Next.js 15 App Router Patterns for Multi-Step Workflows

**Decision**: Use nested route groups with parallel routes for workflow steps

**Rationale**:
- App Router's file-based routing naturally maps to workflow steps
- Nested routes `/projects/[id]/schema` → `/projects/[id]/schema/review` represent progression
- Route groups `(dashboard)` allow shared layouts without affecting URLs
- Parallel routes enable side-by-side views (e.g., document preview + schema form)

**Implementation Pattern**:
```
app/(dashboard)/projects/[id]/
├── page.tsx              # Project overview (hub)
├── documents/page.tsx    # Step 1
├── schema/
│   ├── page.tsx          # Step 2
│   └── review/page.tsx   # Step 3
├── process/page.tsx      # Step 4
└── results/page.tsx      # Step 5
```

**Alternatives Considered**:
- Single-page app with client-side routing → Rejected: Loses URL-based navigation, harder to bookmark steps
- Query parameters for steps (`?step=2`) → Rejected: Less semantic, harder to share specific steps

**Best Practices**:
- Use `useParams()` to access `[id]` in all workflow pages
- Implement `layout.tsx` at project level to show workflow progress indicator
- Use `loading.tsx` for automatic loading states during navigation
- Implement `error.tsx` for error boundaries at each step

### 2. Form State Management for Multi-Step Wizard (Step 2)

**Decision**: Use React Hook Form + Zustand for wizard state persistence

**Rationale**:
- React Hook Form: Best-in-class form validation, TypeScript support, performance
- Zustand: Lightweight global state (easier than Context API for wizard state)
- Persist wizard progress in Zustand store across page navigations
- Zod integration for schema validation

**Implementation Pattern**:
```typescript
// store/schemaWizardStore.ts
interface SchemaWizardState {
  variables: Variable[];
  currentStep: number;
  addVariable: (variable: Variable) => void;
  updateVariable: (index: number, variable: Variable) => void;
  deleteVariable: (index: number) => void;
  reorderVariables: (startIndex: number, endIndex: number) => void;
}

// components/workflow/step2/VariableForm.tsx
const { register, handleSubmit, formState: { errors } } = useForm<VariableFormData>({
  resolver: zodResolver(variableSchema),
});
```

**Alternatives Considered**:
- React Context API → Rejected: Boilerplate-heavy, re-render issues
- Redux → Rejected: Overkill for Phase 1 scope
- URL state (query params) → Rejected: Too much state to serialize, URL pollution

**Best Practices**:
- Validate each variable before allowing "Next" in wizard
- Auto-save wizard state to Zustand on every field change
- Provide "Save Draft" functionality (persist to localStorage)
- Clear wizard state only after schema confirmation (Step 3)

### 3. Mock Data Service Layer Architecture

**Decision**: Abstract API layer with interface-based design for easy Phase 2 swap

**Rationale**:
- Components call `api.ts` (interface), which delegates to `mockApi.ts` (Phase 1) or `realApi.ts` (Phase 2)
- Single import change switches entire app from mock → real
- TypeScript interfaces enforce contract consistency
- Mock data includes realistic latency simulation for better UX testing

**Implementation Pattern**:
```typescript
// services/api.ts (interface used by components)
export const api = {
  projects: projectsApi,
  documents: documentsApi,
  schema: schemaApi,
  processing: processingApi,
  results: resultsApi,
};

// Phase 1: Import mock
import { projectsApi } from './mockApi';

// Phase 2: Import real (ONLY change this line)
// import { projectsApi } from './realApi';

// mockApi.ts implementation
export const projectsApi = {
  list: async (): Promise<Project[]> => {
    await delay(500); // Simulate network latency
    return mockProjects;
  },
  // ... more methods
};
```

**Alternatives Considered**:
- MSW (Mock Service Worker) → Rejected: Overkill for Phase 1, adds complexity
- Inline mock data in components → Rejected: Violates service layer principle, hard to swap
- Feature flags → Rejected: Unnecessary complexity for Phase 1

**Best Practices**:
- Define all types in `types/` directory first
- Mock data must match real API response structure exactly
- Include error scenarios in mock data (network failures, validation errors)
- Document mock data assumptions in `mocks/README.md`

### 4. Accessibility Patterns for Complex Workflows

**Decision**: Use shadcn/ui components (built on Radix UI) + custom ARIA labels

**Rationale**:
- shadcn/ui components are accessible by default (Radix UI primitives)
- Radix UI handles focus management, keyboard navigation, ARIA attributes
- Custom components need explicit ARIA labels for workflow-specific semantics
- Focus trapping in modals/dialogs prevents keyboard escape

**Implementation Checklist**:
- [ ] All interactive elements are keyboard accessible (Tab, Enter, Space)
- [ ] Workflow progress indicator has `role="progressbar"` and `aria-valuenow`
- [ ] Form fields have associated `<label>` or `aria-label`
- [ ] Error messages announced via `aria-live="polite"`
- [ ] Modal dialogs trap focus and restore on close
- [ ] Skip links for keyboard users ("Skip to main content")
- [ ] Color contrast ratio ≥ 4.5:1 for all text

**shadcn/ui Components Used**:
- `Button`: Accessible buttons with variants
- `Form`: Form wrapper with error handling
- `Input`: Text inputs with label association
- `Select`: Accessible dropdown (Radix `Select`)
- `Dialog`: Modal with focus trap (Radix `Dialog`)
- `Table`: Data table with sortable headers
- `Toast`: Notifications with `aria-live`

**Best Practices**:
- Test with keyboard only (no mouse)
- Test with screen reader (VoiceOver on Mac, NVDA on Windows)
- Use semantic HTML (`<button>` not `<div onClick>`)
- Provide alt text for all icons (or `aria-hidden` if decorative)

### 5. Real-Time Progress Updates for Processing (Step 4)

**Decision**: Use React state + setTimeout for mock progress simulation (Phase 1)

**Rationale**:
- Phase 1 has no backend, so WebSocket/Server-Sent Events not needed
- Simulate progress with `setInterval` updating percentage
- Phase 2 will replace with real WebSocket connection (same UI)
- Progress bar component is backend-agnostic (just receives `percentage` prop)

**Implementation Pattern (Phase 1 Mock)**:
```typescript
// Step 4: Processing page
const [progress, setProgress] = useState(0);
const [status, setStatus] = useState<'idle' | 'processing' | 'complete'>('idle');

const startMockProcessing = async () => {
  setStatus('processing');

  // Simulate processing with mock delay
  for (let i = 0; i <= 100; i += 10) {
    await delay(500);
    setProgress(i);
    // Add mock log entries
  }

  setStatus('complete');
};

// Phase 2 will replace with:
// const socket = io(BACKEND_URL);
// socket.on('job:progress', ({ percentage }) => setProgress(percentage));
```

**Alternatives Considered**:
- WebSocket in Phase 1 with mock server → Rejected: Unnecessary complexity
- Polling API → Rejected: No backend to poll
- Instant mock completion → Rejected: Doesn't test loading UX

**Best Practices**:
- Show processing log with document names and timestamps
- Allow background processing (user can navigate away)
- Persist processing state in Zustand store
- Display toast notification on completion

### 6. Data Table Patterns for Large Result Sets (Step 5)

**Decision**: Use TanStack Table (React Table v8) with virtualization for large datasets

**Rationale**:
- TanStack Table: Best headless table library, full TypeScript support
- Headless design allows custom styling with Tailwind CSS
- Built-in sorting, filtering, pagination
- Virtual scrolling handles 1000+ rows without performance issues
- shadcn/ui provides table styling wrapper

**Implementation Pattern**:
```typescript
import { useReactTable, getCoreRowModel, getSortedRowModel, getFilteredRowModel } from '@tanstack/react-table';

const table = useReactTable({
  data: extractionResults,
  columns: schemaColumns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
});
```

**Features Needed**:
- Column sorting (click header to sort)
- Global search/filter
- Confidence threshold filter (custom filter function)
- Row selection for bulk actions
- Export visible rows to CSV

**Alternatives Considered**:
- Plain HTML table → Rejected: No sorting/filtering, performance issues
- AG Grid → Rejected: Commercial license required for some features
- Material-UI DataGrid → Rejected: Conflicts with shadcn/ui styling

**Best Practices**:
- Memoize table data and columns with `useMemo`
- Implement column resizing for better UX
- Add loading skeleton while fetching data
- Export respects current filters/sorting

### 7. File Upload Patterns (Step 1)

**Decision**: Use react-dropzone + HTML5 File API for drag-and-drop upload

**Rationale**:
- react-dropzone: Most popular drag-and-drop library, accessible
- HTML5 File API for reading file contents (mock processing)
- Supports multiple files, file type validation, size limits
- Preview documents in list after upload

**Implementation Pattern**:
```typescript
import { useDropzone } from 'react-dropzone';

const { getRootProps, getInputProps, isDragActive } = useDropzone({
  accept: {
    'application/pdf': ['.pdf'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'text/plain': ['.txt'],
  },
  maxSize: 10 * 1024 * 1024, // 10MB
  onDrop: (acceptedFiles) => {
    // Process files
  },
});
```

**Alternatives Considered**:
- Native `<input type="file">` → Rejected: Less UX polish, no drag-and-drop
- Uppy → Rejected: Overkill for simple upload

**Best Practices**:
- Show upload progress for each file (mock in Phase 1)
- Display file previews (name, size, type)
- Allow removing files before proceeding
- Validate file types and sizes client-side

### 8. State Persistence Across Sessions

**Decision**: Use localStorage for Phase 1 session persistence

**Rationale**:
- No database in Phase 1, need to preserve user work
- localStorage stores project data, wizard state, documents
- Automatically restore state on page refresh
- Clear strategy: Manual "Delete Project" or 7-day expiration

**Implementation Pattern**:
```typescript
// Zustand persist middleware
import { persist } from 'zustand/middleware';

const useProjectStore = create(
  persist(
    (set) => ({
      projects: [],
      currentProject: null,
      // ... store logic
    }),
    {
      name: 'research-tool-storage',
      version: 1,
    }
  )
);
```

**Alternatives Considered**:
- SessionStorage → Rejected: Lost on tab close
- IndexedDB → Rejected: Overkill for simple key-value storage
- No persistence → Rejected: Poor UX (lose work on refresh)

**Best Practices**:
- Namespace localStorage keys (`research-tool-*`)
- Handle localStorage quota errors gracefully
- Provide "Clear All Data" button in settings
- Migrate localStorage schema if structure changes

## Summary of Technology Decisions

| Concern | Decision | Rationale |
|---------|----------|-----------|
| Routing | Next.js App Router nested routes | Natural workflow step mapping |
| Form Management | React Hook Form + Zod | Best-in-class validation |
| Global State | Zustand | Lightweight, less boilerplate than Redux |
| Mock API | Interface-based service layer | Easy swap to real API |
| Accessibility | shadcn/ui (Radix) + ARIA | Accessible by default |
| Progress Updates | Mock with setTimeout | Simulates real progress UX |
| Data Tables | TanStack Table | Best headless table library |
| File Upload | react-dropzone | Drag-and-drop UX |
| Persistence | localStorage + Zustand persist | Simple session persistence |

## Phase 2 Integration Points

1. **Authentication**: Add NextAuth.js, protect dashboard routes
2. **Real API**: Replace `mockApi.ts` with `realApi.ts` (FastAPI backend)
3. **WebSocket**: Add Socket.io for real-time progress updates
4. **Database**: Replace localStorage with PostgreSQL persistence
5. **File Storage**: Upload documents to S3/storage service
6. **LLM Processing**: Connect to LangGraph backend for real extraction

## Open Questions (Resolved)

All technical clarifications resolved. No blockers for implementation.
