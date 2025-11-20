/**
 * Sidebar Component
 * Project navigation sidebar for document/schema/results pages
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  FileText,
  MessageSquare,
  Table2,
  Download,
  Play,
  Home,
} from 'lucide-react';

interface SidebarProps {
  projectId: string;
  className?: string;
}

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

export function Sidebar({ projectId, className }: SidebarProps) {
  const pathname = usePathname();

  const navItems: NavItem[] = [
    {
      label: 'Overview',
      href: `/projects/${projectId}`,
      icon: <Home className="h-4 w-4" />,
    },
    {
      label: 'Documents',
      href: `/projects/${projectId}/documents`,
      icon: <FileText className="h-4 w-4" />,
    },
    {
      label: 'Schema',
      href: `/projects/${projectId}/schema`,
      icon: <MessageSquare className="h-4 w-4" />,
    },
    {
      label: 'Process',
      href: `/projects/${projectId}/process`,
      icon: <Play className="h-4 w-4" />,
    },
    {
      label: 'Results',
      href: `/projects/${projectId}/results`,
      icon: <Table2 className="h-4 w-4" />,
    },
    {
      label: 'Export',
      href: `/projects/${projectId}/export`,
      icon: <Download className="h-4 w-4" />,
    },
  ];

  return (
    <aside
      className={cn(
        'w-64 border-r border-border bg-background',
        className
      )}
    >
      <nav className="space-y-1 p-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Workflow stepper indicator */}
      <div className="p-4 border-t border-border">
        <div className="text-xs font-medium text-muted-foreground mb-2">
          Project Workflow
        </div>
        <div className="space-y-1 text-xs text-muted-foreground">
          <div>1. Upload documents</div>
          <div>2. Define schema</div>
          <div>3. Test on sample</div>
          <div>4. Process all documents</div>
          <div>5. Review results</div>
          <div>6. Export data</div>
        </div>
      </div>
    </aside>
  );
}
