/**
 * TypingIndicator Component
 * Animated typing indicator for AI responses
 */

'use client';

import { cn } from '@/lib/utils';

interface TypingIndicatorProps {
  className?: string;
}

export function TypingIndicator({ className }: TypingIndicatorProps) {
  return (
    <div className={cn('flex items-center gap-1 p-3', className)}>
      <div className="flex gap-1">
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.3s]" />
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.15s]" />
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
      </div>
      <span className="text-sm text-muted-foreground ml-2">AI is thinking...</span>
    </div>
  );
}
