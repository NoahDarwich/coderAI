/**
 * Mock Project Data
 * Sample projects for Phase 1 development
 */

import { Project } from '@/lib/types/api';

export const mockProjects: Project[] = [
  {
    id: 'proj-001',
    userId: 'user-001',
    name: 'Climate Protests in Europe',
    description: 'Analyzing climate protest events across European countries from 2020-2023. Extracting dates, locations, participant counts, and protest outcomes.',
    status: 'completed',
    documentCount: 45,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-20T14:45:00Z',
  },
  {
    id: 'proj-002',
    userId: 'user-001',
    name: 'Healthcare Policy Analysis',
    description: 'Extracting policy decisions, implementation dates, and impact metrics from healthcare legislation documents.',
    status: 'processing',
    documentCount: 28,
    createdAt: '2024-02-01T09:00:00Z',
    updatedAt: '2024-02-05T16:20:00Z',
  },
  {
    id: 'proj-003',
    userId: 'user-001',
    name: 'Corporate Earnings Reports',
    description: 'Analyzing quarterly earnings reports to extract revenue figures, profit margins, and forward guidance statements.',
    status: 'draft',
    documentCount: 12,
    createdAt: '2024-02-10T11:15:00Z',
    updatedAt: '2024-02-10T11:15:00Z',
  },
  {
    id: 'proj-004',
    userId: 'user-001',
    name: 'Legal Case Outcomes',
    description: 'Extracting case decisions, sentencing information, and legal precedents from court documents.',
    status: 'completed',
    documentCount: 67,
    createdAt: '2023-12-01T08:00:00Z',
    updatedAt: '2023-12-15T17:30:00Z',
  },
  {
    id: 'proj-005',
    userId: 'user-001',
    name: 'Social Media Sentiment',
    description: 'Analyzing social media posts to extract sentiment, topics, and engagement metrics.',
    status: 'error',
    documentCount: 8,
    createdAt: '2024-02-12T13:00:00Z',
    updatedAt: '2024-02-12T14:30:00Z',
  },
];

/**
 * Get all projects
 */
export function getMockProjects(): Project[] {
  return mockProjects;
}

/**
 * Get project by ID
 */
export function getMockProjectById(id: string): Project | undefined {
  return mockProjects.find(p => p.id === id);
}

/**
 * Create new project (mock)
 */
export function createMockProject(data: { name: string; description: string }): Project {
  const newProject: Project = {
    id: `proj-${Date.now()}`,
    userId: 'user-001',
    name: data.name,
    description: data.description,
    status: 'draft',
    documentCount: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  mockProjects.push(newProject);
  return newProject;
}

/**
 * Delete project (mock)
 */
export function deleteMockProject(id: string): boolean {
  const index = mockProjects.findIndex(p => p.id === id);
  if (index !== -1) {
    mockProjects.splice(index, 1);
    return true;
  }
  return false;
}
