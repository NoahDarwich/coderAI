/**
 * MessageBubble Component
 * Displays a single chat message with markdown support
 */

'use client';

import { ChatMessage } from '@/lib/types/api';
import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { formatDate } from '@/lib/utils/formatting';

interface MessageBubbleProps {
  message: ChatMessage;
  className?: string;
}

export function MessageBubble({ message, className }: MessageBubbleProps) {
  const isAI = message.role === 'assistant';

  return (
    <div
      className={cn(
        'flex gap-3 mb-4',
        isAI ? 'justify-start' : 'justify-end',
        className
      )}
    >
      {/* Avatar - AI */}
      {isAI && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
          <Bot className="h-5 w-5 text-primary-foreground" />
        </div>
      )}

      {/* Message content */}
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-3',
          isAI
            ? 'bg-muted text-foreground'
            : 'bg-primary text-primary-foreground'
        )}
      >
        {/* Markdown content */}
        <div
          className={cn(
            'prose prose-sm max-w-none',
            isAI ? 'prose-slate' : 'prose-invert',
            // Custom prose styles
            '[&>*:first-child]:mt-0 [&>*:last-child]:mb-0',
            '[&_p]:leading-relaxed',
            '[&_strong]:font-semibold',
            '[&_ul]:my-2 [&_ol]:my-2',
            '[&_li]:my-1'
          )}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Timestamp */}
        <div
          className={cn(
            'text-xs mt-2',
            isAI ? 'text-muted-foreground' : 'text-primary-foreground/70'
          )}
        >
          {formatDate(message.timestamp)}
        </div>
      </div>

      {/* Avatar - User */}
      {!isAI && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
          <User className="h-5 w-5 text-primary-foreground" />
        </div>
      )}
    </div>
  );
}
