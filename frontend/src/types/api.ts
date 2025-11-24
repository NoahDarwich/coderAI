// types/api.ts - API Response Wrappers
import { ProjectStatus } from './project';

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

// Request types
export interface CreateProjectRequest {
  name: string;
  scale: 'small' | 'large';
}

export interface UpdateProjectRequest {
  name?: string;
  status?: ProjectStatus;
}

export interface SaveSchemaRequest {
  variables: CreateVariableRequest[];
}

export interface CreateVariableRequest {
  name: string;
  type: 'text' | 'number' | 'date' | 'category' | 'boolean';
  instructions: string;
  classificationRules?: string[];
}

export interface UpdateVariableRequest {
  name?: string;
  type?: 'text' | 'number' | 'date' | 'category' | 'boolean';
  instructions?: string;
  classificationRules?: string[];
}

export interface ResultsListOptions {
  page?: number;
  pageSize?: number;
  minConfidence?: number;        // Filter by minimum confidence score
  documentId?: string;           // Filter by specific document
  variableId?: string;           // Filter by specific variable
}
