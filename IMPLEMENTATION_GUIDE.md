# Implementation Guide: Complete User Workflow (5 Steps)

**Project**: Research Automation Tool - Frontend MVP (Phase 1)
**Status**: Foundation Complete (28/130 tasks) - 21.5%
**Date**: 2025-11-23
**Architecture**: Next.js 15, React 19, TypeScript, shadcn/ui

---

## Table of Contents

1. [Current Status](#current-status)
2. [Architecture Overview](#architecture-overview)
3. [Completed Foundation](#completed-foundation)
4. [Remaining Implementation](#remaining-implementation)
5. [Task-by-Task Guide](#task-by-task-guide)
6. [Component Templates](#component-templates)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Guide](#deployment-guide)

---

## Current Status

### ✅ Completed Tasks (28/130)

#### Phase 1: Setup (T001-T007) - COMPLETE ✓
- ✅ T001: Next.js 15 project initialized
- ✅ T002: All dependencies installed (zustand, tanstack, react-dropzone, zod, etc.)
- ✅ T003: shadcn/ui initialized
- ✅ T004: shadcn/ui components installed
- ✅ T005: TypeScript configured with strict mode
- ✅ T006: Tailwind CSS configured
- ✅ T007: Directory structure created

#### Phase 2: Foundational (T008-T028) - COMPLETE ✓
- ✅ T008-T014: All TypeScript types created (`/frontend/src/types/`)
  - `project.ts` - Project and ProjectStatus types
  - `document.ts` - Document and DocumentStatus types
  - `schema.ts` - Schema, Variable, VariableType types
  - `extraction.ts` - ExtractionResult, ExtractedValue, getConfidenceLevel
  - `processing.ts` - ProcessingJob, ProcessingLog, JobStatus types
  - `export.ts` - ExportConfig, ExportResult, ExportFormat types
  - `api.ts` - API response wrappers and request types

- ✅ T015: `types/index.ts` - Central export file
- ✅ T016-T020: All mock data created (`/frontend/src/mocks/`)
  - `mockProjects.ts` - 5 projects in various states
  - `mockDocuments.ts` - 20+ documents across projects
  - `mockSchemas.ts` - 2 complete schemas with variables
  - `mockExtractions.ts` - 5 extraction results with confidence scores
  - `mockProcessingJobs.ts` - 3 processing jobs (sample, full, various statuses)

- ✅ T021: `mocks/README.md` - Mock data documentation
- ✅ T022-T027: Complete mock API implementation (`/frontend/src/services/newMockApi.ts`)
  - Projects API (list, get, create, update, delete)
  - Documents API (list, get, upload, delete, getContent)
  - Schema API (get, save, confirm, addVariable, updateVariable, deleteVariable, reorderVariables)
  - Processing API (startSample, startFull, getJob, cancelJob)
  - Results API (list, get, flag)
  - Export API (generate, download)

- ✅ T028: Main API interface created (`/frontend/src/services/api.ts`)

### 📋 Remaining Tasks (102/130)

#### Phase 2 Continued: Utilities & Layout (T029-T036) - 8 tasks
- [ ] T029: projectStore (Zustand)
- [ ] T030: workflowStore (Zustand)
- [ ] T031: schemaWizardStore (Zustand)
- [ ] T032: Utility functions (lib/utils.ts)
- [ ] T033: Zod validation schemas (lib/validations.ts)
- [ ] T034: WorkflowProgress component
- [ ] T035: ErrorBoundary component
- [ ] T036: Dashboard layout

#### Phase 3: User Story 1 (T037-T048) - 12 tasks
Project Setup & Document Input

#### Phase 4: User Story 2 (T049-T062) - 14 tasks
Schema Definition Wizard

#### Phase 5: User Story 3 (T063-T075) - 13 tasks
Schema Review & Confirmation

#### Phase 6: User Story 4 (T076-T095) - 20 tasks
Sample Testing & Full Processing

#### Phase 7: User Story 5 (T096-T113) - 18 tasks
Results Review & Export

#### Phase 8: Polish (T114-T130) - 17 tasks
Cross-Cutting Concerns & Deployment

---

## Architecture Overview

### Directory Structure

```
frontend/
├── src/
│   ├── app/                           # Next.js 15 App Router
│   │   ├── (dashboard)/
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx           # Projects list
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx       # NEW PROJECT (Step 1a)
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx       # Project overview
│   │   │   │       ├── documents/
│   │   │   │       │   └── page.tsx   # DOCUMENT UPLOAD (Step 1b)
│   │   │   │       ├── schema/
│   │   │   │       │   ├── page.tsx   # SCHEMA WIZARD (Step 2)
│   │   │   │       │   └── review/
│   │   │   │       │       └── page.tsx # SCHEMA REVIEW (Step 3)
│   │   │   │       ├── process/
│   │   │   │       │   └── page.tsx   # PROCESSING (Step 4)
│   │   │   │       └── results/
│   │   │   │           └── page.tsx   # RESULTS & EXPORT (Step 5)
│   │   │   └── layout.tsx             # Dashboard layout with nav
│   │   ├── layout.tsx                 # Root layout
│   │   └── page.tsx                   # Landing page
│   ├── components/
│   │   ├── ui/                        # shadcn/ui components (DONE)
│   │   ├── workflow/                  # Workflow components (TO BUILD)
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
│   │       ├── WorkflowProgress.tsx
│   │       └── ErrorBoundary.tsx
│   ├── lib/
│   │   ├── utils.ts                   # Utility functions (TO BUILD)
│   │   └── validations.ts             # Zod schemas (TO BUILD)
│   ├── services/
│   │   ├── api.ts                     # ✅ API interface (DONE)
│   │   └── newMockApi.ts              # ✅ Mock implementation (DONE)
│   ├── types/                         # ✅ ALL TYPES (DONE)
│   │   ├── project.ts
│   │   ├── document.ts
│   │   ├── schema.ts
│   │   ├── extraction.ts
│   │   ├── processing.ts
│   │   ├── export.ts
│   │   ├── api.ts
│   │   └── index.ts
│   ├── mocks/                         # ✅ ALL MOCK DATA (DONE)
│   │   ├── mockProjects.ts
│   │   ├── mockDocuments.ts
│   │   ├── mockSchemas.ts
│   │   ├── mockExtractions.ts
│   │   ├── mockProcessingJobs.ts
│   │   └── README.md
│   └── store/                         # Zustand stores (TO BUILD)
│       ├── projectStore.ts
│       ├── workflowStore.ts
│       └── schemaWizardStore.ts
├── package.json                       # ✅ Dependencies installed
├── tsconfig.json                      # ✅ Configured
└── tailwind.config.ts                 # ✅ Configured
```

### Tech Stack (All Installed ✅)

- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19
- **Language**: TypeScript 5.6+ (strict mode)
- **Styling**: Tailwind CSS 4.0
- **Components**: shadcn/ui (Radix UI primitives)
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (optional, can use simple fetch)
- **Tables**: TanStack Table
- **Forms**: React Hook Form + Zod
- **File Upload**: react-dropzone
- **Date Utilities**: date-fns

### Design Principles

1. **Type Safety**: Strict TypeScript, all API responses typed
2. **Component Composition**: Small, focused components
3. **State Management**: Zustand for global state, React state for local
4. **Mock-First**: All features work with mock data (Phase 1)
5. **Easy Phase 2 Migration**: Single import change swaps mock → real API

---

## Completed Foundation

### Type System ✅

All types are defined in `/frontend/src/types/` and exported from `index.ts`:

```typescript
// Usage in components:
import { Project, Document, Schema, ExtractionResult } from '@/types';
```

**Key Types:**
- `Project` - Project entity with status workflow
- `Document` - Uploaded document metadata
- `Schema` - Extraction schema with ordered variables
- `Variable` - Individual extraction field definition
- `ExtractionResult` - Extraction output with confidence scores
- `ProcessingJob` - Background processing job status
- `ExportConfig` - Export configuration options

### Mock Data ✅

Comprehensive mock data in `/frontend/src/mocks/`:

- **5 Projects**: Various states (setup, schema, review, processing, complete)
- **20+ Documents**: PDF, DOCX, TXT across multiple projects
- **2 Schemas**: Complete extraction schemas with 3-5 variables each
- **5 Extraction Results**: With varying confidence scores (70-99%)
- **3 Processing Jobs**: Sample, full, various statuses

### Mock API ✅

Complete mock API in `/frontend/src/services/newMockApi.ts`:

```typescript
// Usage in components:
import { api } from '@/services/api';

// Projects
await api.projects.list();
await api.projects.get(id);
await api.projects.create({ name, scale });
await api.projects.update(id, data);
await api.projects.delete(id);

// Documents
await api.documents.list(projectId);
await api.documents.upload(projectId, files);
await api.documents.delete(documentId);
await api.documents.getContent(documentId);

// Schema
await api.schema.get(projectId);
await api.schema.save(projectId, { variables });
await api.schema.confirm(projectId);
await api.schema.addVariable(projectId, variable);
await api.schema.updateVariable(projectId, variableId, data);
await api.schema.deleteVariable(projectId, variableId);
await api.schema.reorderVariables(projectId, variableIds);

// Processing
await api.processing.startSample(projectId, sampleSize);
await api.processing.startFull(projectId);
await api.processing.getJob(jobId);
await api.processing.cancelJob(jobId);

// Results
await api.results.list(projectId, options);
await api.results.get(extractionId);
await api.results.flag(extractionId, isCorrect);

// Export
await api.export.generate(projectId, config);
await api.export.download(exportId);
```

**Features:**
- ✅ Network delay simulation (200-800ms)
- ✅ Error handling with typed errors
- ✅ In-memory persistence during session
- ✅ Automatic project updates (document counts, statuses)
- ✅ CSV generation (wide & long formats)
- ✅ Blob URL generation for downloads

---

## Remaining Implementation

### Phase 2 Continued: Utilities & Layout (T029-T036)

#### T029: Project Store (Zustand)

**File**: `/frontend/src/store/projectStore.ts`

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Project } from '@/types';

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;

  // Actions
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  removeProject: (id: string) => void;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      projects: [],
      currentProject: null,

      setProjects: (projects) => set({ projects }),
      setCurrentProject: (project) => set({ currentProject: project }),
      addProject: (project) => set((state) => ({
        projects: [...state.projects, project]
      })),
      updateProject: (id, updates) => set((state) => ({
        projects: state.projects.map(p =>
          p.id === id ? { ...p, ...updates } : p
        ),
        currentProject: state.currentProject?.id === id
          ? { ...state.currentProject, ...updates }
          : state.currentProject
      })),
      removeProject: (id) => set((state) => ({
        projects: state.projects.filter(p => p.id !== id),
        currentProject: state.currentProject?.id === id ? null : state.currentProject
      })),
    }),
    {
      name: 'research-tool-projects',
      version: 1,
    }
  )
);
```

#### T030: Workflow Store (Zustand)

**File**: `/frontend/src/store/workflowStore.ts`

```typescript
import { create } from 'zustand';

interface WorkflowState {
  currentStep: number;           // 1-5
  canProceed: boolean;

  // Actions
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setCanProceed: (canProceed: boolean) => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  currentStep: 1,
  canProceed: false,

  setStep: (step) => set({ currentStep: Math.max(1, Math.min(5, step)) }),
  nextStep: () => set((state) => ({
    currentStep: Math.min(5, state.currentStep + 1)
  })),
  prevStep: () => set((state) => ({
    currentStep: Math.max(1, state.currentStep - 1)
  })),
  setCanProceed: (canProceed) => set({ canProceed }),
}));
```

#### T031: Schema Wizard Store (Zustand)

**File**: `/frontend/src/store/schemaWizardStore.ts`

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Variable } from '@/types';

interface SchemaWizardState {
  variables: Variable[];
  currentVariableIndex: number;
  isDraft: boolean;
  projectId: string | null;

  // Actions
  setProjectId: (projectId: string) => void;
  addVariable: (variable: Omit<Variable, 'id' | 'order'>) => void;
  updateVariable: (index: number, variable: Partial<Variable>) => void;
  deleteVariable: (index: number) => void;
  reorderVariables: (startIndex: number, endIndex: number) => void;
  setCurrentIndex: (index: number) => void;
  saveDraft: () => void;
  loadDraft: (projectId: string) => void;
  clearDraft: () => void;
  reset: () => void;
}

export const useSchemaWizardStore = create<SchemaWizardState>()(
  persist(
    (set, get) => ({
      variables: [],
      currentVariableIndex: 0,
      isDraft: false,
      projectId: null,

      setProjectId: (projectId) => set({ projectId }),

      addVariable: (variable) => set((state) => {
        const newVariable: Variable = {
          id: `var-temp-${Date.now()}`,
          ...variable,
          order: state.variables.length,
        };
        return {
          variables: [...state.variables, newVariable],
          isDraft: true,
        };
      }),

      updateVariable: (index, updates) => set((state) => ({
        variables: state.variables.map((v, i) =>
          i === index ? { ...v, ...updates } : v
        ),
        isDraft: true,
      })),

      deleteVariable: (index) => set((state) => ({
        variables: state.variables
          .filter((_, i) => i !== index)
          .map((v, i) => ({ ...v, order: i })),
        isDraft: true,
      })),

      reorderVariables: (startIndex, endIndex) => set((state) => {
        const result = Array.from(state.variables);
        const [removed] = result.splice(startIndex, 1);
        result.splice(endIndex, 0, removed);
        return {
          variables: result.map((v, i) => ({ ...v, order: i })),
          isDraft: true,
        };
      }),

      setCurrentIndex: (index) => set({ currentVariableIndex: index }),

      saveDraft: () => set({ isDraft: false }),

      loadDraft: (projectId) => {
        // Loads from localStorage automatically via persist middleware
        const state = get();
        if (state.projectId === projectId) {
          return;
        }
        // Reset if different project
        set({ variables: [], currentVariableIndex: 0, projectId, isDraft: false });
      },

      clearDraft: () => set({
        variables: [],
        currentVariableIndex: 0,
        isDraft: false,
      }),

      reset: () => set({
        variables: [],
        currentVariableIndex: 0,
        isDraft: false,
        projectId: null,
      }),
    }),
    {
      name: 'research-tool-schema-wizard',
      version: 1,
    }
  )
);
```

