'use client';

import { useState } from 'react';
import { ProjectList } from '@/components/projects/ProjectList';
import { NewProjectDialog } from '@/components/projects/NewProjectDialog';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

export default function DashboardPage() {
  const [isNewProjectDialogOpen, setIsNewProjectDialogOpen] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">
            Projects
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2">
            Manage your research extraction projects
          </p>
        </div>
        <Button
          size="lg"
          onClick={() => setIsNewProjectDialogOpen(true)}
        >
          <Plus className="mr-2 h-5 w-5" />
          New Project
        </Button>
      </div>

      <ProjectList />

      <NewProjectDialog
        open={isNewProjectDialogOpen}
        onOpenChange={setIsNewProjectDialogOpen}
      />
    </div>
  );
}
