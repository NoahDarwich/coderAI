/**
 * Processing API Client
 * TanStack Query hooks for job processing operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import {
  BackendProcessingJob,
  BackendJobResults,
  BackendProjectResults,
  BackendProcessingLog,
  transformJob,
} from './transforms';

/**
 * Frontend Types (for UI compatibility)
 */
export interface ProcessingJob {
  id: string;
  projectId: string;
  type: 'sample' | 'full';
  status: 'pending' | 'processing' | 'paused' | 'completed' | 'failed' | 'cancelled';
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
 * Transform backend job with logs to ProcessingJob with logs
 */
function transformBackendJobWithLogs(
  backendJob: BackendProcessingJob,
  logs: BackendProcessingLog[] = []
): ProcessingJob {
  const base = transformJob(backendJob);

  const logLevelMap: Record<BackendProcessingLog['log_level'], ProcessingLog['level']> = {
    'INFO': 'info',
    'WARNING': 'warning',
    'ERROR': 'error',
  };

  return {
    ...base,
    startedAt: base.startedAt || new Date().toISOString(),
    documentIds: backendJob.document_ids || [],
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

  cancelJob: async (_jobId: string): Promise<void> => {
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

    return transformBackendJobWithLogs(response);
  },

  getJobStatus: async (jobId: string): Promise<ProcessingJob> => {
    const response = await apiClient.get<BackendProcessingJob>(
      `/api/v1/jobs/${jobId}`
    );

    let logs: BackendProcessingLog[] = [];
    try {
      logs = (response as any).logs || [];
    } catch {
      // Logs endpoint might not exist
    }

    return transformBackendJobWithLogs(response, logs);
  },

  getJobResults: async (jobId: string): Promise<BackendJobResults> => {
    return apiClient.get<BackendJobResults>(`/api/v1/jobs/${jobId}/results`);
  },

  getProjectResults: async (projectId: string): Promise<BackendProjectResults> => {
    return apiClient.get<BackendProjectResults>(`/api/v1/projects/${projectId}/results`);
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
      queryClient.setQueryData(processingKeys.job(job.id), job);
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
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;

      if (data.status === 'completed' ||
          data.status === 'failed' ||
          data.status === 'cancelled') {
        return false;
      }

      return 2000;
    },
    refetchIntervalInBackground: true,
    staleTime: 1000,
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
    staleTime: 1000 * 60 * 5,
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
        return {
          project_id: projectId,
          total_documents: 0,
          documents: [],
        };
      }
      return realProcessingApi.getProjectResults(projectId);
    },
    enabled: enabled && !!projectId,
    staleTime: 1000 * 60 * 2,
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
      queryClient.invalidateQueries({ queryKey: processingKeys.job(jobId) });
    },
  });
}

// Re-export backend types for consumers
export type { BackendJobResults, BackendProjectResults, BackendProcessingLog } from './transforms';
