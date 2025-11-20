/**
 * DocumentPreview Component
 * Modal to preview document details
 */

'use client';

import { Document } from '@/lib/types/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FileText, Download, X } from 'lucide-react';
import { formatFileSize, formatDate } from '@/lib/utils/formatting';

interface DocumentPreviewProps {
  document: Document | null;
  open: boolean;
  onClose: () => void;
}

export function DocumentPreview({
  document,
  open,
  onClose,
}: DocumentPreviewProps) {
  if (!document) return null;

  const getStatusBadge = (status: Document['status']) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default">Completed</Badge>;
      case 'processing':
        return <Badge variant="secondary">Processing</Badge>;
      case 'uploaded':
        return <Badge variant="outline">Uploaded</Badge>;
      case 'pending':
        return <Badge variant="outline">Pending</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            {document.filename}
          </DialogTitle>
          <DialogDescription>Document details and preview</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Status */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Status:</span>
            {getStatusBadge(document.status)}
          </div>

          {/* Error message */}
          {document.status === 'error' && document.errorMessage && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive">
              <p className="text-sm text-destructive">{document.errorMessage}</p>
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4 p-4 rounded-lg bg-muted">
            <div>
              <p className="text-xs text-muted-foreground mb-1">File Type</p>
              <p className="text-sm font-medium">
                {document.fileType.toUpperCase()}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">File Size</p>
              <p className="text-sm font-medium">
                {formatFileSize(document.fileSize)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Uploaded</p>
              <p className="text-sm font-medium">
                {formatDate(document.uploadedAt)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Document ID</p>
              <p className="text-sm font-medium font-mono text-xs">
                {document.id}
              </p>
            </div>
          </div>

          {/* Preview placeholder */}
          <div className="border rounded-lg p-8 text-center bg-muted/30">
            <FileText className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <p className="text-sm text-muted-foreground">
              Document preview not available in Phase 1
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Preview functionality will be added in Phase 2
            </p>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" disabled>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button onClick={onClose}>
              <X className="h-4 w-4 mr-2" />
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
