'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
};

interface FileWithPreview extends File {
  preview?: string;
}

interface DocumentUploaderProps {
  onUpload: (files: File[]) => Promise<void>;
  isUploading?: boolean;
  maxFiles?: number;
}

export function DocumentUploader({
  onUpload,
  isUploading = false,
  maxFiles,
}: DocumentUploaderProps) {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);

    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const errors = rejectedFiles.map((file) => {
        const errorMessages = file.errors.map((e: any) => {
          if (e.code === 'file-too-large') {
            return `${file.file.name}: File is too large (max 10MB)`;
          }
          if (e.code === 'file-invalid-type') {
            return `${file.file.name}: Invalid file type (only PDF, DOCX, TXT)`;
          }
          return `${file.file.name}: ${e.message}`;
        });
        return errorMessages.join(', ');
      });
      setError(errors.join('\n'));
      return;
    }

    // Handle accepted files
    if (acceptedFiles.length > 0) {
      const newFiles = acceptedFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
        })
      );
      setFiles((prev) => [...prev, ...newFiles]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    maxFiles: maxFiles,
    disabled: isUploading,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => {
      const newFiles = [...prev];
      const removed = newFiles.splice(index, 1)[0];
      if (removed.preview) {
        URL.revokeObjectURL(removed.preview);
      }
      return newFiles;
    });
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    try {
      setError(null);
      await onUpload(files);
      // Clear files after successful upload
      files.forEach((file) => {
        if (file.preview) {
          URL.revokeObjectURL(file.preview);
        }
      });
      setFiles([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload files');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <Card
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed transition-colors cursor-pointer',
          isDragActive && 'border-blue-500 bg-blue-50',
          !isDragActive && 'border-gray-300 hover:border-gray-400',
          isUploading && 'opacity-50 cursor-not-allowed'
        )}
        role="button"
        aria-label="Document upload area. Drag and drop files or click to browse."
        tabIndex={isUploading ? -1 : 0}
      >
        <CardContent className="flex flex-col items-center justify-center py-12">
          <input
            {...getInputProps()}
            aria-label="Upload documents"
            aria-describedby="upload-instructions"
          />
          <Upload
            className={cn(
              'w-12 h-12 mb-4',
              isDragActive ? 'text-blue-500' : 'text-gray-400'
            )}
          />
          <p className="text-lg font-medium text-gray-900 mb-1">
            {isDragActive ? 'Drop files here' : 'Drag and drop files here'}
          </p>
          <p className="text-sm text-gray-500 mb-4">
            or click to browse your computer
          </p>
          <div id="upload-instructions">
            <p className="text-xs text-gray-400">
              Supported formats: PDF, DOCX, TXT (max 10MB per file)
            </p>
            {maxFiles && (
              <p className="text-xs text-gray-400 mt-1">
                Maximum {maxFiles} files
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" role="alert" aria-live="assertive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="whitespace-pre-line">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2" role="region" aria-label="Selected files list">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900" id="selected-files-heading">
              Selected Files ({files.length})
            </h3>
            <Button
              onClick={handleUpload}
              disabled={isUploading || files.length === 0}
              size="sm"
              aria-label={`Upload ${files.length} selected file${files.length > 1 ? 's' : ''}`}
            >
              {isUploading ? 'Uploading...' : `Upload ${files.length} file${files.length > 1 ? 's' : ''}`}
            </Button>
          </div>

          <div className="space-y-2" role="list" aria-labelledby="selected-files-heading">
            {files.map((file, index) => (
              <Card key={index} role="listitem">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <FileText className="w-8 h-8 text-blue-500 flex-shrink-0" aria-hidden="true" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.name}
                      </p>
                      <p className="text-xs text-gray-500" aria-label={`File size: ${formatFileSize(file.size)}`}>
                        {formatFileSize(file.size)}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                    disabled={isUploading}
                    aria-label={`Remove ${file.name}`}
                  >
                    <X className="w-4 h-4" aria-hidden="true" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
