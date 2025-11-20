/**
 * DocumentUploader Component
 * Drag and drop file uploader with validation
 */

'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Upload, FileText } from 'lucide-react';
import { UploadProgress } from './UploadProgress';
import { UploadFile } from '@/lib/types/document';
import { validateFiles } from '@/lib/utils/validation';
import { SUPPORTED_FILE_TYPES } from '@/lib/types/document';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface DocumentUploaderProps {
  uploadFiles: UploadFile[];
  onFilesAdded: (files: File[]) => void;
  onFileRemove: (id: string) => void;
  onUploadAll: () => void;
  isUploading: boolean;
  className?: string;
}

export function DocumentUploader({
  uploadFiles,
  onFilesAdded,
  onFileRemove,
  onUploadAll,
  isUploading,
  className,
}: DocumentUploaderProps) {
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Validate files
      const validation = validateFiles(acceptedFiles);

      if (!validation.valid) {
        toast.error(validation.error || 'File validation failed');
        return;
      }

      onFilesAdded(acceptedFiles);
      setDragActive(false);
    },
    [onFilesAdded]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: SUPPORTED_FILE_TYPES,
    multiple: true,
    disabled: isUploading,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  });

  const hasPendingFiles = uploadFiles.some((f) => f.status === 'pending');

  return (
    <div className={cn('space-y-4', className)}>
      {/* Drop zone */}
      <Card
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed cursor-pointer transition-colors',
          'hover:border-primary hover:bg-accent/50',
          isDragActive && 'border-primary bg-accent',
          isUploading && 'cursor-not-allowed opacity-50'
        )}
      >
        <div className="p-8 text-center">
          <input {...getInputProps()} />

          <div className="flex flex-col items-center gap-4">
            <div className="p-4 rounded-full bg-primary/10">
              <Upload className="h-8 w-8 text-primary" />
            </div>

            <div>
              <p className="text-lg font-medium mb-1">
                {isDragActive ? (
                  'Drop files here'
                ) : (
                  <>
                    Drag and drop files here, or{' '}
                    <span className="text-primary">browse</span>
                  </>
                )}
              </p>
              <p className="text-sm text-muted-foreground">
                Supported formats: PDF, DOCX, TXT (Max 10MB per file)
              </p>
            </div>

            {!isUploading && (
              <Button type="button" variant="outline" size="sm">
                <FileText className="h-4 w-4 mr-2" />
                Choose Files
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Upload queue */}
      {uploadFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">
              Upload Queue ({uploadFiles.length})
            </h3>
            {hasPendingFiles && (
              <Button
                onClick={onUploadAll}
                disabled={isUploading}
                size="sm"
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload All
              </Button>
            )}
          </div>

          <div className="space-y-2">
            {uploadFiles.map((uploadFile) => (
              <UploadProgress
                key={uploadFile.id}
                uploadFile={uploadFile}
                onRemove={onFileRemove}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
