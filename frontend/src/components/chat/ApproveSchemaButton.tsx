/**
 * ApproveSchemaButton Component
 * Button to approve and finalize the schema
 */

'use client';

import { Button } from '@/components/ui/button';
import { CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ApproveSchemaButtonProps {
  onClick: () => void;
  disabled?: boolean;
  isLoading?: boolean;
  className?: string;
}

export function ApproveSchemaButton({
  onClick,
  disabled,
  isLoading,
  className,
}: ApproveSchemaButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={disabled || isLoading}
      size="lg"
      className={cn('w-full', className)}
    >
      <CheckCircle className="h-5 w-5 mr-2" />
      {isLoading ? 'Approving Schema...' : 'Approve Schema & Continue'}
    </Button>
  );
}
