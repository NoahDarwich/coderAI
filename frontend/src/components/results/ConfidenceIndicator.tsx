/**
 * ConfidenceIndicator Component
 * Colored dot indicator for confidence scores
 */

'use client';

import { cn } from '@/lib/utils';

interface ConfidenceIndicatorProps {
  confidence: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function ConfidenceIndicator({
  confidence,
  size = 'md',
  showLabel = false,
  className,
}: ConfidenceIndicatorProps) {
  const getColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getSizeClass = () => {
    switch (size) {
      case 'sm':
        return 'h-2 w-2';
      case 'lg':
        return 'h-4 w-4';
      default:
        return 'h-3 w-3';
    }
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div
        className={cn(
          'rounded-full',
          getColor(confidence),
          getSizeClass()
        )}
        title={`${confidence}% confidence`}
      />
      {showLabel && (
        <span className="text-xs text-muted-foreground">{confidence}%</span>
      )}
    </div>
  );
}
