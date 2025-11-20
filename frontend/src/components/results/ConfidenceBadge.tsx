/**
 * ConfidenceBadge Component
 * Badge showing confidence score with color coding
 */

'use client';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface ConfidenceBadgeProps {
  confidence: number; // 0-100
  className?: string;
}

export function ConfidenceBadge({
  confidence,
  className,
}: ConfidenceBadgeProps) {
  const getVariant = (score: number): 'default' | 'secondary' | 'destructive' => {
    if (score >= 90) return 'default';
    if (score >= 70) return 'secondary';
    return 'destructive';
  };

  const getLabel = (score: number) => {
    if (score >= 90) return 'High';
    if (score >= 70) return 'Medium';
    return 'Low';
  };

  return (
    <Badge
      variant={getVariant(confidence)}
      className={cn('text-xs', className)}
    >
      {getLabel(confidence)} ({confidence}%)
    </Badge>
  );
}
