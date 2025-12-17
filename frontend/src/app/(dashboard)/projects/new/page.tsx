'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ProjectSetupForm } from '@/components/projects/ProjectSetupForm';
import { useCreateProject } from '@/lib/api/projects';
import { ProjectFormData } from '@/lib/validations';

export default function NewProjectPage() {
  const router = useRouter();
  const createProject = useCreateProject();
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: ProjectFormData) => {
    console.log('Form submitted with data:', data);
    setError(null);

    try {
      // Create project via backend API
      // Note: Form only has name and scale, so we use name as description
      const newProject = await createProject.mutateAsync({
        name: data.name,
        description: `${data.scale === 'small' ? 'Small-scale' : 'Large-scale'} research project`,
      });

      console.log('Project created successfully:', newProject);

      // Navigate to the new project documents page
      router.push(`/projects/${newProject.id}/documents`);
    } catch (err) {
      console.error('Failed to create project:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to create project: ${errorMessage}`);
    }
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

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
          <CardDescription>
            Provide basic information about your research project.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {createProject.isPending ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <span className="ml-3 text-muted-foreground">Creating project...</span>
            </div>
          ) : (
            <ProjectSetupForm onSubmit={handleSubmit} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
