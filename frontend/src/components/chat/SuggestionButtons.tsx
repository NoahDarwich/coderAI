/**
 * SuggestionButtons Component
 * Quick reply suggestion buttons
 */

'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SuggestionButtonsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
  disabled?: boolean;
  className?: string;
}

export function SuggestionButtons({
  suggestions,
  onSelect,
  disabled,
  className,
}: SuggestionButtonsProps) {
  if (suggestions.length === 0) return null;

  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {suggestions.map((suggestion, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          onClick={() => onSelect(suggestion)}
          disabled={disabled}
          className="text-sm"
        >
          {suggestion}
        </Button>
      ))}
    </div>
  );
}
