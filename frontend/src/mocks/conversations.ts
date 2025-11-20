/**
 * Mock Conversation Data
 * Predefined chat flows for schema definition
 */

import { ChatMessage, SchemaVariable } from '@/lib/types/api';

/**
 * Sample conversation flow for climate protests project
 */
export const mockConversationFlow: ChatMessage[] = [
  {
    id: 'msg-001',
    role: 'assistant',
    content: 'Hello! I\'m here to help you define your extraction schema. Let\'s start by understanding your research. **What is your research project about?**',
    timestamp: '2024-01-15T10:00:00Z',
  },
  {
    id: 'msg-002',
    role: 'user',
    content: 'I\'m studying climate protests in Europe from 2020 to 2023.',
    timestamp: '2024-01-15T10:01:30Z',
  },
  {
    id: 'msg-003',
    role: 'assistant',
    content: 'Great! Climate protests in Europe is an interesting research area. **What specific information do you need to extract from your documents?** For example, dates, locations, participants, outcomes, etc.',
    timestamp: '2024-01-15T10:01:32Z',
  },
  {
    id: 'msg-004',
    role: 'user',
    content: 'I need to extract:\n- Date of protest\n- Location (city and country)\n- Number of participants\n- What they were protesting about\n- Whether there was any violence\n- Police response',
    timestamp: '2024-01-15T10:03:00Z',
  },
  {
    id: 'msg-005',
    role: 'assistant',
    content: 'Perfect! I can help you extract all of that. Let\'s define each variable more clearly. **For "what they were protesting about", how would you like me to classify this?** For example, you could have categories like: Climate policy, Fossil fuels, Deforestation, etc.',
    timestamp: '2024-01-15T10:03:02Z',
  },
  {
    id: 'msg-006',
    role: 'user',
    content: 'Categories should be: Climate policy, Fossil fuels, Deforestation, General environmental issues, Other',
    timestamp: '2024-01-15T10:04:15Z',
  },
  {
    id: 'msg-007',
    role: 'assistant',
    content: 'Excellent! Now for **"violence"** - how should I classify this? Do you want a simple Yes/No, or more detailed categories?',
    timestamp: '2024-01-15T10:04:17Z',
  },
  {
    id: 'msg-008',
    role: 'user',
    content: 'Yes/No is fine. Violence means physical confrontation or property damage.',
    timestamp: '2024-01-15T10:05:00Z',
  },
  {
    id: 'msg-009',
    role: 'assistant',
    content: 'Got it! And for **"police response"**, what categories would you like?',
    timestamp: '2024-01-15T10:05:02Z',
  },
  {
    id: 'msg-010',
    role: 'user',
    content: 'Categories: None, Observation only, Crowd control, Arrests made, Force used',
    timestamp: '2024-01-15T10:06:00Z',
  },
  {
    id: 'msg-011',
    role: 'assistant',
    content: 'Perfect! I\'ve generated your extraction schema. Here\'s what I\'ll extract from each document:\n\n**Variables:**\n- **Protest Date** (Date)\n- **City** (Location)\n- **Country** (Location)\n- **Participant Count** (Number)\n- **Protest Topic** (Classification: Climate policy, Fossil fuels, Deforestation, General environmental issues, Other)\n- **Violence Occurred** (Classification: Yes, No)\n- **Police Response** (Classification: None, Observation only, Crowd control, Arrests made, Force used)\n\nWould you like to test this on a sample of your documents?',
    timestamp: '2024-01-15T10:06:02Z',
  },
  {
    id: 'msg-012',
    role: 'user',
    content: 'Yes, let\'s test it on 10 documents first.',
    timestamp: '2024-01-15T10:07:00Z',
  },
];

/**
 * Generated schema from conversation
 */
export const mockGeneratedSchema: SchemaVariable[] = [
  {
    id: 'var-001',
    name: 'protest_date',
    type: 'date',
    description: 'The date when the protest occurred',
    prompt: 'Extract the date of the protest event from the document. Format as YYYY-MM-DD.',
  },
  {
    id: 'var-002',
    name: 'city',
    type: 'location',
    description: 'The city where the protest took place',
    prompt: 'Extract the city name where the protest occurred.',
  },
  {
    id: 'var-003',
    name: 'country',
    type: 'location',
    description: 'The country where the protest took place',
    prompt: 'Extract the country where the protest occurred.',
  },
  {
    id: 'var-004',
    name: 'participant_count',
    type: 'custom',
    description: 'Estimated number of participants in the protest',
    prompt: 'Extract the number of participants mentioned in the document. If a range is given, use the midpoint. If "thousands" is mentioned, estimate based on context.',
  },
  {
    id: 'var-005',
    name: 'protest_topic',
    type: 'classification',
    description: 'The main topic of the protest',
    prompt: 'Classify the main topic of the protest into one of these categories: Climate policy, Fossil fuels, Deforestation, General environmental issues, Other.',
    categories: ['Climate policy', 'Fossil fuels', 'Deforestation', 'General environmental issues', 'Other'],
  },
  {
    id: 'var-006',
    name: 'violence_occurred',
    type: 'classification',
    description: 'Whether violence occurred during the protest (physical confrontation or property damage)',
    prompt: 'Determine if violence occurred during the protest. Violence includes physical confrontation or property damage. Answer Yes or No.',
    categories: ['Yes', 'No'],
  },
  {
    id: 'var-007',
    name: 'police_response',
    type: 'classification',
    description: 'The level of police response to the protest',
    prompt: 'Classify the police response into one of these categories: None, Observation only, Crowd control, Arrests made, Force used.',
    categories: ['None', 'Observation only', 'Crowd control', 'Arrests made', 'Force used'],
  },
];

/**
 * Get mock conversation by project ID
 */
export function getMockConversation(projectId: string): ChatMessage[] {
  // For now, return the same conversation for all projects
  // In a real app, this would be stored per project
  return mockConversationFlow;
}

/**
 * Add message to conversation (mock)
 */
export function addMockMessage(message: string): ChatMessage {
  const newMessage: ChatMessage = {
    id: `msg-${Date.now()}`,
    role: 'user',
    content: message,
    timestamp: new Date().toISOString(),
  };

  // In a real app, this would trigger AI response
  // For mock, we could add a simulated AI response

  return newMessage;
}