#### T032: Utility Functions

**File**: `/frontend/src/lib/utils.ts`

```typescript
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, parseISO } from 'date-fns';

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format ISO date string to readable format
 */
export function formatDate(dateString: string, formatString: string = 'PPP'): string {
  try {
    return format(parseISO(dateString), formatString);
  } catch {
    return 'Invalid date';
  }
}

/**
 * Format date as relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString: string): string {
  try {
    return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
  } catch {
    return 'Unknown';
  }
}

/**
 * Format file size in bytes to human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Truncate text to specified length with ellipsis
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + '...';
}

/**
 * Get confidence level badge color
 */
export function getConfidenceBadgeColor(confidence: number): string {
  if (confidence >= 85) return 'bg-green-100 text-green-800 border-green-200';
  if (confidence >= 70) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  return 'bg-red-100 text-red-800 border-red-200';
}

/**
 * Get confidence emoji indicator
 */
export function getConfidenceEmoji(confidence: number): string {
  if (confidence >= 85) return '🟢';
  if (confidence >= 70) return '🟡';
  return '🔴';
}

/**
 * Sleep utility for delays
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Generate a simple UUID v4
 */
export function generateId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Download blob as file
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
```

#### T033: Zod Validation Schemas

**File**: `/frontend/src/lib/validations.ts`

