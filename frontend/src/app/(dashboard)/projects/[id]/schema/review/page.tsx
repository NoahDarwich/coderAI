/**
 * Schema Review Page - Step 3: Review and confirm extraction schema
 */

'use client';

import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SchemaReview } from '@/components/workflow/step3/SchemaReview';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { useProjectStore } from '@/store/projectStore';

export default function SchemaReviewPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { updateProject } = useProjectStore();

  const handleConfirm = () => {
    // Update project status to processing phase
    updateProject(projectId, {
      status: 'processing',
      schemaComplete: true,
    });
    router.push(`/projects/${projectId}/process`);
  };

  const handleBackToWizard = () => {
    router.push(`/projects/${projectId}/schema`);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
              Review Schema
            </h1>
            <p className="text-gray-600">
              Review and confirm your extraction schema before processing
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => router.push('/projects')}
            aria-label="Save and return to dashboard"
          >
            Save & Exit
          </Button>
        </div>

        <WorkflowProgress currentStep={3} />
      </div>

      <SchemaReview
        projectId={projectId}
        onConfirm={handleConfirm}
        onBackToWizard={handleBackToWizard}
      />
    </div>
  );
}
