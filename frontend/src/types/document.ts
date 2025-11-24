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
