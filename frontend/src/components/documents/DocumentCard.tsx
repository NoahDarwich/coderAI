/**
 * DocumentCard Component
 * Displays a single document with actions
 */

'use client';

import { Document } from '@/lib/types/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  FileText,
  FileType,
  File as FileIcon,
  MoreVertical,
  Trash2,
  Eye,
  Download,
} from 'lucide-react';
import { formatFileSize, formatDate } from '@/lib/utils/formatting';
import { cn } from '@/lib/utils';

interface DocumentCardProps {
  document: Document;
  onDelete?: (id: string) => void;
  onPreview?: (document: Document) => void;
  className?: string;
}

export function DocumentCard({
  document,
  onDelete,
  onPreview,
  className,
}: DocumentCardProps) {
  const getFileIcon = (fileType: Document['fileType']) => {
    switch (fileType) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-red-600" />;
      case 'docx':
        return <FileType className="h-5 w-5 text-blue-600" />;
      case 'txt':
        return <FileIcon className="h-5 w-5 text-gray-600" />;
      default:
        return <FileIcon className="h-5 w-5 text-gray-600" />;
    }
  };

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
    <Card className={cn('p-4', className)}>
      <div className="flex items-start gap-3">
        {/* File icon */}
        <div className="flex-shrink-0 mt-1">
          {getFileIcon(document.fileType)}
        </div>

        {/* File info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h3 className="text-sm font-medium truncate">{document.filename}</h3>
            {getStatusBadge(document.status)}
          </div>

          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span>{formatFileSize(document.fileSize)}</span>
            <span>{document.fileType.toUpperCase()}</span>
            <span>{formatDate(document.uploadedAt)}</span>
          </div>

          {/* Error message */}
          {document.status === 'error' && document.errorMessage && (
            <p className="text-xs text-destructive mt-2">
              {document.errorMessage}
            </p>
          )}
        </div>

        {/* Actions menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="flex-shrink-0">
              <MoreVertical className="h-4 w-4" />
              <span className="sr-only">Document actions</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {onPreview && (
              <DropdownMenuItem onClick={() => onPreview(document)}>
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </DropdownMenuItem>
            )}
            <DropdownMenuItem disabled>
              <Download className="h-4 w-4 mr-2" />
              Download
            </DropdownMenuItem>
            {onDelete && (
              <DropdownMenuItem
                onClick={() => onDelete(document.id)}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </Card>
  );
}
