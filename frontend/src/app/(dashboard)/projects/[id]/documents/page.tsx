/**
 * Documents Page - Step 1: Upload and manage project documents
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowRight, ArrowLeft, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { DocumentUploader } from '@/components/workflow/step1/DocumentUploader';
import { DocumentList } from '@/components/workflow/step1/DocumentList';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { useProjectStore } from '@/store/projectStore';
import { Document } from '@/types';
import { generateId } from '@/lib/utils';
import { mockDocuments } from '@/mocks/mockDocuments';

export default function DocumentsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { updateProject } = useProjectStore();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Load documents for this project
  useEffect(() => {
    if (!mounted) return;

    const loadDocuments = async () => {
      setIsLoading(true);
      try {
        // Simulate API call - filter mock documents by projectId
        await new Promise((resolve) => setTimeout(resolve, 500));
        const projectDocs = mockDocuments.filter((doc) => doc.projectId === projectId);
        setDocuments(projectDocs);
      } finally {
        setIsLoading(false);
      }
    };

    loadDocuments();
  }, [projectId, mounted]);

  const handleUpload = async (files: File[]) => {
    setIsUploading(true);
    try {
      // Simulate upload - in real app, this would call API
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const newDocuments: Document[] = files.map((file) => ({
        id: generateId(),
        projectId,
        fileName: file.name,
        fileType: file.name.endsWith('.pdf')
          ? 'pdf'
          : file.name.endsWith('.docx')
          ? 'docx'
          : 'txt',
        fileSize: file.size,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded',
        contentPreview: 'Sample document content preview...',
      }));

      setDocuments((prev) => [...prev, ...newDocuments]);

      // Update project document count
      updateProject(projectId, {
        documentCount: documents.length + newDocuments.length,
        status: 'setup',
      });
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));

      // Update project document count
      updateProject(projectId, {
        documentCount: documents.length - 1,
      });
    } catch (error) {
      console.error('Delete failed:', error);
      throw error;
    }
  };

  const handleContinue = () => {
    // Update project status to schema phase
    updateProject(projectId, {
      status: 'schema',
    });
    router.push(`/projects/${projectId}/schema`);
  };

  if (!mounted) {
    return null;
  }

  const hasDocuments = documents.length > 0;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button
        variant="ghost"
        onClick={() => router.push(`/projects/${projectId}`)}
        className="mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Project
      </Button>

      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Upload Documents
            </h1>
            <p className="text-gray-600">
              Upload your documents to start the extraction process
            </p>
          </div>
        </div>

        <WorkflowProgress currentStep={1} />
      </div>

      <div className="space-y-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Documents</CardTitle>
            <CardDescription>
              Drag and drop files or click to browse. Supported formats: PDF, DOCX, TXT (max 10MB per file)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DocumentUploader onUpload={handleUpload} isUploading={isUploading} />
          </CardContent>
        </Card>

        {/* Documents List */}
        <Card>
          <CardHeader>
            <CardTitle>
              Uploaded Documents {documents.length > 0 && `(${documents.length})`}
            </CardTitle>
            <CardDescription>
              Manage your uploaded documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DocumentList
              documents={documents}
              onDelete={handleDelete}
              isLoading={isLoading}
            />
          </CardContent>
        </Card>

        {/* Continue Button */}
        {hasDocuments && (
          <div className="flex justify-end">
            <Button size="lg" onClick={handleContinue}>
              Continue to Schema Definition
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
