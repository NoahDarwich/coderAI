/**
 * Project Detail Layout
 * Layout for all project-specific pages with sidebar navigation
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useProjectStore } from '@/store/projectStore';

export default function ProjectLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { projects } = useProjectStore();
  const [mounted, setMounted] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Give Zustand persist middleware time to hydrate from localStorage
    const timer = setTimeout(() => {
      setHydrated(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Get project directly from store (only after hydration)
  const project = (mounted && hydrated) ? projects.find((p) => p.id === projectId) : null;

  // Redirect to projects list if project not found after hydration
  useEffect(() => {
    if (mounted && hydrated && !project && projects.length > 0) {
      console.log('Project not found in layout, redirecting to /projects');
      router.push('/projects');
    }
  }, [mounted, hydrated, project, projects, router]);

  // Simply render children - the page component handles project display
  return <>{children}</>;
}
