/**
 * Mock API Interface for Frontend (Phase 1)
 *
 * This file defines the TypeScript interfaces for the mock API service layer.
 * These interfaces will be implemented by mockApi.ts in Phase 1.
 * In Phase 2, realApi.ts will implement the same interfaces with actual HTTP calls.
 *
 * NO BACKEND IMPLEMENTATION - Frontend only
 */

import {
  Project,
  Document,
  Schema,
  Variable,
  ExtractionResult,
  ProcessingJob,
  ExportConfig,
} from '../../../frontend/src/types';

// ============================================================================
// API Response Wrappers
// ============================================================================

export interface ApiResponse<T> {
  data: T;
  error?: ApiError;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

// ============================================================================
// Projects API
// ============================================================================

export interface ProjectsApi {
  /**
   * List all projects for the current user
   */
  list(): Promise<ApiResponse<Project[]>>;

  /**
   * Get a single project by ID
   */
  get(id: string): Promise<ApiResponse<Project>>;

  /**
   * Create a new project
   */
  create(data: CreateProjectRequest): Promise<ApiResponse<Project>>;

  /**
   * Update an existing project
   */
  update(id: string, data: UpdateProjectRequest): Promise<ApiResponse<Project>>;

  /**
   * Delete a project (and all associated data)
   */
  delete(id: string): Promise<ApiResponse<void>>;
}

export interface CreateProjectRequest {
  name: string;
  scale: 'small' | 'large';
}

export interface UpdateProjectRequest {
  name?: string;
  status?: Project['status'];
}

// ============================================================================
// Documents API
// ============================================================================

export interface DocumentsApi {
  /**
   * List all documents for a project
   */
  list(projectId: string): Promise<ApiResponse<Document[]>>;

  /**
   * Get a single document by ID
   */
  get(documentId: string): Promise<ApiResponse<Document>>;

  /**
   * Upload documents to a project
   * Phase 1: Accepts File objects, simulates upload
   * Phase 2: Will use multipart/form-data to real backend
   */
  upload(projectId: string, files: File[]): Promise<ApiResponse<Document[]>>;

  /**
   * Delete a document
   */
  delete(documentId: string): Promise<ApiResponse<void>>;

  /**
   * Get document content (for preview)
   * Phase 1: Returns mock text
   * Phase 2: Fetches from backend/storage
   */
  getContent(documentId: string): Promise<ApiResponse<string>>;
}

// ============================================================================
// Schema API
// ============================================================================

export interface SchemaApi {
  /**
   * Get the schema for a project
   */
  get(projectId: string): Promise<ApiResponse<Schema | null>>;

  /**
   * Create or update the schema for a project
   */
  save(projectId: string, data: SaveSchemaRequest): Promise<ApiResponse<Schema>>;

  /**
   * Confirm schema (lock it for processing)
   * After confirmation, schema cannot be edited without resetting processing
   */
  confirm(projectId: string): Promise<ApiResponse<Schema>>;

  /**
   * Add a variable to the schema
   */
  addVariable(projectId: string, variable: CreateVariableRequest): Promise<ApiResponse<Variable>>;

  /**
   * Update a variable
   */
  updateVariable(projectId: string, variableId: string, data: UpdateVariableRequest): Promise<ApiResponse<Variable>>;

  /**
   * Delete a variable
   */
  deleteVariable(projectId: string, variableId: string): Promise<ApiResponse<void>>;

  /**
   * Reorder variables
   */
  reorderVariables(projectId: string, variableIds: string[]): Promise<ApiResponse<Schema>>;
}

export interface SaveSchemaRequest {
  variables: CreateVariableRequest[];
}

export interface CreateVariableRequest {
  name: string;
  type: Variable['type'];
  instructions: string;
  classificationRules?: string[];
}

export interface UpdateVariableRequest {
  name?: string;
  type?: Variable['type'];
  instructions?: string;
  classificationRules?: string[];
}

// ============================================================================
// Processing API
// ============================================================================

export interface ProcessingApi {
  /**
   * Start sample processing (test on 10-20 documents)
   */
  startSample(projectId: string, sampleSize: number): Promise<ApiResponse<ProcessingJob>>;

  /**
   * Start full processing (all documents)
   */
  startFull(projectId: string): Promise<ApiResponse<ProcessingJob>>;

  /**
   * Get processing job status
   */
  getJob(jobId: string): Promise<ApiResponse<ProcessingJob>>;

  /**
   * Cancel a processing job
   * Phase 1: Stops mock processing
   * Phase 2: Sends cancellation to backend
   */
  cancelJob(jobId: string): Promise<ApiResponse<void>>;
}

// ============================================================================
// Results API
// ============================================================================

export interface ResultsApi {
  /**
   * Get extraction results for a project
   * Supports filtering and pagination
   */
  list(projectId: string, options?: ResultsListOptions): Promise<ApiResponse<PaginatedResponse<ExtractionResult>>>;

  /**
   * Get a single extraction result
   */
  get(extractionId: string): Promise<ApiResponse<ExtractionResult>>;

  /**
   * Flag an extraction result as correct/incorrect
   * Used in sample testing for user feedback
   */
  flag(extractionId: string, isCorrect: boolean): Promise<ApiResponse<void>>;
}

export interface ResultsListOptions {
  page?: number;
  pageSize?: number;
  minConfidence?: number;        // Filter by minimum confidence score
  documentId?: string;           // Filter by specific document
  variableId?: string;           // Filter by specific variable
}

// ============================================================================
// Export API
// ============================================================================

export interface ExportApi {
  /**
   * Generate export file
   * Phase 1: Returns CSV blob immediately
   * Phase 2: Creates async export job, returns job ID
   */
  generate(projectId: string, config: ExportConfig): Promise<ApiResponse<ExportResult>>;

  /**
   * Download export file
   * Phase 1: Returns blob URL
   * Phase 2: Returns signed download URL from storage
   */
  download(exportId: string): Promise<ApiResponse<Blob>>;
}

export interface ExportResult {
  id: string;
  fileName: string;
  fileSize: number;
  createdAt: string;
  downloadUrl?: string;          // Available in Phase 1 (blob URL)
}

// ============================================================================
// Main API Interface (Combined)
// ============================================================================

/**
 * This is the main API interface that components will use.
 * In Phase 1: Implemented by mockApi.ts
 * In Phase 2: Implemented by realApi.ts (with HTTP calls)
 */
export interface ApiClient {
  projects: ProjectsApi;
  documents: DocumentsApi;
  schema: SchemaApi;
  processing: ProcessingApi;
  results: ResultsApi;
  export: ExportApi;
}

// ============================================================================
// Usage Example (in components)
// ============================================================================

/**
 * Example component usage:
 *
 * ```typescript
 * import { api } from '@/services/api';
 *
 * export function ProjectsList() {
 *   const [projects, setProjects] = useState<Project[]>([]);
 *
 *   useEffect(() => {
 *     api.projects.list().then(response => {
 *       if (response.data) {
 *         setProjects(response.data);
 *       }
 *     });
 *   }, []);
 *
 *   return <div>{...}</div>;
 * }
 * ```
 *
 * In Phase 1, `api` is imported from `services/mockApi.ts`
 * In Phase 2, change one line: import from `services/realApi.ts`
 */
