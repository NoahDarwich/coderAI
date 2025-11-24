// mocks/mockProcessingJobs.ts - Comprehensive mock processing job data
import { ProcessingJob, ProcessingLog } from '@/types/processing';

export const mockProcessingJobs: ProcessingJob[] = [
  {
    id: 'job-001',
    projectId: '550e8400-e29b-41d4-a716-446655440000',
    type: 'full',
    status: 'completed',
    progress: 100,
    totalDocuments: 15,
    processedDocuments: 15,
    startedAt: '2025-01-20T14:00:00Z',
    completedAt: '2025-01-20T14:20:00Z',
    logs: [
      {
        timestamp: '2025-01-20T14:00:00Z',
        level: 'info',
        message: 'Processing started for 15 documents',
      },
      {
        timestamp: '2025-01-20T14:01:00Z',
        level: 'info',
        message: 'Processing document: berlin_climate_protest_2023.pdf',
        documentId: 'doc-001',
      },
      {
        timestamp: '2025-01-20T14:02:00Z',
        level: 'info',
        message: 'Processing document: london_extinction_rebellion.pdf',
        documentId: 'doc-002',
      },
      {
        timestamp: '2025-01-20T14:03:00Z',
        level: 'info',
        message: 'Processing document: paris_climate_march.pdf',
        documentId: 'doc-003',
      },
      {
        timestamp: '2025-01-20T14:04:00Z',
        level: 'info',
        message: 'Processing document: madrid_youth_strike.docx',
        documentId: 'doc-004',
      },
      {
        timestamp: '2025-01-20T14:05:00Z',
        level: 'info',
        message: 'Processing document: amsterdam_climate_action.txt',
        documentId: 'doc-005',
      },
      {
        timestamp: '2025-01-20T14:20:00Z',
        level: 'info',
        message: 'Processing completed successfully. 15 of 15 documents processed.',
      },
    ],
  },
  {
    id: 'job-002',
    projectId: '661f9511-f3ac-52e5-b827-557766551111',
    type: 'full',
    status: 'processing',
    progress: 45,
    totalDocuments: 250,
    processedDocuments: 112,
    startedAt: '2025-01-22T10:00:00Z',
    logs: [
      {
        timestamp: '2025-01-22T10:00:00Z',
        level: 'info',
        message: 'Processing started for 250 documents',
      },
      {
        timestamp: '2025-01-22T10:15:00Z',
        level: 'info',
        message: 'Processed 50 documents (20%)',
      },
      {
        timestamp: '2025-01-22T10:30:00Z',
        level: 'info',
        message: 'Processed 100 documents (40%)',
      },
      {
        timestamp: '2025-01-22T10:35:00Z',
        level: 'warning',
        message: 'Low confidence extraction for document: twitter_sample_015.txt',
        documentId: 'doc-050',
      },
    ],
  },
  {
    id: 'job-003',
    projectId: '550e8400-e29b-41d4-a716-446655440000',
    type: 'sample',
    status: 'completed',
    progress: 100,
    totalDocuments: 10,
    processedDocuments: 10,
    startedAt: '2025-01-20T13:00:00Z',
    completedAt: '2025-01-20T13:10:00Z',
    logs: [
      {
        timestamp: '2025-01-20T13:00:00Z',
        level: 'info',
        message: 'Sample processing started for 10 documents',
      },
      {
        timestamp: '2025-01-20T13:10:00Z',
        level: 'info',
        message: 'Sample processing completed successfully',
      },
    ],
  },
];
