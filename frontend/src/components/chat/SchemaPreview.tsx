/**
 * SchemaPreview Component
 * Sidebar showing the schema being built
 */

'use client';

import { SchemaVariable } from '@/lib/types/api';
import { VariableCard } from './VariableCard';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Layers, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SchemaPreviewProps {
  schema: SchemaVariable[];
  onApprove?: () => void;
  isApproved?: boolean;
  isLoading?: boolean;
  className?: string;
}

export function SchemaPreview({
  schema,
  onApprove,
  isApproved,
  isLoading,
  className,
}: SchemaPreviewProps) {
  const hasSchema = schema.length > 0;

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <Layers className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold">Schema Preview</h3>
      </div>

      {/* Schema variables */}
      {hasSchema ? (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            {schema.length} variable{schema.length !== 1 ? 's' : ''} defined
          </p>

          {schema.map((variable) => (
            <VariableCard key={variable.id} variable={variable} />
          ))}
        </div>
      ) : (
        <Card className="p-6 text-center">
          <AlertCircle className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
          <p className="text-sm text-muted-foreground">
            No schema defined yet. Chat with the AI to build your extraction
            schema.
          </p>
        </Card>
      )}

      {/* Approve button */}
      {hasSchema && onApprove && !isApproved && (
        <Button
          onClick={onApprove}
          disabled={isLoading}
          className="w-full"
          size="lg"
        >
          {isLoading ? 'Approving...' : 'Approve Schema & Continue'}
        </Button>
      )}

      {isApproved && (
        <Card className="p-4 bg-green-50 border-green-600 dark:bg-green-950">
          <p className="text-sm font-medium text-green-900 dark:text-green-100">
            ✓ Schema approved and ready for processing
          </p>
        </Card>
      )}
    </div>
  );
}
