/**
 * Document-related types and utilities
 */

import { Document } from './api';

/**
 * Upload File with Progress
 */
export interface UploadFile {
  file: File;
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  errorMessage?: string;
}

/**
 * File Validation Result
 */
export interface FileValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * Supported File Types
 */
export const SUPPORTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
} as const;

export type SupportedMimeType = keyof typeof SUPPORTED_FILE_TYPES;

/**
 * File Upload Configuration
 */
export interface FileUploadConfig {
  maxFileSize: number; // bytes
  maxFiles: number;
  acceptedFileTypes: SupportedMimeType[];
}

/**
 * Default Upload Config
 */
export const DEFAULT_UPLOAD_CONFIG: FileUploadConfig = {
  maxFileSize: 10 * 1024 * 1024, // 10MB
  maxFiles: 100,
  acceptedFileTypes: Object.keys(SUPPORTED_FILE_TYPES) as SupportedMimeType[],
};

/**
 * Document Filter Options
 */
export interface DocumentFilterOptions {
  status?: Document['status'][];
  fileType?: Document['fileType'][];
  search?: string;
  sortBy?: 'filename' | 'uploadedAt' | 'fileSize';
  sortOrder?: 'asc' | 'desc';
}

/**
 * Document Preview Props
 */
export interface DocumentPreviewProps {
  document: Document;
  onClose: () => void;
}
