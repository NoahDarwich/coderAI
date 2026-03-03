'use client';

import { useState } from 'react';
import { useProjects, useDeleteProject } from '@/lib/api/projects';
import { ProjectCard } from './ProjectCard';
import { EmptyState } from './EmptyState';
import { DeleteProjectDialog } from './DeleteProjectDialog';
import { Loader2 } from 'lucide-react';

export function ProjectList() {
  const { data: projects = [], isLoading } = useProjects();
  const deleteProjectMutation = useDeleteProject();
  const [deleteProjectId, setDeleteProjectId] = useState<string | null>(null);

  const handleDelete = async () => {
    if (!deleteProjectId) return;
    try {
      await deleteProjectMutation.mutateAsync(deleteProjectId);
      setDeleteProjectId(null);
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-slate-600 dark:text-slate-400" />
      </div>
    );
  }

  if (projects.length === 0) {
    return <EmptyState />;
  }

  return (
    <>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            onDelete={(id) => setDeleteProjectId(id)}
          />
        ))}
      </div>

      <DeleteProjectDialog
        open={!!deleteProjectId}
        onOpenChange={(open) => !open && setDeleteProjectId(null)}
        onConfirm={handleDelete}
        isDeleting={deleteProjectMutation.isPending}
      />
    </>
  );
}
