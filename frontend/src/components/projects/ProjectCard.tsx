import Link from 'next/link';
import { Project } from '@/lib/types/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Trash2, Calendar } from 'lucide-react';
import { formatDistanceToNow } from '@/lib/utils/formatting';

interface ProjectCardProps {
  project: Project;
  onDelete: (id: string) => void;
}

export function ProjectCard({ project, onDelete }: ProjectCardProps) {
  const statusColors: Record<string, string> = {
    draft: 'bg-gray-500',
    processing: 'bg-yellow-500',
    completed: 'bg-green-500',
    error: 'bg-red-500',
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-xl">{project.name}</CardTitle>
            <CardDescription className="mt-2">
              {project.description}
            </CardDescription>
          </div>
          <Badge className={statusColors[project.status]}>
            {project.status}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            <span>{project.documentCount} documents</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>{formatDistanceToNow(project.createdAt)}</span>
          </div>
        </div>
      </CardContent>

      <CardFooter className="flex gap-2">
        <Link href={`/projects/${project.id}/documents`} className="flex-1">
          <Button className="w-full" variant="default">
            Open Project
          </Button>
        </Link>
        <Button
          variant="destructive"
          size="icon"
          onClick={() => onDelete(project.id)}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
