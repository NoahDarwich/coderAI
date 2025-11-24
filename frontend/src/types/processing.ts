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
