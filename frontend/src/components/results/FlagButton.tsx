/**
 * FlagButton Component
 * Button to flag/unflag extraction results for review
 */

'use client';

import { Button } from '@/components/ui/button';
import { Flag } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FlagButtonProps {
  flagged: boolean;
  onToggle: () => void;
  disabled?: boolean;
  size?: 'sm' | 'default' | 'icon';
  className?: string;
}

export function FlagButton({
  flagged,
  onToggle,
  disabled,
  size = 'icon',
  className,
}: FlagButtonProps) {
  return (
    <Button
      variant={flagged ? 'default' : 'ghost'}
      size={size === 'icon' ? 'icon' : size}
      onClick={onToggle}
      disabled={disabled}
      className={cn(
        flagged && 'bg-orange-500 hover:bg-orange-600',
        className
      )}
      title={flagged ? 'Unflag for review' : 'Flag for review'}
    >
      <Flag className={cn('h-4 w-4', flagged && 'fill-current')} />
      {size !== 'icon' && (
        <span className="ml-2">{flagged ? 'Flagged' : 'Flag'}</span>
      )}
    </Button>
  );
}