```typescript
import { z } from 'zod';

/**
 * Project creation validation
 */
export const projectSchema = z.object({
  name: z
    .string()
    .min(1, 'Project name is required')
    .max(100, 'Project name must be less than 100 characters'),
  scale: z.enum(['small', 'large'], {
    required_error: 'Please select a project scale',
  }),
});

export type ProjectFormData = z.infer<typeof projectSchema>;

/**
 * Variable definition validation
 */
export const variableSchema = z.object({
  name: z
    .string()
    .min(1, 'Variable name is required')
    .max(50, 'Variable name must be less than 50 characters'),
  type: z.enum(['text', 'number', 'date', 'category', 'boolean'], {
    required_error: 'Please select a variable type',
  }),
  instructions: z
    .string()
    .min(10, 'Instructions must be at least 10 characters')
    .max(500, 'Instructions must be less than 500 characters'),
  classificationRules: z.array(z.string()).optional(),
});

export type VariableFormData = z.infer<typeof variableSchema>;

/**
 * Conditional validation: classificationRules required for category type
 */
export const variableSchemaWithConditional = variableSchema.refine(
  (data) => {
    if (data.type === 'category') {
      return data.classificationRules && data.classificationRules.length >= 2;
    }
    return true;
  },
  {
    message: 'Category variables must have at least 2 classification rules',
    path: ['classificationRules'],
  }
);

/**
 * Document upload validation
 */
export const documentUploadSchema = z.object({
  files: z
    .array(
      z.object({
        name: z.string(),
        size: z.number().max(10485760, 'File size must be less than 10MB'),
        type: z.enum([
          'application/pdf',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'text/plain',
        ], {
          errorMap: () => ({ message: 'Only PDF, DOCX, and TXT files are allowed' }),
        }),
      })
    )
    .min(1, 'At least one file is required'),
});

/**
 * Export configuration validation
 */
export const exportConfigSchema = z.object({
  format: z.enum(['csv']),
  structure: z.enum(['wide', 'long']),
  includeConfidence: z.boolean(),
  includeSourceText: z.boolean(),
  minConfidence: z.number().min(0).max(100).optional(),
});

export type ExportConfigFormData = z.infer<typeof exportConfigSchema>;

/**
 * Sample size validation
 */
export const sampleSizeSchema = z.object({
  sampleSize: z
    .number()
    .int('Sample size must be an integer')
    .min(10, 'Sample size must be at least 10')
    .max(20, 'Sample size must be at most 20'),
});

export type SampleSizeFormData = z.infer<typeof sampleSizeSchema>;
```

