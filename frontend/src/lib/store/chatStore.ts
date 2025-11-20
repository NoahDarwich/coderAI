/**
 * Chat Store
 * Manages chat messages and conversation state for schema definition
 */

import { create } from 'zustand';
import { ChatMessage, SchemaVariable } from '@/lib/types/api';
import { mockConversationFlow, mockGeneratedSchema } from '@/mocks/conversations';

interface ChatState {
  messages: ChatMessage[];
  schema: SchemaVariable[];
  isTyping: boolean;
  isSchemaApproved: boolean;

  // Actions
  initializeConversation: (projectId: string) => void;
  sendMessage: (content: string) => void;
  simulateAIResponse: (response: string) => void;
  setTyping: (isTyping: boolean) => void;
  updateSchema: (variables: SchemaVariable[]) => void;
  approveSchema: () => void;
  resetConversation: () => void;
}

// TODO(Phase 2): Replace with real API calls and WebSocket for real-time AI responses
export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  schema: [],
  isTyping: false,
  isSchemaApproved: false,

  initializeConversation: (projectId: string) => {
    // For Phase 1, load mock conversation
    // TODO(Phase 2): Load from backend based on project ID
    set({
      messages: mockConversationFlow,
      schema: mockGeneratedSchema,
      isSchemaApproved: false,
    });
  },

  sendMessage: (content: string) => {
    const newMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, newMessage],
    }));

    // Simulate AI response delay
    set({ isTyping: true });

    // TODO(Phase 2): Send to backend and receive real AI response
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: 'Thank you for that information. I\'ve updated the schema based on your input. Is there anything else you\'d like to add or modify?',
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, aiResponse],
        isTyping: false,
      }));
    }, 1500);
  },

  simulateAIResponse: (response: string) => {
    const aiMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'assistant',
      content: response,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, aiMessage],
      isTyping: false,
    }));
  },

  setTyping: (isTyping: boolean) => {
    set({ isTyping });
  },

  updateSchema: (variables: SchemaVariable[]) => {
    set({ schema: variables });
  },

  approveSchema: () => {
    set({ isSchemaApproved: true });
  },

  resetConversation: () => {
    set({
      messages: [],
      schema: [],
      isTyping: false,
      isSchemaApproved: false,
    });
  },
}));
