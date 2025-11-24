# Data Model: Frontend State & Mock Data Structures

**Feature**: 001-complete-user-workflow
**Date**: 2025-01-23
**Scope**: Frontend-only (Phase 1) - UI state models and TypeScript interfaces

**Important**: This is NOT a database schema. These are TypeScript interfaces for frontend state management and mock data structures.

## Core Entities (Frontend State)

### 1. Project

Represents a research project in the UI.

```typescript
// types/project.ts
export interface Project {
  id: string;                    // UUID
  name: string;                  // User-defined project name
  scale: 'small' | 'large';      // Project scale
  createdAt: string;             // ISO 8601 timestamp
  updatedAt: string;             // ISO 8601 timestamp
  status: ProjectStatus;         // Current workflow step
  documentCount: number;         // Number of uploaded documents
  schemaComplete: boolean;       // Has schema been confirmed?
  processingComplete: boolean;   // Has processing finished?
}

export type ProjectStatus =
  | 'setup'           // Step 1: Document upload
  | 'schema'          // Step 2: Schema definition
  | 'review'          // Step 3: Schema review
  | 'processing'      // Step 4: Processing
  | 'complete';       // Step 5: Results ready

// Mock data example
export const mockProject: Project = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  name: 'Climate Protests Study',
  scale: 'small',
  createdAt: '2025-01-23T10:00:00Z',
  updatedAt: '2025-01-23T14:30:00Z',
  status: 'complete',
  documentCount: 15,
  schemaComplete: true,
  processingComplete: true,
};
```

**Validation Rules**:
- `name`: 1-100 characters, required
- `scale`: Must be 'small' or 'large'
- `status`: Follows workflow progression (setup → schema → review → processing → complete)

**UI State Transitions**:
```
setup → schema (when documents uploaded)
schema → review (when variables defined)
review → processing (when schema confirmed)
processing → complete (when processing finished)
```

### 2. Document

Represents an uploaded document in the UI.

```typescript
// types/document.ts
export interface Document {
  id: string;                    // UUID
  projectId: string;             // Foreign key to Project
  fileName: string;              // Original file name
  fileType: DocumentType;        // File extension
  fileSize: number;              // Bytes
  uploadedAt: string;            // ISO 8601 timestamp
  status: DocumentStatus;        // Upload/processing status
  contentPreview?: string;       // First 500 chars (optional)
}

export type DocumentType = 'pdf' | 'docx' | 'txt';

export type DocumentStatus =
  | 'uploading'
  | 'uploaded'
  | 'processing'
  | 'processed'
  | 'error';

// Mock data example
export const mockDocument: Document = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  projectId: '550e8400-e29b-41d4-a716-446655440000',
  fileName: 'protest_article_2023.pdf',
  fileType: 'pdf',
  fileSize: 524288, // 512 KB
  uploadedAt: '2025-01-23T10:15:00Z',
  status: 'processed',
  contentPreview: 'On March 15, 2023, thousands gathered in Berlin...',
};
```

**Validation Rules**:
- `fileName`: Must include valid extension (.pdf, .docx, .txt)
- `fileSize`: Max 10 MB (10485760 bytes)
- `fileType`: Must match file extension

### 3. Schema (Variable Collection)

Represents the extraction schema defined by the user.

```typescript
// types/schema.ts
export interface Schema {
  id: string;                    // UUID
  projectId: string;             // Foreign key to Project
  variables: Variable[];         // Ordered list of variables
  createdAt: string;             // ISO 8601 timestamp
  confirmedAt?: string;          // When user confirmed schema (Step 3)
}

export interface Variable {
  id: string;                    // UUID
  name: string;                  // Variable name (user-defined)
  type: VariableType;            // Data type
  instructions: string;          // Extraction instructions
  classificationRules?: string[]; // For categorical variables
  order: number;                 // Display order (0-indexed)
}

export type VariableType =
  | 'text'
  | 'number'
  | 'date'
  | 'category'
  | 'boolean';

// Mock data example
export const mockSchema: Schema = {
  id: '789e0123-e45b-67c8-d901-234567890abc',
  projectId: '550e8400-e29b-41d4-a716-446655440000',
  variables: [
    {
      id: 'var-001',
      name: 'Date of Protest',
      type: 'date',
      instructions: 'Extract the date when the protest occurred. Look for explicit dates in the text.',
      order: 0,
    },
    {
      id: 'var-002',
      name: 'Location',
      type: 'text',
      instructions: 'Extract the city or location where the protest took place.',
      order: 1,
    },
    {
      id: 'var-003',
      name: 'Number of Participants',
      type: 'number',
      instructions: 'Extract the estimated number of protesters. Use the highest estimate if multiple are given.',
      order: 2,
    },
    {
      id: 'var-004',
      name: 'Protest Topic',
      type: 'category',
      instructions: 'Classify the main topic of the protest.',
      classificationRules: ['Climate Policy', 'Fossil Fuels', 'Deforestation', 'Other'],
      order: 3,
    },
    {
      id: 'var-005',
      name: 'Violence Occurred',
      type: 'boolean',
      instructions: 'Did violence occur during the protest? Answer true or false.',
      order: 4,
    },
  ],
  createdAt: '2025-01-23T11:00:00Z',
  confirmedAt: '2025-01-23T11:30:00Z',
};
```