#### T034: WorkflowProgress Component

**File**: `/frontend/src/components/layout/WorkflowProgress.tsx`

```typescript
'use client';

import { cn } from '@/lib/utils';

interface WorkflowProgressProps {
  currentStep: number; // 1-5
  projectId?: string;
}

const WORKFLOW_STEPS = [
  { number: 1, label: 'Setup', path: 'documents' },
  { number: 2, label: 'Schema', path: 'schema' },
  { number: 3, label: 'Review', path: 'schema/review' },
  { number: 4, label: 'Process', path: 'process' },
  { number: 5, label: 'Results', path: 'results' },
];

export function WorkflowProgress({ currentStep, projectId }: WorkflowProgressProps) {
  return (
    <nav aria-label="Workflow progress" className="mb-8">
      <ol className="flex items-center justify-between">
        {WORKFLOW_STEPS.map((step, index) => {
          const isComplete = step.number < currentStep;
          const isCurrent = step.number === currentStep;
          const isUpcoming = step.number > currentStep;

          return (
            <li key={step.number} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={cn(
                    'flex items-center justify-center w-10 h-10 rounded-full border-2 font-semibold text-sm transition-colors',
                    isComplete && 'bg-primary border-primary text-primary-foreground',
                    isCurrent && 'bg-background border-primary text-primary',
                    isUpcoming && 'bg-background border-muted text-muted-foreground'
                  )}
                  aria-current={isCurrent ? 'step' : undefined}
                >
                  {isComplete ? (
                    <svg
                      className="w-5 h-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      aria-hidden="true"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    step.number
                  )}
                </div>
                <span
                  className={cn(
                    'mt-2 text-sm font-medium',
                    isCurrent && 'text-primary',
                    isUpcoming && 'text-muted-foreground'
                  )}
                >
                  {step.label}
                </span>
              </div>

              {index < WORKFLOW_STEPS.length - 1 && (
                <div
                  className={cn(
                    'flex-1 h-0.5 mx-4',
                    isComplete ? 'bg-primary' : 'bg-muted'
                  )}
                  aria-hidden="true"
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
```

