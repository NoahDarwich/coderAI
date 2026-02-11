/**
 * Shared Backend ↔ Frontend Transform Functions
 *
 * Centralizes all snake_case backend responses → camelCase frontend types
 * and frontend → backend request transformations.
 */

import type { Project, Document, Variable, ProcessingJob, ExtractionResult, ExtractionDataPoint } from '@/lib/types/api';

// ─── Backend Response Types (snake_case) ────────────────────────────────

export interface BackendProject {
  id: string;
  user_id?: string;
  name: string;
  description?: string | null;
  scale: 'SMALL' | 'LARGE';
  language: string;
  domain?: string | null;
  unit_of_observation?: Record<string, unknown> | null;
  status: 'CREATED' | 'SCHEMA_DEFINED' | 'SCHEMA_APPROVED' | 'SAMPLE_TESTING' | 'READY' | 'PROCESSING' | 'COMPLETE' | 'ERROR';
  created_at: string;
  updated_at: string;
  variable_count?: number;
  document_count?: number;
}

export interface BackendDocument {
  id: string;
  project_id: string;
  name: string;
  content_type: 'PDF' | 'DOCX' | 'TXT' | 'HTML';
  size_bytes: number;
  status?: 'UPLOADED' | 'PARSED' | 'READY' | 'FAILED';
  word_count?: number;
  error_message?: string;
  uploaded_at: string;
  content_preview?: string;
}

