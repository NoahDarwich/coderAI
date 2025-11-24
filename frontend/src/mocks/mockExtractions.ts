// mocks/mockExtractions.ts - Comprehensive mock extraction results
import { ExtractionResult, ExtractedValue } from '@/types/extraction';

export const mockExtractionResults: ExtractionResult[] = [
  // Berlin protest extraction
  {
    id: 'ext-001',
    projectId: '550e8400-e29b-41d4-a716-446655440000',
    documentId: 'doc-001',
    values: [
      {
        variableId: 'var-001',
        value: '2023-03-15',
        confidence: 95,
        sourceText: 'On March 15, 2023, thousands gathered...',
      },
      {
        variableId: 'var-002',
        value: 'Berlin',
        confidence: 98,
        sourceText: 'thousands gathered in Berlin for a climate protest',
      },
      {
        variableId: 'var-003',
        value: 5000,
        confidence: 78,
        sourceText: 'Estimates ranged from 3,000 to 5,000 participants',
      },
      {
        variableId: 'var-004',
        value: 'Climate Policy',
        confidence: 88,
        sourceText: 'demanding stronger climate policies',
      },
      {
        variableId: 'var-005',
        value: false,
        confidence: 99,
        sourceText: 'The demonstration remained peaceful throughout',
      },
    ],
    completedAt: '2025-01-20T14:15:00Z',
  },
  // London protest extraction
  {
    id: 'ext-002',
    projectId: '550e8400-e29b-41d4-a716-446655440000',
    documentId: 'doc-002',
    values: [
      {
        variableId: 'var-001',
        value: '2023-04-03',
        confidence: 92,
        sourceText: 'on April 3, activists blocked major roads',
      },
      {
        variableId: 'var-002',
        value: 'London',
        confidence: 96,
        sourceText: 'blocked major roads in London',
      },
      {
        variableId: 'var-003',
        value: 8000,
        confidence: 72,
        sourceText: 'approximately 8,000 protesters participated',
      },
      {
        variableId: 'var-004',
        value: 'Fossil Fuels',
        confidence: 85,
        sourceText: 'protesting against fossil fuel investments',
      },
      {
        variableId: 'var-005',
        value: true,
        confidence: 88,
        sourceText: 'minor scuffles with police were reported',
      },
    ],
    completedAt: '2025-01-20T14:16:00Z',
  },
  // Paris protest extraction
  {
    id: 'ext-003',
    projectId: '550e8400-e29b-41d4-a716-446655440000',
    documentId: 'doc-003',
    values: [
      {
        variableId: 'var-001',
        value: '2023-05-20',
        confidence: 94,
        sourceText: 'May 20, 2023 march through Paris',
      },
      {
        variableId: 'var-002',
        value: 'Paris',
        confidence: 99,
        sourceText: 'marched through Paris streets',
      },
      {
        variableId: 'var-003',
        value: 12000,
        confidence: 80,
        sourceText: 'Over 10,000 people, with some estimates as high as 12,000',
      },
      {
        variableId: 'var-004',
        value: 'Climate Policy',
        confidence: 90,
        sourceText: 'demanding climate action and policy reform',
      },
      {
        variableId: 'var-005',
        value: false,
        confidence: 95,
        sourceText: 'peaceful march concluded without incident',
      },
    ],
    completedAt: '2025-01-20T14:17:00Z',
  },
  // Additional extractions for other documents (doc-004 through doc-015)
  {
    id: 'ext-004',
    projectId: '550e8400-e29b-41d4-a716-446655440000',
    documentId: 'doc-004',
    values: [
      {
        variableId: 'var-001',
        value: '2023-06-10',
        confidence: 91,
        sourceText: 'June 10, 2023 youth climate strike',
      },
      {
        variableId: 'var-002',
        value: 'Madrid',
        confidence: 97,
        sourceText: 'Youth climate strikers in Madrid',
      },
      {
        variableId: 'var-003',
        value: 3500,
        confidence: 75,
        sourceText: 'estimated 3,500 young people',
      },
      {
        variableId: 'var-004',
        value: 'Climate Policy',
        confidence: 87,
        sourceText: 'calling for urgent climate policy changes',
      },
      {
        variableId: 'var-005',
        value: false,
        confidence: 98,
        sourceText: 'peaceful demonstration',
      },
    ],
    completedAt: '2025-01-20T14:18:00Z',
  },
  {
    id: 'ext-005',
    projectId: '550e8400-e29b-41d4-a716-446655440000',
    documentId: 'doc-005',
    values: [
      {
        variableId: 'var-001',
        value: '2023-05-12',
        confidence: 93,
        sourceText: 'largest climate protest on May 12, 2023',
      },
      {
        variableId: 'var-002',
        value: 'Amsterdam',
        confidence: 99,
        sourceText: 'Amsterdam saw its largest climate protest',
      },
      {
        variableId: 'var-003',
        value: 15000,
        confidence: 82,
        sourceText: 'more than 15,000 participants',
      },
      {
        variableId: 'var-004',
        value: 'Deforestation',
        confidence: 86,
        sourceText: 'protesting deforestation and biodiversity loss',
      },
      {
        variableId: 'var-005',
        value: false,
        confidence: 96,
        sourceText: 'remained peaceful and orderly',
      },
    ],
    completedAt: '2025-01-20T14:19:00Z',
  },
];
