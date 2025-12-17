/**
 * Processing API Client
 * TanStack Query hooks for job processing operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

/**
 * Backend Types (matching backend schema)
 */
export interface BackendProcessingJob {
  id: string;
  project_id: string;
  job_type: 'SAMPLE' | 'FULL';
  status: 'PENDING' | 'PROCESSING' | 'COMPLETE' | 'FAILED' | 'CANCELLED';
  progress: number;
  document_ids: string[];
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface BackendJobResults {
  job_id: string;
  project_id: string;
  total_extractions: number;
  extractions: BackendExtraction[];
}

export interface BackendExtraction {
  id: string;
  job_id: string;
  document_id: string;
  variable_id: string;
  value: any;
  confidence: number;
  source_text?: string;
  flagged: boolean;
  created_at: string;
}

export interface BackendProjectResults {
  project_id: string;
  total_documents: number;
  documents: BackendDocumentResult[];
}

export interface BackendDocumentResult {
  document_id: string;
  document_name: string;
  data: Record<string, {
    value: any;
    confidence: number;
    source_text?: string;
  }>;
  flagged: boolean;
  extracted_at: string;
  average_confidence?: number;
}

export interface BackendProcessingLog {
  id: string;
  job_id: string;
  document_id?: string;
  log_level: 'INFO' | 'WARNING' | 'ERROR';
  message: string;
  created_at: string;
}

/**
 * Frontend Types (for UI compatibility)
 */
export interface ProcessingJob {
  id: string;
  projectId: string;
  type: 'sample' | 'full';
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  documentIds: string[];
  totalDocuments: number;
  processedDocuments: number;
  startedAt: string;
  completedAt?: string;
  logs: ProcessingLog[];
}

export interface ProcessingLog {
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  documentId?: string;
}

/**
 * Transform backend job to frontend format
 */
function transformBackendJob(backendJob: BackendProcessingJob, logs: BackendProcessingLog[] = []): ProcessingJob {
  const statusMap: Record<BackendProcessingJob['status'], ProcessingJob['status']> = {
    'PENDING': 'pending',
    'PROCESSING': 'processing',
    'COMPLETE': 'completed',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled',
  };

  const logLevelMap: Record<BackendProcessingLog['log_level'], ProcessingLog['level']> = {
    'INFO': 'info',
    'WARNING': 'warning',
    'ERROR': 'error',
  };

  const totalDocuments = backendJob.document_ids.length;
  const processedDocuments = Math.round((backendJob.progress / 100) * totalDocuments);

  return {
    id: backendJob.id,
    projectId: backendJob.project_id,
    type: backendJob.job_type.toLowerCase() as 'sample' | 'full',
    status: statusMap[backendJob.status] || 'pending',
    progress: backendJob.progress,
    documentIds: backendJob.document_ids,
    totalDocuments,
    processedDocuments,
    startedAt: backendJob.created_at,
    completedAt: backendJob.completed_at,
    logs: logs.map(log => ({
      timestamp: log.created_at,
      level: logLevelMap[log.log_level] || 'info',
      message: log.message,
      documentId: log.document_id,
    })),
  };
}

/**
 * Mock API functions (for development)
 */
const mockProcessingApi = {
  createJob: async (
    projectId: string,
    jobType: 'SAMPLE' | 'FULL',
    documentIds: string[]
  ): Promise<ProcessingJob> => {
    await new Promise((resolve) => setTimeout(resolve, 500));

    return {
      id: `job-${Date.now()}`,
      projectId,
      type: jobType.toLowerCase() as 'sample' | 'full',
      status: 'pending',
      progress: 0,
      documentIds,
      totalDocuments: documentIds.length,
      processedDocuments: 0,
      startedAt: new Date().toISOString(),
      logs: [{
        timestamp: new Date().toISOString(),
        level: 'info',
        message: `Job created with ${documentIds.length} documents`,
      }],
    };
  },

  getJobStatus: async (jobId: string): Promise<ProcessingJob> => {
    await new Promise((resolve) => setTimeout(resolve, 300));

    // Mock: simulate progress
    const progress = Math.min(100, Math.floor(Math.random() * 30) + 50);

    return {
      id: jobId,
      projectId: 'mock-project',
      type: 'full',
      status: progress === 100 ? 'completed' : 'processing',
      progress,
      documentIds: [],
      totalDocuments: 10,
      processedDocuments: Math.floor((progress / 100) * 10),
      startedAt: new Date().toISOString(),
      logs: [],
    };
  },

  getJobResults: async (jobId: string): Promise<BackendJobResults> => {
    await new Promise((resolve) => setTimeout(resolve, 500));

    return {
      job_id: jobId,
      project_id: 'mock-project',
      total_extractions: 0,
      extractions: [],
    };
  },

  cancelJob: async (jobId: string): Promise<void> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
  },
};

