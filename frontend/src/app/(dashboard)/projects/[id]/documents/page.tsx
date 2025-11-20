/**
 * Documents Page
 * Upload and manage project documents
 */

'use client';

import { useParams, useRouter } from 'next/navigation';
import { useDocuments } from '@/lib/api/documents';
import { useDocumentUpload } from '@/lib/hooks/useDocuments';
import { DocumentUploader } from '@/components/documents/DocumentUploader';
import { DocumentList } from '@/components/documents/DocumentList';
import { Button } from '@/components/ui/button';
import { ArrowRight, FileText } from 'lucide-react';

export default function DocumentsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  // Fetch documents
  const { data: documents = [], isLoading } = useDocuments(projectId);

  // Upload management
  const {
    uploadFiles,
    addFiles,
    removeFile,
    uploadAll,
    deleteDocument,
    isUploading,
  } = useDocumentUpload(projectId);

  const hasDocuments = documents.length > 0;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FileText className="h-6 w-6" />
            Documents
          </h2>
          <p className="text-muted-foreground mt-1">
            Upload and manage documents for extraction
          </p>
        </div>

        {hasDocuments && (
          <Button
            onClick={() => router.push(`/projects/${projectId}/schema`)}
          >
            Next: Define Schema
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Upload section */}
      <div>
        <h3 className="text-lg font-medium mb-3">Upload Documents</h3>
        <DocumentUploader
          uploadFiles={uploadFiles}
          onFilesAdded={addFiles}
          onFileRemove={removeFile}
          onUploadAll={uploadAll}
          isUploading={isUploading}
        />
      </div>

      {/* Documents list */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-medium">
            Uploaded Documents
            {!isLoading && documents.length > 0 && (
              <span className="ml-2 text-sm font-normal text-muted-foreground">
                ({documents.length})
              </span>
            )}
          </h3>
        </div>

        <DocumentList
          documents={documents}
          onDelete={(id) => {
            const doc = documents.find((d) => d.id === id);
            if (doc) {
              deleteDocument(id, doc.filename);
            }
          }}
          isLoading={isLoading}
        />
      </div>

      {/* Next step CTA */}
      {hasDocuments && (
        <div className="flex justify-end pt-4 border-t">
          <Button
            size="lg"
            onClick={() => router.push(`/projects/${projectId}/schema`)}
          >
            Continue to Schema Definition
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
