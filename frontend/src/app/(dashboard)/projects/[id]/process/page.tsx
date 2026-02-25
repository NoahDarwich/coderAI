/**
 * Processing Page - Step 5: Process documents with extraction
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SampleTesting } from '@/components/workflow/step4/SampleTesting';
import { FullProcessing } from '@/components/workflow/step4/FullProcessing';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { useDocuments } from '@/lib/api/documents';
import { useVariables } from '@/lib/api/schema';

export default function ProcessPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState<'sample' | 'full'>('sample');
  const [sampleApproved, setSampleApproved] = useState(false);

  // Fetch documents and variables from API
  const { data: documents = [], isLoading: documentsLoading } = useDocuments(projectId);
  const { data: variables = [], isLoading: variablesLoading } = useVariables(projectId);

  // Debug logging
  useEffect(() => {
    console.log('=== PROCESS PAGE DEBUG ===');
    console.log('Project ID:', projectId);
    console.log('Variables loading:', variablesLoading);
    console.log('Variables data:', variables);
    console.log('Variables count:', variables?.length);
    console.log('Documents count:', documents?.length);
    console.log('========================');
  }, [projectId, variables, variablesLoading, documents]);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSampleApprove = () => {
    setSampleApproved(true);
    setActiveTab('full');
  };

  const handleRefineSchema = () => {
    router.push(`/projects/${projectId}/schema`);
  };

  const handleContinue = () => {
    router.push(`/projects/${projectId}/results`);
  };

  if (!mounted) {
    return null;
  }

  const isLoading = documentsLoading || variablesLoading;
  const totalDocuments = documents.length;

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
              Processing Documents
            </h1>
            <p className="text-gray-600">
              Extract data from your documents using the defined schema
            </p>
          </div>
        </div>

        <WorkflowProgress currentStep={5} />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Loading documents and variables...</div>
        </div>
      ) : (
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'sample' | 'full')} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="sample">
              Phase A: Sample Testing
            </TabsTrigger>
            <TabsTrigger value="full" disabled={!sampleApproved}>
              Phase B: Full Processing
            </TabsTrigger>
          </TabsList>

          <TabsContent value="sample">
            <SampleTesting
              projectId={projectId}
              documents={documents}
              variables={variables}
              totalDocuments={totalDocuments}
              onApprove={handleSampleApprove}
              onRefineSchema={handleRefineSchema}
            />
          </TabsContent>

          <TabsContent value="full">
            <FullProcessing
              projectId={projectId}
              documents={documents}
              onContinue={handleContinue}
            />
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
