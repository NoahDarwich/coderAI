/**
 * Documents Page - Step 1: Upload and manage project documents
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowRight, ArrowLeft, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { DocumentUploader } from '@/components/workflow/step1/DocumentUploader';
import { DocumentList } from '@/components/workflow/step1/DocumentList';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { useProjectStore } from '@/store/projectStore';
import { Document } from '@/types';
import { generateId } from '@/lib/utils';
import { apiClient } from '@/lib/api/client';
import { useDocuments } from '@/lib/api/documents';

export default function DocumentsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { updateProject } = useProjectStore();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [textDocName, setTextDocName] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  // Load documents for this project using API hook
  const { data: apiDocuments, isLoading, refetch } = useDocuments(projectId);

  // Update local state when API data changes
  useEffect(() => {
    if (apiDocuments) {
      // Map from API Document to @/types Document
      setDocuments(apiDocuments.map((d) => ({
        id: d.id,
        projectId: d.projectId,
        fileName: d.filename || d.name,
        fileType: d.fileType as Document['fileType'],
        fileSize: d.fileSize,
        uploadedAt: d.uploadedAt,
        status: 'uploaded' as Document['status'],
        contentPreview: (d as any).contentPreview,
      })));
    }
  }, [apiDocuments]);

  const handleUpload = async (files: File[]) => {
    setIsUploading(true);
    try {
      // Simulate upload - in real app, this would call API
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const newDocuments: Document[] = files.map((file) => ({
        id: generateId(),
        projectId,
        fileName: file.name,
        fileType: (file.name.endsWith('.pdf')
          ? 'pdf'
          : file.name.endsWith('.docx')
          ? 'docx'
          : 'txt') as Document['fileType'],
        fileSize: file.size,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded' as Document['status'],
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

  const handleTextSubmit = async () => {
    if (!textInput.trim() || !textDocName.trim()) return;

    setIsUploading(true);
    try {
      // Check if using mock data
      const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

      if (useMockData) {
        // Mock mode - simulate creation
        await new Promise((resolve) => setTimeout(resolve, 500));

        const newDoc: Document = {
          id: generateId(),
          projectId,
          fileName: textDocName,
          fileType: 'txt',
          fileSize: new Blob([textInput]).size,
          uploadedAt: new Date().toISOString(),
          status: 'uploaded',
          contentPreview: textInput.substring(0, 200),
        };

        setDocuments((prev) => [...prev, newDoc]);
      } else {
        // Real API call
        const response = await apiClient.post(
          `/api/v1/projects/${projectId}/documents/text`,
          {
            name: textDocName,
            content: textInput,
          }
        );

        // Convert backend response to frontend format
        const backendDoc = response as any;
        const newDoc: Document = {
          id: backendDoc.id,
          projectId: backendDoc.project_id,
          fileName: backendDoc.name,
          fileType: (backendDoc.content_type || 'txt').toLowerCase() as Document['fileType'],
          fileSize: backendDoc.size_bytes,
          uploadedAt: backendDoc.uploaded_at,
          status: 'uploaded',
          contentPreview: textInput.substring(0, 200),
        };

        setDocuments((prev) => [...prev, newDoc]);

        // Refetch documents to get updated list from backend
        refetch();
      }

      // Clear form
      setTextInput('');
      setTextDocName('');

      // Update project document count
      updateProject(projectId, {
        documentCount: documents.length + 1,
        status: 'setup',
      });
    } catch (error) {
      console.error('Text document creation failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Failed to create text document: ${errorMessage}\n\nPlease make sure:\n1. Backend is running (http://localhost:8000)\n2. Project exists in backend\n3. Check browser console for details`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleContinue = () => {
    router.push(`/projects/${projectId}/unit-of-observation`);
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
        {/* Upload/Text Input Section */}
        <Card>
          <CardHeader>
            <CardTitle>Add Documents</CardTitle>
            <CardDescription>
              Upload files or paste text directly for quick testing (MVP feature)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="upload" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="upload">Upload Files</TabsTrigger>
                <TabsTrigger value="text">Paste Text (MVP)</TabsTrigger>
              </TabsList>

              <TabsContent value="upload" className="mt-4">
                <DocumentUploader onUpload={handleUpload} isUploading={isUploading} />
              </TabsContent>

              <TabsContent value="text" className="mt-4 space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="docName">Document Name</Label>
                  <Input
                    id="docName"
                    placeholder="e.g., Article 1, Event Report, News Article..."
                    value={textDocName}
                    onChange={(e) => setTextDocName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="textContent">Text Content</Label>
                  <Textarea
                    id="textContent"
                    placeholder="Paste your text content here...&#10;&#10;Example: News articles, reports, documents, or any text you want to extract data from."
                    rows={15}
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    className="font-mono text-sm"
                  />
                  <p className="text-sm text-muted-foreground">
                    Tip: You can paste text in any language. The AI will extract structured data based on your defined variables.
                  </p>
                </div>

                <Button
                  onClick={handleTextSubmit}
                  disabled={!textInput.trim() || !textDocName.trim() || isUploading}
                  className="w-full"
                  size="lg"
                >
                  <FileText className="mr-2 h-4 w-4" />
                  {isUploading ? 'Adding...' : 'Add Text Document'}
                </Button>
              </TabsContent>
            </Tabs>
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
              Continue to Unit of Observation
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
