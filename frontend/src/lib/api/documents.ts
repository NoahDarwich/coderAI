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
import { apiClient } from './client';
import { BackendDocument, transformDocument } from './transforms';

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

// Mock API functions
const mockDocumentApi = {
  list: async (projectId: string): Promise<Document[]> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return getMockDocumentsByProjectId(projectId);
  },

  upload: async (projectId: string, file: File): Promise<Document> => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return uploadMockDocument(projectId, {
      name: file.name,
      size: file.size,
      type: file.type,
    });
  },

  delete: async (documentId: string): Promise<void> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    deleteMockDocument(documentId);
  },
};

// Real API functions
const realDocumentApi = {
  list: async (projectId: string): Promise<Document[]> => {
    const documents = await apiClient.get<BackendDocument[]>(
      `/api/v1/projects/${projectId}/documents`
    );
    return documents.map(transformDocument);
  },

  upload: async (projectId: string, file: File): Promise<Document> => {
    const document = await apiClient.upload<BackendDocument>(
      `/api/v1/projects/${projectId}/documents`,
      file
    );
    return transformDocument(document);
  },

  delete: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/documents/${documentId}`);
  },
};

// Select API based on environment
const documentApi = apiClient.useMockData ? mockDocumentApi : realDocumentApi;

/**
 * Fetch documents for a project
 */
export function useDocuments(projectId: string) {
  return useQuery({
    queryKey: documentKeys.list(projectId),
    queryFn: () => documentApi.list(projectId),
    staleTime: 1000 * 60 * 5, // 5 minutes
    enabled: !!projectId,
  });
}

/**
 * Upload document mutation
 */
export function useUploadDocument(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => documentApi.upload(projectId, file),
    onSuccess: (newDocument) => {
      // Update the documents list cache
      queryClient.setQueryData<Document[]>(
        documentKeys.list(projectId),
        (oldDocuments = []) => [...oldDocuments, newDocument]
      );

      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: documentKeys.list(projectId) });

      // Also invalidate project details to update document count
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] });
    },
  });
}

/**
 * Delete document mutation
 */
export function useDeleteDocument(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) => documentApi.delete(documentId),
    onSuccess: (_, documentId) => {
      // Remove from cache
      queryClient.setQueryData<Document[]>(
        documentKeys.list(projectId),
        (oldDocuments = []) => oldDocuments.filter((doc) => doc.id !== documentId)
      );

      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: documentKeys.list(projectId) });

      // Also invalidate project details to update document count
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] });
    },
  });
}
