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
 * Project Model
 */
export interface Project {
  id: string;
  userId: string;
  name: string;
  description: string;
  status: 'draft' | 'processing' | 'completed' | 'error';
  documentCount: number;
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
  filename: string;
  fileType: 'pdf' | 'docx' | 'txt';
  fileSize: number; // bytes
  content?: string; // Full text content (not always loaded)
  status: 'pending' | 'uploaded' | 'parsing' | 'parsed' | 'processing' | 'completed' | 'error';
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
 * Schema Variable Definition
 */
export interface SchemaVariable {
  id: string;
  name: string;
  type: 'date' | 'location' | 'entity' | 'custom' | 'classification';
  description: string;
  prompt?: string; // The extraction prompt for this variable
  categories?: string[]; // For classification types
}

/**
 * Extraction Schema Configuration
 */
export interface SchemaConfig {
  id: string;
  projectId: string;
  conversationHistory: ChatMessage[];
  variables: SchemaVariable[];
  prompts: Record<string, string>; // Variable name -> extraction prompt
  approved?: boolean; // Whether the schema has been approved by the user
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
  sourceText?: string; // The text snippet this was extracted from
}

/**
 * Extraction Result (one per document)
 */
export interface ExtractionResult {
  id: string;
  documentId: string;
  documentName: string;
  schemaId: string;
  data: Record<string, ExtractionDataPoint>; // Variable name -> extracted data
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
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  totalDocuments: number;
  processedDocuments: number;
  currentDocument?: string;
  estimatedTimeRemaining?: number; // seconds
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
  format: 'wide' | 'long';
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
  name?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  expiresAt: string;
}
