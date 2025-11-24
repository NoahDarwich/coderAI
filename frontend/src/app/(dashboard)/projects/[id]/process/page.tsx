/**
 * Processing Page - Step 4: Process documents with extraction
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SampleTesting } from '@/components/workflow/step4/SampleTesting';
import { FullProcessing } from '@/components/workflow/step4/FullProcessing';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { useProjectStore } from '@/store/projectStore';
import { useSchemaWizardStore } from '@/store/schemaWizardStore';
import { ProcessingJob, ProcessingLog } from '@/types';
import { generateId, sleep } from '@/lib/utils';
import { mockDocuments } from '@/mocks/mockDocuments';

export default function ProcessPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { updateProject } = useProjectStore();
  const { variables } = useSchemaWizardStore();

  const [mounted, setMounted] = useState(false);
  const [job, setJob] = useState<ProcessingJob | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState<'sample' | 'full'>('sample');
  const [sampleApproved, setSampleApproved] = useState(false);

  // Get total documents count
  const projectDocs = mockDocuments.filter((doc) => doc.projectId === projectId);
  const totalDocuments = projectDocs.length || 10;

  useEffect(() => {
    setMounted(true);
  }, []);

  // Simulate processing
  const startProcessing = async () => {
    setIsProcessing(true);

    // Get documents for this project
    const projectDocs = mockDocuments.filter((doc) => doc.projectId === projectId);
    const totalDocs = projectDocs.length || 10; // Default to 10 if no documents

    const newJob: ProcessingJob = {
      id: generateId(),
      projectId,
      type: 'full',
      status: 'processing',
      progress: 0,
      totalDocuments: totalDocs,
      processedDocuments: 0,
      startedAt: new Date().toISOString(),
      logs: [
        {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: `Processing started for ${totalDocs} documents`,
        },
      ],
    };

    setJob(newJob);

    // Simulate processing each document
    for (let i = 0; i < totalDocs; i++) {
      await sleep(800); // Simulate processing time

      const progress = Math.round(((i + 1) / totalDocs) * 100);
      const docName = projectDocs[i]?.fileName || `document_${i + 1}.pdf`;

      setJob((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          progress,
          processedDocuments: i + 1,
          logs: [
            ...prev.logs,
            {
              timestamp: new Date().toISOString(),
              level: 'info',
              message: `Processing document: ${docName}`,
              documentId: projectDocs[i]?.id,
            },
          ],
        };
      });
    }

    // Mark as completed
    await sleep(500);
    setJob((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        status: 'completed',
        completedAt: new Date().toISOString(),
        logs: [
          ...prev.logs,
          {
            timestamp: new Date().toISOString(),
            level: 'info',
            message: 'Processing completed successfully',
          },
        ],
      };
    });

    setIsProcessing(false);

    // Update project status
    updateProject(projectId, {
      status: 'complete',
      processingComplete: true,
    });

    // Show success toast notification
    toast.success('Processing Complete!', {
      description: `Successfully processed ${totalDocs} documents. View results now.`,
      action: {
        label: 'View Results',
        onClick: () => router.push(`/projects/${projectId}/results`),
      },
    });
  };

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

        <WorkflowProgress currentStep={4} />
      </div>

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
            variables={variables}
            totalDocuments={totalDocuments}
            onApprove={handleSampleApprove}
            onRefineSchema={handleRefineSchema}
          />
        </TabsContent>

        <TabsContent value="full">
          <FullProcessing
            job={job}
            onStart={startProcessing}
            onContinue={handleContinue}
            isProcessing={isProcessing}
            canStart={!job}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
