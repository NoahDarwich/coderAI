/**
 * useDocuments Hook
 * Custom hook for document management with file upload state
 */

import { useState, useCallback } from 'react';
import { UploadFile } from '@/lib/types/document';
import { validateFile } from '@/lib/utils/validation';
import { useUploadDocument, useDeleteDocument } from '@/lib/api/documents';
import { toast } from 'sonner';

export function useDocumentUpload(projectId: string) {
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);
  const uploadMutation = useUploadDocument(projectId);
  const deleteMutation = useDeleteDocument(projectId);

  /**
   * Add files to upload queue
   */
  const addFiles = useCallback((files: File[]) => {
    const newUploadFiles: UploadFile[] = files.map((file) => ({
      file,
      id: `upload-${Date.now()}-${Math.random()}`,
      progress: 0,
      status: 'pending',
    }));

    setUploadFiles((prev) => [...prev, ...newUploadFiles]);
    return newUploadFiles;
  }, []);

  /**
   * Remove file from upload queue
   */
  const removeFile = useCallback((id: string) => {
    setUploadFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  /**
   * Upload a single file
   */
  const uploadFile = useCallback(
    async (uploadFile: UploadFile) => {
      // Validate file
      const validation = validateFile(uploadFile.file);
      if (!validation.valid) {
        setUploadFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id
              ? {
                  ...f,
                  status: 'error',
                  errorMessage: validation.error,
                }
              : f
          )
        );
        toast.error(validation.error || 'File validation failed');
        return;
      }

      // Update status to uploading
      setUploadFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id ? { ...f, status: 'uploading', progress: 0 } : f
        )
      );

      try {
        // Simulate progress (TODO(Phase 2): Replace with real upload progress)
        const progressInterval = setInterval(() => {
          setUploadFiles((prev) =>
            prev.map((f) =>
              f.id === uploadFile.id && f.progress < 90
                ? { ...f, progress: f.progress + 10 }
                : f
            )
          );
        }, 100);

        // Upload file
        await uploadMutation.mutateAsync(uploadFile.file);

        // Clear interval and set to 100%
        clearInterval(progressInterval);

        setUploadFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id
              ? { ...f, status: 'success', progress: 100 }
              : f
          )
        );

        toast.success(`${uploadFile.file.name} uploaded successfully`);

        // Remove from queue after 2 seconds
        setTimeout(() => {
          removeFile(uploadFile.id);
        }, 2000);
      } catch (error) {
        setUploadFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id
              ? {
                  ...f,
                  status: 'error',
                  errorMessage: 'Upload failed',
                }
              : f
          )
        );
        toast.error(`Failed to upload ${uploadFile.file.name}`);
      }
    },
    [uploadMutation, removeFile]
  );

  /**
   * Upload all pending files
   */
  const uploadAll = useCallback(async () => {
    const pendingFiles = uploadFiles.filter((f) => f.status === 'pending');

    for (const file of pendingFiles) {
      await uploadFile(file);
    }
  }, [uploadFiles, uploadFile]);

  /**
   * Delete a document
   */
  const deleteDocument = useCallback(
    async (documentId: string, documentName: string) => {
      try {
        await deleteMutation.mutateAsync(documentId);
        toast.success(`${documentName} deleted successfully`);
      } catch (error) {
        toast.error(`Failed to delete ${documentName}`);
      }
    },
    [deleteMutation]
  );

  return {
    uploadFiles,
    addFiles,
    removeFile,
    uploadFile,
    uploadAll,
    deleteDocument,
    isUploading: uploadFiles.some((f) => f.status === 'uploading'),
  };
}
