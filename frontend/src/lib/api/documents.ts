/**
 * Documents API Client
 * TanStack Query hooks for document operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Document } from '@/lib/types/api';
import {
  getMockDocumentsByProjectId,
  uploadMockDocument,
  deleteMockDocument,
} from '@/mocks/documents';

/**
 * Query Keys
 */
export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (projectId: string) => [...documentKeys.lists(), projectId] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};

/**
 * Fetch documents for a project
 */
export function useDocuments(projectId: string) {
  return useQuery({
    queryKey: documentKeys.list(projectId),
    queryFn: async () => {
      // TODO(Phase 2): Replace with real API call
      await new Promise((resolve) => setTimeout(resolve, 300));
      return getMockDocumentsByProjectId(projectId);
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Upload document mutation
 */
export function useUploadDocument(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      // TODO(Phase 2): Replace with real API call
      // Simulate upload delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      return uploadMockDocument(projectId, {
        name: file.name,
        size: file.size,
        type: file.type,
      });
    },
    onSuccess: (newDocument) => {
      // Update the documents list cache
      queryClient.setQueryData<Document[]>(
        documentKeys.list(projectId),
        (oldDocuments = []) => [...oldDocuments, newDocument]
      );

      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: documentKeys.list(projectId) });
    },
  });
}

/**
 * Delete document mutation
 */
export function useDeleteDocument(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (documentId: string) => {
      // TODO(Phase 2): Replace with real API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      const success = deleteMockDocument(documentId);
      if (!success) {
        throw new Error('Failed to delete document');
      }
      return documentId;
    },
    onSuccess: (deletedId) => {
      // Remove from cache
      queryClient.setQueryData<Document[]>(
        documentKeys.list(projectId),
        (oldDocuments = []) =>
          oldDocuments.filter((doc) => doc.id !== deletedId)
      );

      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: documentKeys.list(projectId) });
    },
  });
}
