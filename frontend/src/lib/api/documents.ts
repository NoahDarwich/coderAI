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

// Backend document types
interface BackendDocument {
  id: string;
  project_id: string;
  name: string;
  content_type: 'PDF' | 'DOCX' | 'TXT';
  size_bytes: number;
  uploaded_at: string;
  content_preview?: string;
}

// Transform backend document to frontend format
function transformBackendDocument(backendDoc: BackendDocument): Document {
  return {
    id: backendDoc.id,
    projectId: backendDoc.project_id,
    filename: backendDoc.name,
    fileType: backendDoc.content_type.toLowerCase() as 'pdf' | 'docx' | 'txt',
    fileSize: backendDoc.size_bytes,
    uploadedAt: backendDoc.uploaded_at,
    status: 'uploaded',
  };
}

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
    return documents.map(transformBackendDocument);
  },

  upload: async (projectId: string, file: File): Promise<Document> => {
    const document = await apiClient.upload<BackendDocument>(
      `/api/v1/projects/${projectId}/documents`,
      file
    );
    return transformBackendDocument(document);
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
