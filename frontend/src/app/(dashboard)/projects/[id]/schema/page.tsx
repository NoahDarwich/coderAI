/**
 * Schema Definition Page - Step 2: Define extraction variables through wizard
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SchemaWizard } from '@/components/workflow/step2/SchemaWizard';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { useProjectStore } from '@/store/projectStore';

export default function SchemaPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { updateProject } = useProjectStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleComplete = () => {
    // Update project status to review phase
    updateProject(projectId, {
      status: 'review',
      schemaComplete: false, // Not complete until reviewed
    });
    router.push(`/projects/${projectId}/schema/review`);
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
              Define Extraction Schema
            </h1>
            <p className="text-gray-600">
              Define the variables you want to extract from your documents
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

        <WorkflowProgress currentStep={2} />
      </div>

      <SchemaWizard projectId={projectId} onComplete={handleComplete} />
    </div>
  );
}