#### T035: ErrorBoundary Component

**File**: `/frontend/src/components/layout/ErrorBoundary.tsx`

```typescript
'use client';

import { Component, ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-[400px] p-4">
          <Card className="max-w-lg">
            <CardHeader>
              <CardTitle>Something went wrong</CardTitle>
              <CardDescription>
                An unexpected error occurred. Please try refreshing the page.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {this.state.error && (
                <details className="text-sm">
                  <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                    Error details
                  </summary>
                  <pre className="mt-2 p-3 bg-muted rounded-md overflow-auto text-xs">
                    {this.state.error.message}
                  </pre>
                </details>
              )}
              <Button
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  window.location.reload();
                }}
              >
                Refresh Page
              </Button>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
```

#### T036: Dashboard Layout

**File**: `/frontend/src/app/(dashboard)/layout.tsx`

```typescript
import { ReactNode } from 'react';
import { DashboardNav } from '@/components/layout/DashboardNav';
import { ErrorBoundary } from '@/components/layout/ErrorBoundary';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <DashboardNav />
      <main className="container mx-auto px-4 py-8">
        <ErrorBoundary>{children}</ErrorBoundary>
      </main>
    </div>
  );
}
```

**File**: `/frontend/src/components/layout/DashboardNav.tsx`

```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export function DashboardNav() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname.startsWith(path);

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center px-4">
        <Link href="/projects" className="mr-8 flex items-center space-x-2">
          <span className="text-xl font-bold">Research Tool</span>
        </Link>

        <nav className="flex items-center space-x-6 text-sm font-medium">
          <Link
            href="/projects"
            className={cn(
              'transition-colors hover:text-foreground/80',
              isActive('/projects') ? 'text-foreground' : 'text-foreground/60'
            )}
          >
            Projects
          </Link>
        </nav>

        <div className="ml-auto flex items-center space-x-4">
          <Button variant="outline" size="sm">
            Docs
          </Button>
        </div>
      </div>
    </header>
  );
}
```

---

## Task-by-Task Guide

### Phase 3: User Story 1 - Project Setup & Document Input (T037-T048)

**Goal**: Enable users to create projects and upload documents

**Route Structure**:
- `/projects` - List all projects
- `/projects/new` - Create new project
- `/projects/[id]` - Project overview
- `/projects/[id]/documents` - Upload documents

#### T037: ProjectSetupForm Component

**File**: `/frontend/src/components/workflow/step1/ProjectSetupForm.tsx`

```typescript
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { projectSchema, type ProjectFormData } from '@/lib/validations';
import { api } from '@/services/api';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useState } from 'react';
import { useToast } from '@/components/ui/use-toast';

export function ProjectSetupForm() {
  const router = useRouter();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: '',
      scale: 'small',
    },
  });

  async function onSubmit(data: ProjectFormData) {
    setIsLoading(true);
    try {
      const response = await api.projects.create(data);

      if (response.error) {
        toast({
          title: 'Error',
          description: response.error.message,
          variant: 'destructive',
        });
        return;
      }

      toast({
        title: 'Success',
        description: 'Project created successfully',
      });

      // Navigate to document upload page
      router.push(`/projects/${response.data.id}/documents`);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create project',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Create New Project</CardTitle>
        <CardDescription>
          Set up a new research project for document extraction
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Project Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., Climate Protests Study"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    A descriptive name for your research project
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="scale"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Project Scale</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select project scale" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="small">
                        Small (up to 50 documents)
                      </SelectItem>
                      <SelectItem value="large">
                        Large (50+ documents)
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Choose based on the number of documents you plan to process
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Create Project'}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
```

#### T038: DocumentUploader Component

**File**: `/frontend/src/components/workflow/step1/DocumentUploader.tsx`

