/**
 * Core API Types
 * All types that represent data from the backend API (or mock API)
 */

/**
 * User Model
 */
export interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string;
  lastLogin?: string;
}

/**
 * Unit of Observation — what each row in the exported dataset represents.
 * Stored as JSONB on the backend; this is the canonical frontend shape.
 */
export interface UnitOfObservation {
  whatEachRowRepresents: string;
  rowsPerDocument: 'one' | 'multiple';
  entityIdentificationPattern?: string;
}

/**
 * Project Model
 */
export interface Project {
  id: string;
  userId: string;
  name: string;
  description: string;
  status: 'draft' | 'schema_defined' | 'schema_approved' | 'sample_testing' | 'ready' | 'processing' | 'completed' | 'error';
  documentCount: number;
  scale?: string;
  language?: string;
  domain?: string;
  unitOfObservation?: Record<string, unknown>;
  schemaConfig?: SchemaConfig;
  createdAt: string;
  updatedAt: string;
}

/**
 * Document Model
 */
export interface Document {
  id: string;
  projectId: string;
  /** @deprecated Use name */
  filename: string;
  name: string;
  /** @deprecated Use contentType */
  fileType: 'pdf' | 'docx' | 'txt' | 'html';
  contentType: 'pdf' | 'docx' | 'txt' | 'html';
  /** @deprecated Use sizeBytes */
  fileSize: number;
  sizeBytes: number;
  wordCount?: number;
  content?: string;
  status: 'pending' | 'uploaded' | 'parsed' | 'ready' | 'processing' | 'completed' | 'failed' | 'error';
  errorMessage?: string;
  uploadedAt: string;
}

/**
 * Chat Message
 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

/**
 * Variable Definition (replaces SchemaVariable)
 */
export interface Variable {
  id: string;
  name: string;
  type: 'TEXT' | 'NUMBER' | 'DATE' | 'CATEGORY' | 'BOOLEAN' | 'LOCATION';
  instructions: string;
  /** @deprecated Use instructions */
  description?: string;
  prompt?: string;
  categories?: string[];
  order?: number;
}

/** @deprecated Use Variable */
export type SchemaVariable = Variable;

/**
 * Extraction Schema Configuration
 */
export interface SchemaConfig {
  id: string;
  projectId: string;
  conversationHistory: ChatMessage[];
  variables: Variable[];
  prompts: Record<string, string>;
  approved?: boolean;
  version: number;
  createdAt: string;
  updatedAt: string;
}

/**
 * Extracted Data Point
 */
export interface ExtractionDataPoint {
  value: string | number | null;
  confidence: number; // 0-100
  sourceText?: string;
}

/**
 * Extraction Result (one per document)
 */
export interface ExtractionResult {
  id: string;
  documentId: string;
  documentName: string;
  schemaId: string;
  data: Record<string, ExtractionDataPoint>;
  flagged: boolean;
  reviewNotes?: string;
  extractedAt: string;
}

/**
 * Processing Job
 */
export interface ProcessingJob {
  id: string;
  projectId: string;
  type: 'sample' | 'full';
  status: 'pending' | 'processing' | 'paused' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  totalDocuments: number;
  processedDocuments: number;
  currentDocument?: string;
  estimatedTimeRemaining?: number;
  startedAt?: string;
  completedAt?: string;
  errorMessage?: string;
}

/**
 * API Response Wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

/**
 * Paginated Response
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/**
 * Export Configuration
 */
export interface ExportConfig {
  format: 'CSV_WIDE' | 'CSV_LONG' | 'EXCEL' | 'JSON' | 'CODEBOOK';
  includeConfidence: boolean;
  includeSourceText: boolean;
  includeFlags: boolean;
  minConfidenceThreshold?: number;
  flaggedOnly?: boolean;
}

/**
 * Authentication Types
 */
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  tokenType?: string;
}
