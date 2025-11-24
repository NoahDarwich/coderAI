'use client';

import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ProjectSetupForm } from '@/components/projects/ProjectSetupForm';
import { useProjectStore } from '@/store/projectStore';
import { ProjectFormData } from '@/lib/validations';
import { Project } from '@/types';
import { generateId } from '@/lib/utils';

export default function NewProjectPage() {
  const router = useRouter();
  const { addProject } = useProjectStore();

  const handleSubmit = async (data: ProjectFormData) => {
    console.log('Form submitted with data:', data);

    const newProject: Project = {
      id: generateId(),
      name: data.name,
      scale: data.scale,
      status: 'setup',
      documentCount: 0,
      schemaComplete: false,
      processingComplete: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    console.log('Creating project:', newProject);
    addProject(newProject);

    await new Promise((resolve) => setTimeout(resolve, 500));

    console.log('Navigating to:', `/projects/${newProject.id}`);
    router.push(`/projects/${newProject.id}`);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button
        variant="ghost"
        onClick={() => router.push('/projects')}
        className="mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Projects
      </Button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Create New Project
        </h1>
        <p className="text-gray-600">
          Set up a new research extraction project to get started.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
          <CardDescription>
            Provide basic information about your research project.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ProjectSetupForm onSubmit={handleSubmit} />
        </CardContent>
      </Card>
    </div>
  );
}
