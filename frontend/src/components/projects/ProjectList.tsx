'use client';

import { useEffect, useState } from 'react';
import { useProjectStore } from '@/lib/store/projectStore';
import { ProjectCard } from './ProjectCard';
import { EmptyState } from './EmptyState';
import { DeleteProjectDialog } from './DeleteProjectDialog';
import { Loader2 } from 'lucide-react';

export function ProjectList() {
  const { projects, isLoading, fetchProjects, deleteProject } = useProjectStore();
  const [deleteProjectId, setDeleteProjectId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleDelete = async () => {
    if (!deleteProjectId) return;

    setIsDeleting(true);
    try {
      await deleteProject(deleteProjectId);
      setDeleteProjectId(null);
    } catch (error) {
      console.error('Failed to delete project:', error);
    } finally {
      setIsDeleting(false);
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
        isDeleting={isDeleting}
      />
    </>
  );
}
