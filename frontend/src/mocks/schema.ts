/**
 * Mock Schema Data
 * Sample extraction schemas
 */

import { SchemaConfig } from '@/lib/types/api';
import { mockConversationFlow, mockGeneratedSchema } from './conversations';

export const mockSchemas: SchemaConfig[] = [
  {
    id: 'schema-001',
    projectId: 'proj-001',
    conversationHistory: mockConversationFlow,
    variables: mockGeneratedSchema,
    prompts: {
      protest_date: 'Extract the date of the protest event from the document. Format as YYYY-MM-DD.',
      city: 'Extract the city name where the protest occurred.',
      country: 'Extract the country where the protest occurred.',
      participant_count: 'Extract the number of participants mentioned in the document. If a range is given, use the midpoint.',
      protest_topic: 'Classify the main topic of the protest into one of these categories: Climate policy, Fossil fuels, Deforestation, General environmental issues, Other.',
      violence_occurred: 'Determine if violence occurred during the protest. Violence includes physical confrontation or property damage. Answer Yes or No.',
      police_response: 'Classify the police response into one of these categories: None, Observation only, Crowd control, Arrests made, Force used.',
    },
    version: 1,
    createdAt: '2024-01-15T10:08:00Z',
    updatedAt: '2024-01-15T10:08:00Z',
  },
];

/**
 * Get schema for a project
 */
export function getMockSchemaByProjectId(projectId: string): SchemaConfig | undefined {
  return mockSchemas.find(s => s.projectId === projectId);
}

/**
 * Create or update schema (mock)
 */
export function saveMockSchema(projectId: string, data: Partial<SchemaConfig>): SchemaConfig {
  const existingIndex = mockSchemas.findIndex(s => s.projectId === projectId);

  if (existingIndex !== -1) {
    // Update existing
    mockSchemas[existingIndex] = {
      ...mockSchemas[existingIndex],
      ...data,
      updatedAt: new Date().toISOString(),
    };
    return mockSchemas[existingIndex];
  } else {
    // Create new
    const newSchema: SchemaConfig = {
      id: `schema-${Date.now()}`,
      projectId,
      conversationHistory: data.conversationHistory || [],
      variables: data.variables || [],
      prompts: data.prompts || {},
      version: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    mockSchemas.push(newSchema);
    return newSchema;
  }
}
