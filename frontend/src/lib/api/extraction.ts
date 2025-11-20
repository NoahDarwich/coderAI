/**
 * Extraction API Client
 * TanStack Query hooks for extraction results operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ExtractionResult } from '@/lib/types/api';
import { mockExtractionResults } from '@/mocks/results';

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

/**
 * Fetch extraction results for a project
 */
export function useExtractionResults(projectId: string) {
  return useQuery({
    queryKey: extractionKeys.list(projectId),
    queryFn: async () => {
      // TODO(Phase 2): Replace with real API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Filter results by project (via schema)
      return mockExtractionResults.filter(
        (result) => result.schemaId === 'schema-001'
      );
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Flag/unflag extraction result mutation
 */
export function useFlagResult(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      resultId,
      flagged,
    }: {
      resultId: string;
      flagged: boolean;
    }) => {
      // TODO(Phase 2): Replace with real API call
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Update mock data
      const result = mockExtractionResults.find((r) => r.id === resultId);
      if (result) {
        result.flagged = flagged;
      }

      return { resultId, flagged };
    },
    onSuccess: () => {
      // Invalidate and refetch
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
    mutationFn: async ({
      resultIds,
      flagged,
    }: {
      resultIds: string[];
      flagged: boolean;
    }) => {
      // TODO(Phase 2): Replace with real API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Update mock data
      resultIds.forEach((id) => {
        const result = mockExtractionResults.find((r) => r.id === id);
        if (result) {
          result.flagged = flagged;
        }
      });

      return { resultIds, flagged };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: extractionKeys.list(projectId) });
    },
  });
}