**Validation Rules**:
- `variables`: Minimum 1 variable required
- `name`: 1-50 characters per variable
- `instructions`: 10-500 characters
- `classificationRules`: Required for type='category', 2-10 categories

### 4. Extraction Result

Represents extracted data from a single document.

```typescript
// types/extraction.ts
export interface ExtractionResult {
  id: string;                    // UUID
  projectId: string;             // Foreign key to Project
  documentId: string;            // Foreign key to Document
  values: ExtractedValue[];      // One per variable
  completedAt: string;           // ISO 8601 timestamp
}

export interface ExtractedValue {
  variableId: string;            // Foreign key to Variable
  value: string | number | boolean | null; // Extracted value
  confidence: number;            // 0-100 confidence score
  sourceText?: string;           // Text span that generated this value
}

export type ConfidenceLevel = 'high' | 'medium' | 'low';

export function getConfidenceLevel(score: number): ConfidenceLevel {
  if (score >= 85) return 'high';   // 🟢
  if (score >= 70) return 'medium'; // 🟡
  return 'low';                      // 🔴
}

// Mock data example
export const mockExtractionResult: ExtractionResult = {
  id: 'ext-001',
  projectId: '550e8400-e29b-41d4-a716-446655440000',
  documentId: '123e4567-e89b-12d3-a456-426614174000',
  values: [
    {
      variableId: 'var-001',
      value: '2023-03-15',
      confidence: 95,
      sourceText: 'On March 15, 2023, thousands gathered...',
    },
    {
      variableId: 'var-002',
      value: 'Berlin',
      confidence: 92,
      sourceText: '...thousands gathered in Berlin for a climate protest.',
    },
    {
      variableId: 'var-003',
      value: 5000,
      confidence: 78,
      sourceText: 'Estimates ranged from 3,000 to 5,000 participants.',
    },
    {
      variableId: 'var-004',
      value: 'Climate Policy',
      confidence: 88,
      sourceText: 'The protest focused on demanding stronger climate policies.',
    },
    {
      variableId: 'var-005',
      value: false,
      confidence: 99,
      sourceText: 'The demonstration remained peaceful throughout.',
    },
  ],
  completedAt: '2025-01-23T14:15:00Z',
};
```

**Validation Rules**:
- `confidence`: 0-100 integer
- `value`: Type must match Variable.type (string for text, number for number, etc.)
- `values`: Must have one entry per variable in schema

### 5. Processing Job

Represents a processing job (sample or full).

