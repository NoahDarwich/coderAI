/**
 * SourceTextView Component
 * Displays the source text snippet for an extracted value
 */

'use client';

import { Card } from '@/components/ui/card';
import { FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SourceTextViewProps {
  sourceText?: string;
  label?: string;
  className?: string;
}

export function SourceTextView({
  sourceText,
  label = 'Source text',
  className,
}: SourceTextViewProps) {
  if (!sourceText) {
    return (
      <Card className={cn('p-4 text-center', className)}>
        <FileText className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
        <p className="text-sm text-muted-foreground">
          No source text available
        </p>
      </Card>
    );
  }

  return (
    <Card className={cn('p-4', className)}>
      <p className="text-xs font-medium text-muted-foreground mb-2">
        {label}
      </p>
      <blockquote className="border-l-4 border-primary pl-4 italic text-sm">
        &ldquo;{sourceText}&rdquo;
      </blockquote>
    </Card>
  );
}
