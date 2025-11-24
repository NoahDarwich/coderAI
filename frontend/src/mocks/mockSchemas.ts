// mocks/mockSchemas.ts - Comprehensive mock schema data
import { Schema, Variable } from '@/types/schema';

export const mockSchemas: Schema[] = [
  {
    id: 'schema-001',
    projectId: '550e8400-e29b-41d4-a716-446655440000',
    variables: [
      {
        id: 'var-001',
        name: 'Date of Protest',
        type: 'date',
        instructions: 'Extract the date when the protest occurred. Look for explicit dates in the text.',
        order: 0,
      },
      {
        id: 'var-002',
        name: 'Location',
        type: 'text',
        instructions: 'Extract the city or location where the protest took place.',
        order: 1,
      },
      {
        id: 'var-003',
        name: 'Number of Participants',
        type: 'number',
        instructions: 'Extract the estimated number of protesters. Use the highest estimate if multiple are given.',
        order: 2,
      },
      {
        id: 'var-004',
        name: 'Protest Topic',
        type: 'category',
        instructions: 'Classify the main topic of the protest.',
        classificationRules: ['Climate Policy', 'Fossil Fuels', 'Deforestation', 'Other'],
        order: 3,
      },
      {
        id: 'var-005',
        name: 'Violence Occurred',
        type: 'boolean',
        instructions: 'Did violence occur during the protest? Answer true or false.',
        order: 4,
      },
    ],
    createdAt: '2025-01-20T11:00:00Z',
    confirmedAt: '2025-01-20T11:30:00Z',
  },
  {
    id: 'schema-002',
    projectId: '661f9511-f3ac-52e5-b827-557766551111',
    variables: [
      {
        id: 'var-006',
        name: 'Post Date',
        type: 'date',
        instructions: 'Extract the date when the post was published.',
        order: 0,
      },
      {
        id: 'var-007',
        name: 'Sentiment',
        type: 'category',
        instructions: 'Classify the sentiment of the post.',
        classificationRules: ['Positive', 'Neutral', 'Negative'],
        order: 1,
      },
      {
        id: 'var-008',
        name: 'Topic',
        type: 'text',
        instructions: 'Extract the main topic or subject of the post.',
        order: 2,
      },
    ],
    createdAt: '2025-01-15T09:00:00Z',
    confirmedAt: '2025-01-15T09:30:00Z',
  },
];