```typescript
// types/processing.ts
export interface ProcessingJob {
  id: string;                    // UUID
  projectId: string;             // Foreign key to Project
  type: 'sample' | 'full';       // Sample testing or full processing
  status: JobStatus;             // Current status
  progress: number;              // 0-100 percentage
  totalDocuments: number;        // Total docs to process
  processedDocuments: number;    // Docs processed so far
  startedAt: string;             // ISO 8601 timestamp
  completedAt?: string;          // ISO 8601 timestamp (when finished)
  logs: ProcessingLog[];         // Processing log entries
}

export type JobStatus =
  | 'queued'
  | 'processing'
  | 'completed'
  | 'failed';

export interface ProcessingLog {
  timestamp: string;             // ISO 8601 timestamp
  level: 'info' | 'warning' | 'error';
  message: string;               // Log message
  documentId?: string;           // Related document (optional)
}

// Mock data example
export const mockProcessingJob: ProcessingJob = {
  id: 'job-001',
  projectId: '550e8400-e29b-41d4-a716-446655440000',
  type: 'full',
  status: 'completed',
  progress: 100,
  totalDocuments: 15,
  processedDocuments: 15,
  startedAt: '2025-01-23T14:00:00Z',
  completedAt: '2025-01-23T14:15:00Z',
  logs: [
    {
      timestamp: '2025-01-23T14:00:00Z',
      level: 'info',
      message: 'Processing started for 15 documents',
    },
    {
      timestamp: '2025-01-23T14:01:00Z',
      level: 'info',
      message: 'Processing document: protest_article_2023.pdf',
      documentId: '123e4567-e89b-12d3-a456-426614174000',
    },
    // ... more logs
    {
      timestamp: '2025-01-23T14:15:00Z',
      level: 'info',
      message: 'Processing completed successfully',
    },
  ],
};
```

### 6. Export Configuration

Represents export settings chosen by user.

```typescript
// types/export.ts
export interface ExportConfig {
  format: ExportFormat;          // CSV only (Phase 1)
  structure: ExportStructure;    // Wide or long
  includeConfidence: boolean;    // Include confidence scores?
  includeSourceText: boolean;    // Include source text spans?
  minConfidence?: number;        // Filter by minimum confidence (0-100)
}

export type ExportFormat = 'csv';  // Phase 2: 'excel' | 'json'

export type ExportStructure =
  | 'wide'   // One row per document (columns = variables)
  | 'long';  // One row per extracted value

// Mock data example
export const mockExportConfig: ExportConfig = {
  format: 'csv',
  structure: 'wide',
  includeConfidence: true,
  includeSourceText: false,
  minConfidence: 70,
};
```

## UI State Management (Zustand Stores)

### Project Store

```typescript
// store/projectStore.ts
interface ProjectState {
  projects: Project[];
  currentProject: Project | null;

  // Actions
  createProject: (data: CreateProjectData) => void;
  loadProject: (id: string) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  deleteProject: (id: string) => void;
}
```

### Workflow Store

```typescript
// store/workflowStore.ts
interface WorkflowState {
  currentStep: number;           // 1-5
  canProceed: boolean;           // Can user proceed to next step?

  // Actions
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  validateStep: () => boolean;
}
```

### Schema Wizard Store

```typescript
// store/schemaWizardStore.ts
interface SchemaWizardState {
  variables: Variable[];
  currentVariableIndex: number;
  isDraft: boolean;

  // Actions
  addVariable: (variable: Variable) => void;
  updateVariable: (index: number, variable: Partial<Variable>) => void;
  deleteVariable: (index: number) => void;
  reorderVariables: (startIndex: number, endIndex: number) => void;
  saveDraft: () => void;
  clearDraft: () => void;
}
```

## Mock Data Collections

All mock data will be stored in `src/mocks/`:

```
mocks/
├── projects.ts         # 5 sample projects (various states)
├── documents.ts        # 50 sample documents (PDFs, DOCX, TXT)
├── schemas.ts          # 5 sample schemas (different variable types)
├── extractions.ts      # 75 sample extraction results
├── processingJobs.ts   # 10 sample jobs (queued, processing, completed, failed)
└── README.md           # Mock data documentation
```

**Mock Data Coverage**:
- **Success cases**: Complete workflows with good confidence scores
- **Error cases**: Failed uploads, processing errors, low confidence extractions
- **Edge cases**: Empty results, missing values, very long text
- **Large datasets**: 100+ documents for performance testing

## TypeScript Interface Exports

All types will be exported from a central index:

```typescript
// types/index.ts
export * from './project';
export * from './document';
export * from './schema';
export * from './extraction';
export * from './processing';
export * from './export';
export * from './api';  // API response types
```

## Summary

**Total Entity Types**: 6 core entities (Project, Document, Schema, Extraction, Processing Job, Export Config)

**Total Interfaces**: 15+ TypeScript interfaces

**Mock Data Files**: 6 files with ~200 mock records total

**UI Stores**: 3 Zustand stores for state management

**No Backend Dependencies**: All data structures designed for frontend-only implementation with localStorage persistence.
