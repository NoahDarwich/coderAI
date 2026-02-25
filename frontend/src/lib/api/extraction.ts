/**
 * Extraction API Client
 * TanStack Query hooks for extraction results operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ExtractionResult } from '@/lib/types/api';
import { mockExtractionResults } from '@/mocks/results';
import { apiClient } from './client';
import { BackendProjectResults, transformDocumentResult } from './transforms';

/**
 * Query Keys
 */
export const extractionKeys = {
  all: ['extractions'] as const,
  lists: () => [...extractionKeys.all, 'list'] as const,
  list: (projectId: string) => [...extractionKeys.lists(), projectId] as const,
  details: () => [...extractionKeys.all, 'detail'] as const,
  detail: (id: string) => [...extractionKeys.details(), id] as const,
};

// Mock API functions
const mockExtractionApi = {
  getResults: async (_projectId: string): Promise<ExtractionResult[]> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return mockExtractionResults.filter(
      (result) => result.schemaId === 'schema-001'
    );
  },

  flagResult: async (resultId: string, flagged: boolean): Promise<{ resultId: string; flagged: boolean }> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const result = mockExtractionResults.find((r) => r.id === resultId);
    if (result) {
      result.flagged = flagged;
    }
    return { resultId, flagged };
  },

  bulkFlag: async (resultIds: string[], flagged: boolean): Promise<{ resultIds: string[]; flagged: boolean }> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    resultIds.forEach((id) => {
      const result = mockExtractionResults.find((r) => r.id === id);
      if (result) {
        result.flagged = flagged;
      }
    });
    return { resultIds, flagged };
  },
};

// Real API functions
const realExtractionApi = {
  getResults: async (projectId: string): Promise<ExtractionResult[]> => {
    const response = await apiClient.get<BackendProjectResults>(
      `/api/v1/projects/${projectId}/results`
    );
    return response.documents.map(transformDocumentResult);
  },

  flagResult: async (extractionId: string, flagged: boolean): Promise<{ resultId: string; flagged: boolean }> => {
    await apiClient.put(`/api/v1/extractions/${extractionId}/flag`, { flagged });
    return { resultId: extractionId, flagged };
  },

  bulkFlag: async (resultIds: string[], flagged: boolean): Promise<{ resultIds: string[]; flagged: boolean }> => {
    // Flag each individually (backend may not have bulk endpoint)
    await Promise.all(
      resultIds.map(id => apiClient.put(`/api/v1/extractions/${id}/flag`, { flagged }))
    );
    return { resultIds, flagged };
  },
};

// Select API based on environment
const extractionApi = apiClient.useMockData ? mockExtractionApi : realExtractionApi;

/**
 * Fetch extraction results for a project
 */
export function useExtractionResults(projectId: string) {
  return useQuery({
    queryKey: extractionKeys.list(projectId),
    queryFn: () => extractionApi.getResults(projectId),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Flag/unflag extraction result mutation
 */
export function useFlagResult(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      resultId,
      flagged,
    }: {
      resultId: string;
      flagged: boolean;
    }) => extractionApi.flagResult(resultId, flagged),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: extractionKeys.list(projectId) });
    },
  });
}

/**
 * Bulk flag/unflag mutation
 */
export function useBulkFlagResults(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      resultIds,
      flagged,
    }: {
      resultIds: string[];
      flagged: boolean;
    }) => extractionApi.bulkFlag(resultIds, flagged),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: extractionKeys.list(projectId) });
    },
  });
}

/**
 * Post feedback on a single extraction (✓ / ✗)
 */
export function usePostFeedback() {
  return useMutation({
    mutationFn: ({
      extractionId,
      feedbackType,
      correctedValue,
    }: {
      extractionId: string;
      feedbackType: 'CORRECT' | 'INCORRECT';
      correctedValue?: unknown;
    }) =>
      apiClient.post(`/api/v1/extractions/${extractionId}/feedback`, {
        feedback_type: feedbackType,
        corrected_value: correctedValue ?? null,
        user_comment: null,
      }),
  });
}

/**
 * Pin a golden (few-shot) example to a variable
 */
export function useAddGoldenExample() {
  return useMutation({
    mutationFn: ({
      variableId,
      sourceText,
      value,
      documentName,
      useInPrompt,
    }: {
      variableId: string;
      sourceText: string;
      value: unknown;
      documentName: string;
      useInPrompt: boolean;
    }) =>
      apiClient.post(`/api/v1/variables/${variableId}/examples`, {
        source_text: sourceText,
        value,
        document_name: documentName,
        use_in_prompt: useInPrompt,
      }),
  });
}
