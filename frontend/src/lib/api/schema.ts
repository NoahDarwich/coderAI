/**
 * Schema API Client
 * TanStack Query hooks for schema operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { SchemaConfig, ChatMessage, SchemaVariable } from '@/lib/types/api';
import {
  getMockSchemaByProjectId,
  saveMockSchema,
} from '@/mocks/schema';

/**
 * Query Keys
 */
export const schemaKeys = {
  all: ['schemas'] as const,
  lists: () => [...schemaKeys.all, 'list'] as const,
  list: (projectId: string) => [...schemaKeys.lists(), projectId] as const,
  details: () => [...schemaKeys.all, 'detail'] as const,
  detail: (id: string) => [...schemaKeys.details(), id] as const,
};

/**
 * Fetch schema for a project
 */
export function useSchema(projectId: string) {
  return useQuery({
    queryKey: schemaKeys.list(projectId),
    queryFn: async () => {
      // TODO(Phase 2): Replace with real API call
      await new Promise((resolve) => setTimeout(resolve, 300));
      return getMockSchemaByProjectId(projectId);
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Save schema mutation
 */
export function useSaveSchema(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      conversationHistory: ChatMessage[];
      variables: SchemaVariable[];
      prompts: Record<string, string>;
    }) => {
      // TODO(Phase 2): Replace with real API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      return saveMockSchema(projectId, data);
    },
    onSuccess: (savedSchema) => {
      // Update cache
      queryClient.setQueryData(
        schemaKeys.list(projectId),
        savedSchema
      );

      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: schemaKeys.list(projectId) });
    },
  });
}

/**
 * Approve schema mutation
 */
export function useApproveSchema(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      // TODO(Phase 2): Replace with real API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      const schema = getMockSchemaByProjectId(projectId);
      if (!schema) {
        throw new Error('Schema not found');
      }

      // Mark schema as approved in backend
      return saveMockSchema(projectId, {
        ...schema,
        approved: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: schemaKeys.list(projectId) });
    },
  });
}