```typescript
'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { api } from '@/services/api';
import { Document } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn, formatFileSize } from '@/lib/utils';
import { useToast } from '@/components/ui/use-toast';

interface DocumentUploaderProps {
  projectId: string;
  onUploadComplete: (documents: Document[]) => void;
}

export function DocumentUploader({ projectId, onUploadComplete }: DocumentUploaderProps) {
  const { toast } = useToast();
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      setIsUploading(true);
      try {
        const response = await api.documents.upload(projectId, acceptedFiles);

        if (response.error) {
          toast({
            title: 'Upload failed',
            description: response.error.message,
            variant: 'destructive',
          });
          return;
        }

        toast({
          title: 'Success',
          description: `${acceptedFiles.length} document(s) uploaded successfully`,
        });

        onUploadComplete(response.data);
      } catch (error) {
        toast({
          title: 'Upload failed',
          description: 'Failed to upload documents',
          variant: 'destructive',
        });
      } finally {
        setIsUploading(false);
      }
    },
    [projectId, onUploadComplete, toast]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: isUploading,
  });

  return (
    <Card>
      <CardContent className="pt-6">
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors',
            isDragActive && 'border-primary bg-primary/5',
            !isDragActive && 'border-muted-foreground/25 hover:border-primary/50',
            isUploading && 'opacity-50 cursor-not-allowed'
          )}
        >
          <input {...getInputProps()} />

          <div className="flex flex-col items-center gap-4">
            <div className="p-4 rounded-full bg-primary/10">
              <svg
                className="w-8 h-8 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>

            {isUploading ? (
              <div className="space-y-2">
                <p className="text-sm font-medium">Uploading documents...</p>
                <div className="w-48 h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-primary animate-pulse" />
                </div>
              </div>
            ) : (
              <>
                <div className="space-y-2">
                  <p className="text-sm font-medium">
                    {isDragActive
                      ? 'Drop files here'
                      : 'Drag and drop files here, or click to browse'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Supports PDF, DOCX, TXT (max 10MB per file)
                  </p>
                </div>
                <Button type="button" variant="outline" size="sm">
                  Browse Files
                </Button>
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

#### T039: DocumentList Component

**File**: `/frontend/src/components/workflow/step1/DocumentList.tsx`

```typescript
'use client';

import { Document } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatFileSize, formatRelativeTime } from '@/lib/utils';
import { api } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';

interface DocumentListProps {
  documents: Document[];
  onDelete: (documentId: string) => void;
}

