/**
 * Project Detail Layout
 * Layout for all project-specific pages with sidebar navigation
 */

'use client';

import { useEffect } from 'react';
import { useParams, notFound } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { useProjectStore } from '@/lib/store/projectStore';

export default function ProjectLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const projectId = params.id as string;
  const { projects, fetchProjects, getProjectById } = useProjectStore();

  useEffect(() => {
    if (projects.length === 0) {
      fetchProjects();
    }
  }, [projects.length, fetchProjects]);

  // Check if project exists
  const project = getProjectById(projectId);

  // If projects are loaded but project doesn't exist, show 404
  if (projects.length > 0 && !project) {
    notFound();
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <Sidebar projectId={projectId} />

      {/* Main content area */}
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-6">
          {/* Project header */}
          {project && (
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-foreground">
                {project.name}
              </h1>
              {project.description && (
                <p className="text-muted-foreground mt-1">
                  {project.description}
                </p>
              )}
            </div>
          )}

          {/* Page content */}
          {children}
        </div>
      </main>
    </div>
  );
}
