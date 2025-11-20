/**
 * useChat Hook
 * Custom hook for managing chat interactions
 */

import { useEffect, useCallback } from 'react';
import { useChatStore } from '@/lib/store/chatStore';
import { useSchema, useSaveSchema } from '@/lib/api/schema';
import { toast } from 'sonner';

export function useChat(projectId: string) {
  const {
    messages,
    schema,
    isTyping,
    isSchemaApproved,
    initializeConversation,
    sendMessage,
    setTyping,
    approveSchema,
  } = useChatStore();

  const { data: savedSchema, isLoading } = useSchema(projectId);
  const saveSchemaMutation = useSaveSchema(projectId);

  // Initialize conversation on mount
  useEffect(() => {
    if (savedSchema) {
      // Load existing conversation
      useChatStore.setState({
        messages: savedSchema.conversationHistory || [],
        schema: savedSchema.variables || [],
      });
    } else {
      // Start new conversation
      initializeConversation(projectId);
    }
  }, [projectId, savedSchema, initializeConversation]);

  /**
   * Send a message to the chat
   */
  const handleSendMessage = useCallback(
    (content: string) => {
      if (!content.trim()) return;

      sendMessage(content);
    },
    [sendMessage]
  );

  /**
   * Save the current schema
   */
  const handleSaveSchema = useCallback(async () => {
    try {
      // Build prompts object from schema variables
      const prompts = schema.reduce((acc, variable) => {
        acc[variable.name] = variable.prompt || '';
        return acc;
      }, {} as Record<string, string>);

      await saveSchemaMutation.mutateAsync({
        conversationHistory: messages,
        variables: schema,
        prompts,
      });

      toast.success('Schema saved successfully');
    } catch (error) {
      toast.error('Failed to save schema');
    }
  }, [messages, schema, saveSchemaMutation]);

  /**
   * Approve and finalize the schema
   */
  const handleApproveSchema = useCallback(async () => {
    try {
      await handleSaveSchema();
      approveSchema();
      toast.success('Schema approved! Ready to process documents.');
    } catch (error) {
      toast.error('Failed to approve schema');
    }
  }, [handleSaveSchema, approveSchema]);

  return {
    messages,
    schema,
    isTyping,
    isSchemaApproved,
    isLoading,
    sendMessage: handleSendMessage,
    saveSchema: handleSaveSchema,
    approveSchema: handleApproveSchema,
    isSaving: saveSchemaMutation.isPending,
  };
}