/**
 * Real API functions
 */
const realProcessingApi = {
  createJob: async (
    projectId: string,
    jobType: 'SAMPLE' | 'FULL',
    documentIds: string[]
  ): Promise<ProcessingJob> => {
    const response = await apiClient.post<BackendProcessingJob>(
      `/api/v1/projects/${projectId}/jobs`,
      {
        job_type: jobType,
        document_ids: documentIds,
      }
    );

    return transformBackendJob(response);
  },

  getJobStatus: async (jobId: string): Promise<ProcessingJob> => {
    const response = await apiClient.get<BackendProcessingJob>(
      `/api/v1/jobs/${jobId}`
    );

    // Also fetch logs if available
    let logs: BackendProcessingLog[] = [];
    try {
      // Backend returns logs in job detail, but let's handle both cases
      logs = (response as any).logs || [];
    } catch (error) {
      // Logs endpoint might not exist, that's ok
    }

    return transformBackendJob(response, logs);
  },

  getJobResults: async (jobId: string): Promise<BackendJobResults> => {
    const response = await apiClient.get<BackendJobResults>(
      `/api/v1/jobs/${jobId}/results`
    );
    return response;
  },

  getProjectResults: async (projectId: string): Promise<BackendProjectResults> => {
    const response = await apiClient.get<BackendProjectResults>(
      `/api/v1/projects/${projectId}/results`
    );
    return response;
  },

  cancelJob: async (jobId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/jobs/${jobId}`);
  },
};

/**
 * Select API based on environment
 */
const processingApi = apiClient.useMockData ? mockProcessingApi : realProcessingApi;

/**
 * Query Keys
 */
export const processingKeys = {
  all: ['processing'] as const,
  jobs: () => [...processingKeys.all, 'jobs'] as const,
  job: (jobId: string) => [...processingKeys.jobs(), jobId] as const,
  results: (jobId: string) => [...processingKeys.all, 'results', jobId] as const,
  projectResults: (projectId: string) => [...processingKeys.all, 'project-results', projectId] as const,
};

/**
 * Create processing job mutation
 */
export function useCreateJob(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      jobType,
      documentIds
    }: {
      jobType: 'SAMPLE' | 'FULL';
      documentIds: string[];
    }) => processingApi.createJob(projectId, jobType, documentIds),
    onSuccess: (job) => {
      // Cache the created job
      queryClient.setQueryData(processingKeys.job(job.id), job);

      // Invalidate jobs list
      queryClient.invalidateQueries({ queryKey: processingKeys.jobs() });
    },
  });
}

/**
 * Poll job status with automatic refetch
 */
export function useJobStatus(jobId: string | null, enabled: boolean = true) {
  return useQuery({
    queryKey: processingKeys.job(jobId || 'none'),
    queryFn: () => {
      if (!jobId) throw new Error('Job ID is required');
      return processingApi.getJobStatus(jobId);
    },
    enabled: enabled && !!jobId,
    refetchInterval: (data) => {
      // Stop polling when job is complete, failed, or cancelled
      if (!data) return false;

      if (data.status === 'completed' ||
          data.status === 'failed' ||
          data.status === 'cancelled') {
        return false;
      }

      // Poll every 2 seconds while processing
      return 2000;
    },
    refetchIntervalInBackground: true,
    staleTime: 1000, // Consider data stale after 1 second
  });
}

/**
 * Fetch job results
 */
export function useJobResults(jobId: string | null, enabled: boolean = true) {
  return useQuery({
    queryKey: processingKeys.results(jobId || 'none'),
    queryFn: () => {
      if (!jobId) throw new Error('Job ID is required');
      return processingApi.getJobResults(jobId);
    },
    enabled: enabled && !!jobId,
    staleTime: 1000 * 60 * 5, // Results don't change, cache for 5 minutes
  });
}

/**
 * Fetch project results (aggregated by document)
 */
export function useProjectResults(projectId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: processingKeys.projectResults(projectId),
    queryFn: () => {
      if (apiClient.useMockData) {
        // Mock mode - return empty results
        return {
          project_id: projectId,
          total_documents: 0,
          documents: [],
        };
      }
      return realProcessingApi.getProjectResults(projectId);
    },
    enabled: enabled && !!projectId,
    staleTime: 1000 * 60 * 2, // Cache for 2 minutes
  });
}

/**
 * Cancel job mutation
 */
export function useCancelJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => processingApi.cancelJob(jobId),
    onSuccess: (_, jobId) => {
      // Invalidate job status to refetch
      queryClient.invalidateQueries({ queryKey: processingKeys.job(jobId) });
    },
  });
}
