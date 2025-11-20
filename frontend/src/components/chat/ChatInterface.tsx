/**
 * ChatInterface Component
 * Main chat interface for schema definition
 */

'use client';

import { useEffect, useRef } from 'react';
import { ChatMessage } from '@/lib/types/api';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  isTyping?: boolean;
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  className?: string;
}

export function ChatInterface({
  messages,
  isTyping,
  onSendMessage,
  disabled,
  className,
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  return (
    <Card className={cn('flex flex-col h-full', className)}>
      {/* Messages area */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-6 space-y-4"
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <p className="text-muted-foreground">
                Start a conversation to define your extraction schema
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}

            {isTyping && <TypingIndicator />}

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input area */}
      <div className="border-t p-4">
        <ChatInput
          onSend={onSendMessage}
          disabled={disabled || isTyping}
          placeholder="Type your message..."
        />
      </div>
    </Card>
  );
}