export interface BackendVariable {
  id: string;
  project_id: string;
  name: string;
  type: 'TEXT' | 'NUMBER' | 'DATE' | 'BOOLEAN' | 'CATEGORY' | 'LOCATION';
  instructions: string;
  classification_rules?: Record<string, unknown> | null;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface BackendProcessingJob {
  id: string;
  project_id: string;
  job_type: 'SAMPLE' | 'FULL';
  status: 'PENDING' | 'PROCESSING' | 'PAUSED' | 'COMPLETE' | 'FAILED' | 'CANCELLED';
  progress: number;
  document_ids: string[];
  documents_processed?: number;
  documents_failed?: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface BackendDocumentResult {
  document_id: string;
  document_name: string;
  data: Record<string, {
    value: unknown;
    confidence: number;
    source_text?: string;
  }>;
  flagged: boolean;
  extracted_at: string;
  average_confidence?: number;
}

export interface BackendProjectResults {
  project_id: string;
  total_documents: number;
  documents: BackendDocumentResult[];
}

export interface BackendExtraction {
  id: string;
  job_id: string;
  document_id: string;
  variable_id: string;
  value: unknown;
  confidence: number;
  source_text?: string;
  flagged: boolean;
  created_at: string;
}

export interface BackendJobResults {
  job_id: string;
  project_id: string;
  total_extractions: number;
  extractions: BackendExtraction[];
}

export interface BackendProcessingLog {
  id: string;
  job_id: string;
  document_id?: string;
  log_level: 'INFO' | 'WARNING' | 'ERROR';
  message: string;
  created_at: string;
}

// ─── Backend Request Types ──────────────────────────────────────────────

export interface BackendProjectCreate {
  name: string;
  scale: 'SMALL' | 'LARGE';
  language?: string;
  domain?: string;
}

export interface BackendProjectUpdate {
  name?: string;
  domain?: string;
}

export interface BackendVariableCreate {
  name: string;
  type: 'TEXT' | 'NUMBER' | 'DATE' | 'BOOLEAN' | 'CATEGORY' | 'LOCATION';
  instructions: string;
  classification_rules?: Record<string, unknown>;
  order: number;
}

export interface BackendVariableUpdate {
  name?: string;
  instructions?: string;
  classification_rules?: Record<string, unknown>;
  order?: number;
}

// ─── Transform Functions: Backend → Frontend ────────────────────────────

const PROJECT_STATUS_MAP: Record<BackendProject['status'], Project['status']> = {
  'CREATED': 'draft',
  'SCHEMA_DEFINED': 'schema_defined',
  'SCHEMA_APPROVED': 'schema_approved',
  'SAMPLE_TESTING': 'sample_testing',
  'READY': 'ready',
  'PROCESSING': 'processing',
  'COMPLETE': 'completed',
  'ERROR': 'error',
};

export function transformProject(bp: BackendProject): Project {
  return {
    id: bp.id,
    userId: bp.user_id || '',
    name: bp.name,
    description: bp.description || bp.domain || '',
    status: PROJECT_STATUS_MAP[bp.status] || 'draft',
    documentCount: bp.document_count ?? 0,
    scale: bp.scale,
    language: bp.language,
    domain: bp.domain ?? undefined,
    unitOfObservation: bp.unit_of_observation ?? undefined,
    createdAt: bp.created_at,
    updatedAt: bp.updated_at,
  };
}

const DOCUMENT_STATUS_MAP: Record<NonNullable<BackendDocument['status']>, Document['status']> = {
  'UPLOADED': 'uploaded',
  'PARSED': 'parsed',
  'READY': 'ready',
  'FAILED': 'failed',
};

export function transformDocument(bd: BackendDocument): Document {
  const ct = bd.content_type.toLowerCase() as Document['contentType'];
  const mappedStatus = bd.status ? (DOCUMENT_STATUS_MAP[bd.status] || 'uploaded') : 'uploaded';
  return {
    id: bd.id,
    projectId: bd.project_id,
    filename: bd.name,
    name: bd.name,
    fileType: ct,
    contentType: ct,
    fileSize: bd.size_bytes,
    sizeBytes: bd.size_bytes,
    wordCount: bd.word_count,
    status: mappedStatus,
    errorMessage: bd.error_message,
    uploadedAt: bd.uploaded_at,
  };
}

export function transformVariable(bv: BackendVariable): Variable {
  const result: Variable = {
    id: bv.id,
    name: bv.name,
    type: bv.type,
    instructions: bv.instructions,
    description: bv.instructions,
    prompt: bv.instructions,
    order: bv.order,
  };

  if (bv.classification_rules && (bv.classification_rules as Record<string, unknown>).categories) {
    result.categories = (bv.classification_rules as Record<string, unknown>).categories as string[];
  }

  return result;
}

const JOB_STATUS_MAP: Record<BackendProcessingJob['status'], ProcessingJob['status']> = {
  'PENDING': 'pending',
  'PROCESSING': 'processing',
  'PAUSED': 'paused',
  'COMPLETE': 'completed',
  'FAILED': 'failed',
  'CANCELLED': 'cancelled',
};

export function transformJob(bj: BackendProcessingJob): ProcessingJob {
  const totalDocuments = bj.document_ids?.length ?? 0;
  const processedDocuments = bj.documents_processed ?? Math.round((bj.progress / 100) * totalDocuments);

  return {
    id: bj.id,
    projectId: bj.project_id,
    type: bj.job_type.toLowerCase() as 'sample' | 'full',
    status: JOB_STATUS_MAP[bj.status] || 'pending',
    progress: bj.progress,
    totalDocuments,
    processedDocuments,
    startedAt: bj.started_at || bj.created_at,
    completedAt: bj.completed_at,
  };
}

export function transformDocumentResult(dr: BackendDocumentResult): ExtractionResult {
  const data: Record<string, ExtractionDataPoint> = {};
  for (const [key, val] of Object.entries(dr.data)) {
    data[key] = {
      value: val.value as string | number | null,
      confidence: val.confidence,
      sourceText: val.source_text,
    };
  }

  return {
    id: dr.document_id,
    documentId: dr.document_id,
    documentName: dr.document_name,
    schemaId: '',
    data,
    flagged: dr.flagged,
    extractedAt: dr.extracted_at,
  };
}

// ─── Transform Functions: Frontend → Backend ────────────────────────────

export function toBackendProjectCreate(data: {
  name: string;
  description?: string;
}): BackendProjectCreate {
  return {
    name: data.name,
    scale: 'SMALL',
    language: 'en',
    domain: data.description,
  };
}

export function toBackendProjectUpdate(data: Partial<Project>): BackendProjectUpdate {
  const update: BackendProjectUpdate = {};
  if (data.name !== undefined) update.name = data.name;
  if (data.description !== undefined) update.domain = data.description;
  return update;
}

export function toBackendVariableCreate(
  variable: Omit<Variable, 'id'>,
  order: number = 1
): BackendVariableCreate {
  const create: BackendVariableCreate = {
    name: variable.name,
    type: variable.type,
    instructions: variable.instructions || variable.description || variable.prompt || '',
    order,
  };

  if (variable.type === 'CATEGORY' && variable.categories) {
    create.classification_rules = {
      categories: variable.categories,
      allow_multiple: false,
    };
  }

  return create;
}

export function toBackendVariableUpdate(updates: Partial<Variable>): BackendVariableUpdate {
  const update: BackendVariableUpdate = {};
  if (updates.name) update.name = updates.name;
  if (updates.instructions || updates.description || updates.prompt) {
    update.instructions = updates.instructions || updates.description || updates.prompt || '';
  }
  if (updates.order !== undefined) update.order = updates.order;
  if (updates.type === 'CATEGORY' && updates.categories) {
    update.classification_rules = {
      categories: updates.categories,
      allow_multiple: false,
    };
  }
  return update;
}
