/**
 * Schema Definition Page
 * Conversational UI for defining extraction schema
 */

'use client';

import { useParams, useRouter } from 'next/navigation';
import { useChat } from '@/lib/hooks/useChat';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { SchemaPreview } from '@/components/chat/SchemaPreview';
import { Button } from '@/components/ui/button';
import { MessageSquare, ArrowRight } from 'lucide-react';

export default function SchemaPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const {
    messages,
    schema,
    isTyping,
    isSchemaApproved,
    isLoading,
    sendMessage,
    approveSchema,
    isSaving,
  } = useChat(projectId);

  const handleApprove = async () => {
    await approveSchema();
    // Redirect to results page after approval
    router.push(`/projects/${projectId}/results`);
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <MessageSquare className="h-6 w-6" />
            Define Extraction Schema
          </h2>
          <p className="text-muted-foreground mt-1">
            Chat with AI to define what data to extract from your documents
          </p>
        </div>

        {isSchemaApproved && (
          <Button
            onClick={() => router.push(`/projects/${projectId}/results`)}
          >
            View Results
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Main content - Chat and Schema Preview side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[600px]">
        {/* Chat Interface - 2/3 width on large screens */}
        <div className="lg:col-span-2">
          <ChatInterface
            messages={messages}
            isTyping={isTyping}
            onSendMessage={sendMessage}
            disabled={isLoading || isSchemaApproved}
            className="h-[600px]"
          />
        </div>

        {/* Schema Preview - 1/3 width on large screens */}
        <div className="lg:col-span-1">
          <SchemaPreview
            schema={schema}
            onApprove={handleApprove}
            isApproved={isSchemaApproved}
            isLoading={isSaving}
          />
        </div>
      </div>

      {/* Next step CTA */}
      {isSchemaApproved && (
        <div className="flex justify-end pt-4 border-t">
          <Button
            size="lg"
            onClick={() => router.push(`/projects/${projectId}/results`)}
          >
            Continue to Results
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
