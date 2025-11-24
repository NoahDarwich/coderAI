'use client';

import { useState } from 'react';
import { FileText, Trash2, Download, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Document } from '@/types';
import { formatFileSize, formatRelativeTime, cn } from '@/lib/utils';

interface DocumentListProps {
  documents: Document[];
  onDelete?: (documentId: string) => Promise<void>;
  onView?: (document: Document) => void;
  isLoading?: boolean;
}

const STATUS_COLORS = {
  uploading: 'bg-blue-100 text-blue-800 border-blue-200',
  uploaded: 'bg-green-100 text-green-800 border-green-200',
  processing: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  processed: 'bg-green-100 text-green-800 border-green-200',
  error: 'bg-red-100 text-red-800 border-red-200',
};

const STATUS_LABELS = {
  uploading: 'Uploading',
  uploaded: 'Uploaded',
  processing: 'Processing',
  processed: 'Processed',
  error: 'Error',
};

const FILE_TYPE_COLORS = {
  pdf: 'bg-red-100 text-red-800',
  docx: 'bg-blue-100 text-blue-800',
  txt: 'bg-gray-100 text-gray-800',
};

export function DocumentList({
  documents,
  onDelete,
  onView,
  isLoading = false,
}: DocumentListProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<Document | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (document: Document) => {
    setDocumentToDelete(document);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!documentToDelete || !onDelete) return;

    setIsDeleting(true);
    try {
      await onDelete(documentToDelete.id);
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    } catch (error) {
      console.error('Failed to delete document:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-200 rounded" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4" />
                  <div className="h-3 bg-gray-200 rounded w-1/2" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mb-3" />
          <p className="text-gray-600 text-center">
            No documents uploaded yet
          </p>
          <p className="text-sm text-gray-500 text-center mt-1">
            Upload documents to get started with data extraction
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <div className="space-y-2">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-900">
            Documents ({documents.length})
          </h3>
        </div>

        {documents.map((document) => (
          <Card
            key={document.id}
            className={cn(
              'transition-shadow hover:shadow-md',
              document.status === 'error' && 'border-red-200'
            )}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                {/* File Icon and Info */}
                <div className="flex items-start space-x-3 flex-1 min-w-0">
                  <FileText className="w-8 h-8 text-blue-500 flex-shrink-0 mt-1" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {document.fileName}
                      </p>
                      <Badge
                        variant="outline"
                        className={cn('text-xs', FILE_TYPE_COLORS[document.fileType])}
                      >
                        {document.fileType.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span>{formatFileSize(document.fileSize)}</span>
                      <span>•</span>
                      <span>Uploaded {formatRelativeTime(document.uploadedAt)}</span>
                    </div>
                    {document.contentPreview && (
                      <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                        {document.contentPreview}
                      </p>
                    )}
                  </div>
                </div>

                {/* Status and Actions */}
                <div className="flex items-start gap-2">
                  <Badge
                    variant="outline"
                    className={cn('text-xs', STATUS_COLORS[document.status])}
                  >
                    {STATUS_LABELS[document.status]}
                  </Badge>

                  <div className="flex gap-1">
                    {onView && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onView(document)}
                        aria-label={`View ${document.fileName}`}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                    )}
                    {onDelete && document.status !== 'processing' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteClick(document)}
                        aria-label={`Delete ${document.fileName}`}
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Document</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{documentToDelete?.fileName}"?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
