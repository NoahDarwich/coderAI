'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Plus, FolderOpen, FileText, Calendar, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useProjectStore } from '@/store/projectStore';
import { Project } from '@/types';
import { formatRelativeTime } from '@/lib/utils';
import { cn } from '@/lib/utils';

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

export default function ProjectsPage() {
  const router = useRouter();
  const { projects, setProjects } = useProjectStore();
  const [isLoading, setIsLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const loadProjects = async () => {
      setIsLoading(true);
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));
        // Projects are already loaded from localStorage via Zustand persist
        // No need to call setProjects([]) - that would clear them!
      } finally {
        setIsLoading(false);
      }
    };

    if (mounted) {
      loadProjects();
    }
  }, [mounted]);

  if (!mounted) {
    return null;
  }

  const handleCreateProject = () => {
    router.push('/projects/new');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="mt-1 text-gray-600">
            Manage your research extraction projects
          </p>
        </div>
        <Button onClick={handleCreateProject} size="lg">
          <Plus className="w-5 h-5 mr-2" />
          New Project
        </Button>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded" />
                  <div className="h-4 bg-gray-200 rounded w-5/6" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && projects.length === 0 && (
        <Card className="text-center py-12">
          <CardContent className="pt-6">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                <FolderOpen className="w-8 h-8 text-gray-400" />
              </div>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              No projects yet
            </h2>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Create your first project to start extracting structured data from your documents.
            </p>
            <Button onClick={handleCreateProject} size="lg">
              <Plus className="w-5 h-5 mr-2" />
              Create Your First Project
            </Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && projects.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project: Project) => (
            <Link key={project.id} href={`/projects/${project.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                <CardHeader>
                  <div className="flex items-start justify-between mb-2">
                    <CardTitle className="text-xl">{project.name}</CardTitle>
                    <Badge
                      variant="outline"
                      className={cn(
                        'text-xs',
                        STATUS_COLORS[project.status] || 'bg-gray-100 text-gray-800'
                      )}
                    >
                      {STATUS_LABELS[project.status] || project.status}
                    </Badge>
                  </div>
                  <CardDescription>
                    {project.scale === 'small' ? 'Small Project' : 'Large Project'} •
                    Created {formatRelativeTime(project.createdAt)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center text-gray-600">
                        <FileText className="w-4 h-4 mr-1" />
                        <span>{project.documentCount || 0} documents</span>
                      </div>
                      {project.status === 'complete' && (
                        <div className="flex items-center text-green-600">
                          <TrendingUp className="w-4 h-4 mr-1" />
                          <span>Complete</span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center text-xs text-gray-500">
                      <Calendar className="w-3 h-3 mr-1" />
                      Updated {formatRelativeTime(project.updatedAt)}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
