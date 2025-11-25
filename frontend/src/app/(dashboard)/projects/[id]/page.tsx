'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Upload, Settings, FileText, Play, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { useProjectStore } from '@/store/projectStore';
import { useWorkflowStore } from '@/store/workflowStore';
import { formatRelativeTime } from '@/lib/utils';
import { cn } from '@/lib/utils';

const STATUS_TO_STEP: Record<string, number> = {
  setup: 1,
  schema: 2,
  review: 3,
  processing: 4,
  complete: 5,
};

const STATUS_LABELS: Record<string, string> = {
  setup: 'Setup',
  schema: 'Defining Schema',
  review: 'Reviewing',
  processing: 'Processing',
  complete: 'Complete',
};

const STATUS_COLORS: Record<string, string> = {
  setup: 'bg-blue-100 text-blue-800 border-blue-200',
  schema: 'bg-purple-100 text-purple-800 border-purple-200',
  review: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  processing: 'bg-orange-100 text-orange-800 border-orange-200',
  complete: 'bg-green-100 text-green-800 border-green-200',
};

export default function ProjectOverviewPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const projectStore = useProjectStore();
  const { setStep } = useWorkflowStore();
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    // Give Zustand persist middleware time to hydrate from localStorage
    const timer = setTimeout(() => {
      setHydrated(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Get project directly from store (only after hydration)
  const project = hydrated ? projectStore.projects.find((p) => p.id === projectId) : null;

  useEffect(() => {
    if (hydrated && project) {
      console.log('Setting workflow step for project:', project.name);
      setStep(STATUS_TO_STEP[project.status] || 1);
    }
  }, [hydrated, project, setStep]);

  useEffect(() => {
    if (hydrated && !project && projectStore.projects.length > 0) {
      console.log('Project not found, redirecting to /projects');
      router.push('/projects');
    }
  }, [hydrated, project, projectStore.projects, router]);

  // Show loading while hydrating
  if (!hydrated) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3" />
          <div className="h-32 bg-gray-200 rounded" />
          <div className="h-64 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  // If project not found after hydration, show loading (will redirect)
  if (!project) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3" />
          <div className="h-32 bg-gray-200 rounded" />
          <div className="h-64 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  const currentStep = STATUS_TO_STEP[project.status] || 1;

  console.log('Rendering project overview page with project:', project.name, 'currentStep:', currentStep);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button
        variant="ghost"
        onClick={() => router.push('/projects')}
        className="mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Projects
      </Button>

      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {project.name}
            </h1>
            <p className="text-gray-600">
              {project.scale === 'small' ? 'Small Project' : 'Large Project'} •
              Created {formatRelativeTime(project.createdAt)}
            </p>
          </div>
          <Badge
            variant="outline"
            className={cn('text-sm', STATUS_COLORS[project.status])}
          >
            {STATUS_LABELS[project.status] || project.status}
          </Badge>
        </div>

        <WorkflowProgress currentStep={currentStep} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Documents</CardDescription>
            <CardTitle className="text-3xl">{project.documentCount || 0}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              {project.scale === 'small' ? 'Up to 50 documents' : '50+ documents'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Variables Defined</CardDescription>
            <CardTitle className="text-3xl">0</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              Data fields to extract
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Progress</CardDescription>
            <CardTitle className="text-3xl">
              {Math.round((currentStep / 5) * 100)}%
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              Step {currentStep} of 5 complete
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Next Steps</CardTitle>
          <CardDescription>
            What you need to do to progress this project
          </CardDescription>
        </CardHeader>
        <CardContent>
          {currentStep === 1 && (
            <div className="space-y-4">
              <p className="text-gray-700">
                Upload your documents to get started with data extraction.
              </p>
              <div className="flex flex-wrap gap-3">
                <Button
                  onClick={() => router.push(`/projects/${projectId}/documents`)}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Upload Documents
                </Button>
                <Button
                  variant="outline"
                  onClick={() => router.push(`/projects/${projectId}/schema`)}
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Define Schema
                </Button>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-4">
              <p className="text-gray-700">
                Define the variables you want to extract from your documents.
              </p>
              <Button
                onClick={() => router.push(`/projects/${projectId}/schema`)}
              >
                <Settings className="w-4 h-4 mr-2" />
                Define Schema
              </Button>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-4">
              <p className="text-gray-700">
                Review your extraction schema before processing.
              </p>
              <Button
                onClick={() => router.push(`/projects/${projectId}/review`)}
              >
                <FileText className="w-4 h-4 mr-2" />
                Review Schema
              </Button>
            </div>
          )}

          {currentStep === 4 && (
            <div className="space-y-4">
              <p className="text-gray-700">
                Your documents are being processed. This may take a few minutes.
              </p>
              <Button disabled>
                <Play className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </Button>
            </div>
          )}

          {currentStep === 5 && (
            <div className="space-y-4">
              <p className="text-gray-700">
                Your project is complete! View results and export your data.
              </p>
              <div className="flex flex-wrap gap-3">
                <Button
                  onClick={() => router.push(`/projects/${projectId}/results`)}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  View Results
                </Button>
                <Button variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
