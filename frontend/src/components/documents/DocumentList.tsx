/**
 * DocumentList Component
 * List of uploaded documents with actions
 */

'use client';

import { useState } from 'react';
import { Document } from '@/lib/types/api';
import { DocumentCard } from './DocumentCard';
import { DocumentPreview } from './DocumentPreview';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, FileX } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DocumentListProps {
  documents: Document[];
  onDelete?: (id: string) => void;
  isLoading?: boolean;
  className?: string;
}

export function DocumentList({
  documents,
  onDelete,
  isLoading,
  className,
}: DocumentListProps) {
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  // Filter documents
  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      searchQuery === '' ||
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === 'all' || doc.status === statusFilter;

    const matchesType = typeFilter === 'all' || doc.fileType === typeFilter;

    return matchesSearch && matchesStatus && matchesType;
  });

  if (isLoading) {
    return (
      <div className={cn('space-y-4', className)}>
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-24 rounded-lg bg-muted animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Filters */}
      {documents.length > 0 && (
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Status filter */}
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full sm:w-[150px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="uploaded">Uploaded</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>

          {/* Type filter */}
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-full sm:w-[150px]">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="pdf">PDF</SelectItem>
              <SelectItem value="docx">DOCX</SelectItem>
              <SelectItem value="txt">TXT</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Document list */}
      {filteredDocuments.length > 0 ? (
        <div className="space-y-2">
          {filteredDocuments.map((document) => (
            <DocumentCard
              key={document.id}
              document={document}
              onDelete={onDelete}
              onPreview={setPreviewDocument}
            />
          ))}
        </div>
      ) : documents.length > 0 ? (
        // No results from filters
        <div className="text-center py-12">
          <FileX className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No documents found</h3>
          <p className="text-sm text-muted-foreground">
            Try adjusting your filters or search query
          </p>
          <Button
            variant="outline"
            onClick={() => {
              setSearchQuery('');
              setStatusFilter('all');
              setTypeFilter('all');
            }}
            className="mt-4"
          >
            Clear Filters
          </Button>
        </div>
      ) : (
        // No documents at all
        <div className="text-center py-12 border-2 border-dashed rounded-lg">
          <FileX className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No documents uploaded</h3>
          <p className="text-sm text-muted-foreground">
            Upload your first document to get started
          </p>
        </div>
      )}

      {/* Preview modal */}
      <DocumentPreview
        document={previewDocument}
        open={previewDocument !== null}
        onClose={() => setPreviewDocument(null)}
      />
    </div>
  );
}
