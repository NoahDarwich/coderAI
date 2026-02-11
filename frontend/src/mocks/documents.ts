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
    name: 'london_climate_protest_jan2023.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 2457600,
    sizeBytes: 2457600,
    status: 'completed',
    uploadedAt: '2024-01-15T11:00:00Z',
  },
  {
    id: 'doc-002',
    projectId: 'proj-001',
    filename: 'berlin_extinction_rebellion_march.pdf',
    name: 'berlin_extinction_rebellion_march.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 1843200,
    sizeBytes: 1843200,
    status: 'completed',
    uploadedAt: '2024-01-15T11:05:00Z',
  },
  {
    id: 'doc-003',
    projectId: 'proj-001',
    filename: 'paris_climate_strike_report.docx',
    name: 'paris_climate_strike_report.docx',
    fileType: 'docx',
    contentType: 'docx',
    fileSize: 987654,
    sizeBytes: 987654,
    status: 'completed',
    uploadedAt: '2024-01-15T11:10:00Z',
  },
  {
    id: 'doc-004',
    projectId: 'proj-001',
    filename: 'madrid_protest_notes.txt',
    name: 'madrid_protest_notes.txt',
    fileType: 'txt',
    contentType: 'txt',
    fileSize: 45678,
    sizeBytes: 45678,
    status: 'completed',
    uploadedAt: '2024-01-15T11:15:00Z',
  },
  {
    id: 'doc-005',
    projectId: 'proj-001',
    filename: 'amsterdam_climate_action.pdf',
    name: 'amsterdam_climate_action.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 3145728,
    sizeBytes: 3145728,
    status: 'completed',
    uploadedAt: '2024-01-15T11:20:00Z',
  },

  // Healthcare Policy project documents
  {
    id: 'doc-006',
    projectId: 'proj-002',
    filename: 'healthcare_reform_2023.pdf',
    name: 'healthcare_reform_2023.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 5242880,
    sizeBytes: 5242880,
    status: 'processing',
    uploadedAt: '2024-02-01T09:30:00Z',
  },
  {
    id: 'doc-007',
    projectId: 'proj-002',
    filename: 'medicare_expansion_bill.docx',
    name: 'medicare_expansion_bill.docx',
    fileType: 'docx',
    contentType: 'docx',
    fileSize: 2097152,
    sizeBytes: 2097152,
    status: 'completed',
    uploadedAt: '2024-02-01T09:35:00Z',
  },
  {
    id: 'doc-008',
    projectId: 'proj-002',
    filename: 'insurance_regulations_update.pdf',
    name: 'insurance_regulations_update.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 3670016,
    sizeBytes: 3670016,
    status: 'completed',
    uploadedAt: '2024-02-01T09:40:00Z',
  },

  // Corporate Earnings project documents
  {
    id: 'doc-009',
    projectId: 'proj-003',
    filename: 'q4_2023_earnings_transcript.pdf',
    name: 'q4_2023_earnings_transcript.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 1572864,
    sizeBytes: 1572864,
    status: 'uploaded',
    uploadedAt: '2024-02-10T11:20:00Z',
  },
  {
    id: 'doc-010',
    projectId: 'proj-003',
    filename: 'annual_report_2023.pdf',
    name: 'annual_report_2023.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 8388608,
    sizeBytes: 8388608,
    status: 'uploaded',
    uploadedAt: '2024-02-10T11:25:00Z',
  },

  // Legal Cases project documents
  {
    id: 'doc-011',
    projectId: 'proj-004',
    filename: 'case_123_decision.pdf',
    name: 'case_123_decision.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 1048576,
    sizeBytes: 1048576,
    status: 'completed',
    uploadedAt: '2023-12-01T08:30:00Z',
  },
  {
    id: 'doc-012',
    projectId: 'proj-004',
    filename: 'case_456_appeal_outcome.pdf',
    name: 'case_456_appeal_outcome.pdf',
    fileType: 'pdf',
    contentType: 'pdf',
    fileSize: 892000,
    sizeBytes: 892000,
    status: 'completed',
    uploadedAt: '2023-12-01T08:35:00Z',
  },

  // Social Media project documents (with error)
  {
    id: 'doc-013',
    projectId: 'proj-005',
    filename: 'twitter_dataset.txt',
    name: 'twitter_dataset.txt',
    fileType: 'txt',
    contentType: 'txt',
    fileSize: 524288,
    sizeBytes: 524288,
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
  const fileTypeMap: Record<string, Document['fileType']> = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'text/plain': 'txt',
    'text/html': 'html',
  };

  const ft = fileTypeMap[file.type] || 'pdf';
  const newDocument: Document = {
    id: `doc-${Date.now()}`,
    projectId,
    filename: file.name,
    name: file.name,
    fileType: ft,
    contentType: ft,
    fileSize: file.size,
    sizeBytes: file.size,
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
