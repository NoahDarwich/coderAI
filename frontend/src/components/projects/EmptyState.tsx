import { FolderOpen } from 'lucide-react';

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <FolderOpen className="h-16 w-16 text-slate-400 dark:text-slate-600 mb-4" />
      <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50 mb-2">
        No projects yet
      </h3>
      <p className="text-slate-600 dark:text-slate-400 max-w-md">
        Get started by creating your first research extraction project. Upload
        documents, define your schema, and extract structured data.
      </p>
    </div>
  );
}