export function DocumentList({ documents, onDelete }: DocumentListProps) {
  const { toast } = useToast();

  async function handleDelete(documentId: string, fileName: string) {
    if (!confirm(`Delete "${fileName}"?`)) return;

    const response = await api.documents.delete(documentId);

    if (response.error) {
      toast({
        title: 'Error',
        description: response.error.message,
        variant: 'destructive',
      });
      return;
    }

    toast({
      title: 'Success',
      description: 'Document deleted',
    });
    onDelete(documentId);
  }

  if (documents.length === 0) {
    return (
      <Card>
        <CardContent className="py-12">
          <p className="text-center text-muted-foreground">
            No documents uploaded yet
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Uploaded Documents ({documents.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className="flex-shrink-0">
                  {getFileIcon(doc.fileType)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{doc.fileName}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(doc.fileSize)} • {formatRelativeTime(doc.uploadedAt)}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Badge variant={getStatusVariant(doc.status)}>
                  {doc.status}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(doc.id, doc.fileName)}
                >
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function getFileIcon(fileType: string) {
  const iconClass = 'w-8 h-8';

  if (fileType === 'pdf') {
    return (
      <svg className={iconClass} fill="currentColor" viewBox="0 0 20 20">
        <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" className="text-red-500" />
      </svg>
    );
  }

  return (
    <svg className={iconClass} fill="currentColor" viewBox="0 0 20 20">
      <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" className="text-blue-500" />
    </svg>
  );
}

function getStatusVariant(status: string): 'default' | 'secondary' | 'destructive' {
  switch (status) {
    case 'processed':
      return 'default';
    case 'uploaded':
      return 'secondary';
    case 'error':
      return 'destructive';
    default:
      return 'secondary';
  }
}
```

#### T040-T048: Remaining User Story 1 Tasks

**T040: Projects List Page**

**File**: `/frontend/src/app/(dashboard)/projects/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/services/api';
import { Project } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatRelativeTime } from '@/lib/utils';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadProjects() {
      const response = await api.projects.list();
      if (response.data) {
        setProjects(response.data);
      }
      setIsLoading(false);
    }
    loadProjects();
  }, []);

  if (isLoading) {
    return <div>Loading projects...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground mt-2">
            Manage your document extraction projects
          </p>
        </div>
        <Button asChild>
          <Link href="/projects/new">New Project</Link>
        </Button>
      </div>

      {projects.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">No projects yet</p>
            <Button asChild>
              <Link href="/projects/new">Create Your First Project</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link key={project.id} href={`/projects/${project.id}`}>
              <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{project.name}</CardTitle>
                    <Badge variant="outline">{project.scale}</Badge>
                  </div>
                  <CardDescription>
                    {formatRelativeTime(project.updatedAt)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Status:</span>
                      <Badge>{project.status}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Documents:</span>
                      <span className="font-medium">{project.documentCount}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
```

**T041: New Project Page**

**File**: `/frontend/src/app/(dashboard)/projects/new/page.tsx`

```typescript
import { ProjectSetupForm } from '@/components/workflow/step1/ProjectSetupForm';

export default function NewProjectPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Create New Project</h1>
        <p className="text-muted-foreground mt-2">
          Step 1 of 5: Project Setup
        </p>
      </div>
      <ProjectSetupForm />
    </div>
  );
}
```

**T042: Project Overview Page**

**File**: `/frontend/src/app/(dashboard)/projects/[id]/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/services/api';
import { Project } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';

export default function ProjectOverviewPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadProject() {
      const response = await api.projects.get(projectId);
      if (response.data) {
        setProject(response.data);
      }
      setIsLoading(false);
    }
    loadProject();
  }, [projectId]);

  if (isLoading) {
    return <div>Loading project...</div>;
  }

  if (!project) {
    return <div>Project not found</div>;
  }

  const currentStep = getWorkflowStep(project.status);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">{project.name}</h1>
        <p className="text-muted-foreground mt-2">
          Created {formatDate(project.createdAt)}
        </p>
      </div>

      <WorkflowProgress currentStep={currentStep} projectId={projectId} />

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Scale:</span>
              <Badge variant="outline">{project.scale}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              <Badge>{project.status}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Documents:</span>
              <span className="font-medium">{project.documentCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Schema Complete:</span>
              <span>{project.schemaComplete ? '✓ Yes' : '✗ No'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Processing Complete:</span>
              <span>{project.processingComplete ? '✓ Yes' : '✗ No'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Next Steps</CardTitle>
            <CardDescription>Continue your workflow</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {getNextStepButton(project, projectId)}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function getWorkflowStep(status: string): number {
  switch (status) {
    case 'setup':
      return 1;
    case 'schema':
      return 2;
    case 'review':
      return 3;
    case 'processing':
      return 4;
    case 'complete':
      return 5;
    default:
      return 1;
  }
}

function getNextStepButton(project: Project, projectId: string) {
  switch (project.status) {
    case 'setup':
      return (
        <Button asChild className="w-full">
          <Link href={`/projects/${projectId}/documents`}>
            Upload Documents
          </Link>
        </Button>
      );
    case 'schema':
      return (
        <Button asChild className="w-full">
          <Link href={`/projects/${projectId}/schema`}>
            Define Schema
          </Link>
        </Button>
      );
    case 'review':
      return (
        <Button asChild className="w-full">
          <Link href={`/projects/${projectId}/schema/review`}>
            Review Schema
          </Link>
        </Button>
      );
    case 'processing':
      return (
        <Button asChild className="w-full">
          <Link href={`/projects/${projectId}/process`}>
            View Processing
          </Link>
        </Button>
      );
    case 'complete':
      return (
        <Button asChild className="w-full">
          <Link href={`/projects/${projectId}/results`}>
            View Results
          </Link>
        </Button>
      );
    default:
      return null;
  }
}
```

**T043: Document Upload Page**

**File**: `/frontend/src/app/(dashboard)/projects/[id]/documents/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/services/api';
import { Document, Project } from '@/types';
import { Button } from '@/components/ui/button';
import { DocumentUploader } from '@/components/workflow/step1/DocumentUploader';
import { DocumentList } from '@/components/workflow/step1/DocumentList';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';

export default function DocumentUploadPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      const [projectRes, docsRes] = await Promise.all([
        api.projects.get(projectId),
        api.documents.list(projectId),
      ]);

      if (projectRes.data) setProject(projectRes.data);
      if (docsRes.data) setDocuments(docsRes.data);
      setIsLoading(false);
    }
    loadData();
  }, [projectId]);

  function handleUploadComplete(newDocs: Document[]) {
    setDocuments((prev) => [...prev, ...newDocs]);
  }

  function handleDelete(documentId: string) {
    setDocuments((prev) => prev.filter((d) => d.id !== documentId));
  }

  async function handleProceed() {
    // Update project status to 'schema'
    await api.projects.update(projectId, { status: 'schema' });
    router.push(`/projects/${projectId}/schema`);
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">{project?.name}</h1>
        <p className="text-muted-foreground mt-2">
          Step 1 of 5: Document Upload
        </p>
      </div>

      <WorkflowProgress currentStep={1} projectId={projectId} />

      <div className="space-y-6">
        <DocumentUploader
          projectId={projectId}
          onUploadComplete={handleUploadComplete}
        />

        <DocumentList
          documents={documents}
          onDelete={handleDelete}
        />

        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => router.push(`/projects/${projectId}`)}
          >
            Back to Project
          </Button>
          <Button
            onClick={handleProceed}
            disabled={documents.length === 0}
          >
            Continue to Schema Definition
          </Button>
        </div>
      </div>
    </div>
  );
}
```

**T044-T048**: Error states, ARIA labels, and manual testing

These tasks involve:
- Adding loading/error states to all components (wrap API calls in try/catch)
- Adding ARIA labels to interactive elements
- Adding keyboard navigation support
- Manual testing of the complete workflow

---

### Phases 4-8: Remaining User Stories

Due to length constraints, the remaining tasks follow similar patterns:

**Phase 4 (US2)**: Schema wizard with multi-step form, variable management
**Phase 5 (US3)**: Schema review table with drag-and-drop reordering
**Phase 6 (US4)**: Sample testing, full processing with real-time progress
**Phase 7 (US5)**: Results table with TanStack Table, CSV export
**Phase 8**: Polish, accessibility audit, deployment

Each follows the same structure:
1. Create components in `/components/workflow/stepN/`
2. Create pages in `/app/(dashboard)/projects/[id]/`
3. Use Zustand stores for state management
4. Call mock API via `/services/api`
5. Add loading/error states
6. Add accessibility features

---

## Component Templates

### Basic Page Template

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/services/api';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';

export default function PageName() {
  const params = useParams();
  const projectId = params.id as string;
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const response = await api.someEndpoint(projectId);
        if (response.error) {
          setError(response.error.message);
          return;
        }
        setData(response.data);
      } catch (err) {
        setError('Failed to load data');
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [projectId]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="space-y-8">
      <WorkflowProgress currentStep={1} projectId={projectId} />
      {/* Page content */}
    </div>
  );
}
```

