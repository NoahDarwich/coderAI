/**
 * UploadProgress Component
 * Shows upload progress for individual files
 */

'use client';

import { UploadFile } from '@/lib/types/document';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { CheckCircle2, XCircle, Loader2, X, FileText } from 'lucide-react';
import { formatFileSize } from '@/lib/utils/formatting';
import { cn } from '@/lib/utils';

interface UploadProgressProps {
  uploadFile: UploadFile;
  onRemove: (id: string) => void;
}

export function UploadProgress({ uploadFile, onRemove }: UploadProgressProps) {
  const { file, status, progress, errorMessage } = uploadFile;

  const getStatusIcon = () => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-destructive" />;
      default:
        return <FileText className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'uploading':
        return `Uploading... ${progress}%`;
      case 'success':
        return 'Upload complete';
      case 'error':
        return errorMessage || 'Upload failed';
      default:
        return 'Pending';
    }
  };

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg border',
        status === 'error' && 'border-destructive bg-destructive/5',
        status === 'success' && 'border-green-600 bg-green-50 dark:bg-green-950',
        (status === 'pending' || status === 'uploading') && 'border-border'
      )}
    >
      {/* Icon */}
      <div className="flex-shrink-0">{getStatusIcon()}</div>

      {/* File info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <p className="text-sm font-medium truncate">{file.name}</p>
          <span className="text-xs text-muted-foreground flex-shrink-0">
            {formatFileSize(file.size)}
          </span>
        </div>

        {/* Status text */}
        <p
          className={cn(
            'text-xs',
            status === 'error' && 'text-destructive',
            status === 'success' && 'text-green-600',
            (status === 'pending' || status === 'uploading') &&
              'text-muted-foreground'
          )}
        >
          {getStatusText()}
        </p>

        {/* Progress bar */}
        {status === 'uploading' && (
          <Progress value={progress} className="h-1 mt-2" />
        )}
      </div>

      {/* Remove button */}
      <Button
        variant="ghost"
        size="icon"
        className="flex-shrink-0"
        onClick={() => onRemove(uploadFile.id)}
        disabled={status === 'uploading'}
      >
        <X className="h-4 w-4" />
        <span className="sr-only">Remove file</span>
      </Button>
    </div>
  );
}
