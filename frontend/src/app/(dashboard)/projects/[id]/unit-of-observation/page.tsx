/**
 * Unit of Observation Page - Step 2: Define the unit of observation
 */

'use client';

import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { UnitOfObservationWizard } from '@/components/workflow/step2/UnitOfObservationWizard';

export default function UnitOfObservationPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button
        variant="ghost"
        onClick={() => router.push(`/projects/${projectId}/documents`)}
        className="mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Documents
      </Button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Unit of Observation
        </h1>
        <p className="text-gray-600 mb-4">
          Define what each row in your extracted dataset will represent
        </p>
        <WorkflowProgress currentStep={2} />
      </div>

      <UnitOfObservationWizard projectId={projectId} />
    </div>
  );
}
