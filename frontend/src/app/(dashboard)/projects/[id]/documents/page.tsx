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
import { apiClient } from '@/lib/api/client';
import { useDocuments } from '@/lib/api/documents';

export default function DocumentsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { updateProject } = useProjectStore();

  const [isUploading, setIsUploading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [textDocName, setTextDocName] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  // Load documents for this project using API hook
  const { data: documents = [], isLoading, refetch } = useDocuments(projectId);

  const handleUpload = async (files: File[]) => {
    setIsUploading(true);
    try {
      // Upload each file to backend sequentially
      for (const file of files) {
        await apiClient.upload(`/api/v1/projects/${projectId}/documents`, file);
      }
      await refetch();
      updateProject(projectId, { status: 'setup' });
    } catch (error) {
      throw error;
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    await apiClient.delete(`/api/v1/documents/${documentId}`);
    await refetch();
  };

  const handleTextSubmit = async () => {
    if (!textInput.trim() || !textDocName.trim()) return;

    setIsUploading(true);
    try {
      await apiClient.post(`/api/v1/projects/${projectId}/documents/text`, {
        name: textDocName,
        content: textInput,
      });
      await refetch();
      setTextInput('');
      setTextDocName('');
      updateProject(projectId, { status: 'setup' });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Failed to create text document: ${errorMessage}`);
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
