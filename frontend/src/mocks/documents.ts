/**
 * Mock Document Data
 * Sample documents for Phase 1 development
 */

import { Document } from '@/lib/types/api';

export const mockDocuments: Document[] = [
  // Climate Protests project documents
  {
    id: 'doc-001',
    projectId: 'proj-001',
    filename: 'london_climate_protest_jan2023.pdf',
    fileType: 'pdf',
    fileSize: 2457600, // 2.4 MB
    status: 'completed',
    uploadedAt: '2024-01-15T11:00:00Z',
  },
  {
    id: 'doc-002',
    projectId: 'proj-001',
    filename: 'berlin_extinction_rebellion_march.pdf',
    fileType: 'pdf',
    fileSize: 1843200, // 1.8 MB
    status: 'completed',
    uploadedAt: '2024-01-15T11:05:00Z',
  },
  {
    id: 'doc-003',
    projectId: 'proj-001',
    filename: 'paris_climate_strike_report.docx',
    fileType: 'docx',
    fileSize: 987654,
    status: 'completed',
    uploadedAt: '2024-01-15T11:10:00Z',
  },
  {
    id: 'doc-004',
    projectId: 'proj-001',
    filename: 'madrid_protest_notes.txt',
    fileType: 'txt',
    fileSize: 45678,
    status: 'completed',
    uploadedAt: '2024-01-15T11:15:00Z',
  },
  {
    id: 'doc-005',
    projectId: 'proj-001',
    filename: 'amsterdam_climate_action.pdf',
    fileType: 'pdf',
    fileSize: 3145728, // 3 MB
    status: 'completed',
    uploadedAt: '2024-01-15T11:20:00Z',
  },

  // Healthcare Policy project documents
  {
    id: 'doc-006',
    projectId: 'proj-002',
    filename: 'healthcare_reform_2023.pdf',
    fileType: 'pdf',
    fileSize: 5242880, // 5 MB
    status: 'processing',
    uploadedAt: '2024-02-01T09:30:00Z',
  },
  {
    id: 'doc-007',
    projectId: 'proj-002',
    filename: 'medicare_expansion_bill.docx',
    fileType: 'docx',
    fileSize: 2097152, // 2 MB
    status: 'completed',
    uploadedAt: '2024-02-01T09:35:00Z',
  },
  {
    id: 'doc-008',
    projectId: 'proj-002',
    filename: 'insurance_regulations_update.pdf',
    fileType: 'pdf',
    fileSize: 3670016, // 3.5 MB
    status: 'completed',
    uploadedAt: '2024-02-01T09:40:00Z',
  },

  // Corporate Earnings project documents
  {
    id: 'doc-009',
    projectId: 'proj-003',
    filename: 'q4_2023_earnings_transcript.pdf',
    fileType: 'pdf',
    fileSize: 1572864, // 1.5 MB
    status: 'uploaded',
    uploadedAt: '2024-02-10T11:20:00Z',
  },
  {
    id: 'doc-010',
    projectId: 'proj-003',
    filename: 'annual_report_2023.pdf',
    fileType: 'pdf',
    fileSize: 8388608, // 8 MB
    status: 'uploaded',
    uploadedAt: '2024-02-10T11:25:00Z',
  },

  // Legal Cases project documents
  {
    id: 'doc-011',
    projectId: 'proj-004',
    filename: 'case_123_decision.pdf',
    fileType: 'pdf',
    fileSize: 1048576, // 1 MB
    status: 'completed',
    uploadedAt: '2023-12-01T08:30:00Z',
  },
  {
    id: 'doc-012',
    projectId: 'proj-004',
    filename: 'case_456_appeal_outcome.pdf',
    fileType: 'pdf',
    fileSize: 892000,
    status: 'completed',
    uploadedAt: '2023-12-01T08:35:00Z',
  },

  // Social Media project documents (with error)
  {
    id: 'doc-013',
    projectId: 'proj-005',
    filename: 'twitter_dataset.txt',
    fileType: 'txt',
    fileSize: 524288, // 512 KB
    status: 'error',
    errorMessage: 'File parsing failed: invalid encoding',
    uploadedAt: '2024-02-12T13:10:00Z',
  },
];

/**
 * Get documents for a project
 */
export function getMockDocumentsByProjectId(projectId: string): Document[] {
  return mockDocuments.filter(d => d.projectId === projectId);
}

/**
 * Get document by ID
 */
export function getMockDocumentById(id: string): Document | undefined {
  return mockDocuments.find(d => d.id === id);
}

/**
 * Upload document (mock)
 */
export function uploadMockDocument(projectId: string, file: { name: string; size: number; type: string }): Document {
  const fileTypeMap: Record<string, 'pdf' | 'docx' | 'txt'> = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'text/plain': 'txt',
  };

  const newDocument: Document = {
    id: `doc-${Date.now()}`,
    projectId,
    filename: file.name,
    fileType: fileTypeMap[file.type] || 'pdf',
    fileSize: file.size,
    status: 'uploaded',
    uploadedAt: new Date().toISOString(),
  };

  mockDocuments.push(newDocument);
  return newDocument;
}

/**
 * Delete document (mock)
 */
export function deleteMockDocument(id: string): boolean {
  const index = mockDocuments.findIndex(d => d.id === id);
  if (index !== -1) {
    mockDocuments.splice(index, 1);
    return true;
  }
  return false;
}