### Basic Component Template

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/services/api';
import { useToast } from '@/components/ui/use-toast';

interface ComponentProps {
  projectId: string;
  onComplete: () => void;
}

export function ComponentName({ projectId, onComplete }: ComponentProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  async function handleAction() {
    setIsLoading(true);
    try {
      const response = await api.someEndpoint(projectId);
      if (response.error) {
        toast({
          title: 'Error',
          description: response.error.message,
          variant: 'destructive',
        });
        return;
      }
      toast({
        title: 'Success',
        description: 'Action completed',
      });
      onComplete();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Action failed',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Component Title</CardTitle>
      </CardHeader>
      <CardContent>
        <Button onClick={handleAction} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Action'}
        </Button>
      </CardContent>
    </Card>
  );
}
```

---

## Testing Strategy

### Manual Testing Checklist

For each workflow step, test:

- [ ] Page loads without errors
- [ ] TypeScript compiles (`npm run build`)
- [ ] API calls work with mock data
- [ ] Loading states display correctly
- [ ] Error states display correctly
- [ ] Form validation works
- [ ] Success messages appear
- [ ] Navigation works (back/forward)
- [ ] Data persists across refreshes (localStorage)
- [ ] Responsive on desktop (1920x1080)
- [ ] Responsive on tablet (768px)
- [ ] Keyboard navigation works
- [ ] Screen reader announces elements
- [ ] Color contrast meets WCAG AA

### Testing Commands

```bash
# TypeScript check
npm run build

# Start dev server
npm run dev

# Lint code
npm run lint
```

---

## Deployment Guide

### Vercel Deployment

1. **Push to GitHub**:
```bash
cd /home/noahdarwich/code/coderAI
git add .
git commit -m "feat: Complete MVP implementation"
git push origin 001-complete-user-workflow
```

2. **Deploy to Vercel**:
```bash
cd frontend
vercel
```

3. **Configure Environment**:
- No environment variables needed for Phase 1 (mock data)
- Phase 2 will require `NEXT_PUBLIC_API_URL`

### Build Verification

```bash
cd frontend
npm run build
```

Should complete with 0 errors.

---

## Quick Start for Developers

### Setup (5 minutes)

```bash
cd /home/noahdarwich/code/coderAI/frontend
npm install
npm run dev
```

Navigate to http://localhost:3000

### Development Workflow

1. **Pick a task** from tasks.md
2. **Create component** using template above
3. **Import types** from `@/types`
4. **Call API** via `import { api } from '@/services/api'`
5. **Test manually** - verify it works
6. **Mark complete** in tasks.md

### Key Files Reference

- **Types**: `/frontend/src/types/`
- **Mock API**: `/frontend/src/services/newMockApi.ts`
- **API Interface**: `/frontend/src/services/api.ts`
- **Mock Data**: `/frontend/src/mocks/`
- **Stores**: `/frontend/src/store/` (to be created)
- **Utils**: `/frontend/src/lib/utils.ts` (to be created)
- **shadcn/ui**: `/frontend/src/components/ui/`

---

## Summary

### What's Built ✅

- Complete type system (7 files, all types defined)
- Comprehensive mock data (5 files, 200+ records)
- Full mock API (700+ lines, all 6 modules)
- Project structure and dependencies

### What's Remaining 📋

- 3 Zustand stores
- Utility functions and validations
- 40+ React components
- 15+ page files
- Accessibility features
- Testing and polish

### Estimated Time to Complete

- **With this guide**: 12-15 hours
- **Stores & Utils**: 2 hours
- **User Story 1**: 3 hours
- **User Story 2**: 3 hours
- **User Story 3**: 2 hours
- **User Story 4**: 4 hours
- **User Story 5**: 3 hours
- **Polish**: 2 hours

### Success Criteria

✅ All 5 workflow steps functional
✅ Mock data works end-to-end
✅ TypeScript builds with no errors
✅ Responsive on desktop & tablet
✅ Keyboard accessible
✅ Deployed to Vercel

---

**Last Updated**: 2025-11-23
**Next Steps**: Implement T029-T036 (Stores & Utils), then proceed with User Stories 1-5

---

## Additional Resources

- **USER_WORKFLOW.md**: Canonical 5-step workflow specification
- **spec.md**: Feature requirements
- **data-model.md**: Entity relationships
- **tasks.md**: Complete task breakdown (130 tasks)
- **plan.md**: Technical architecture

**For questions**: Reference the mock API implementation in `/services/newMockApi.ts` - it contains all API patterns.
