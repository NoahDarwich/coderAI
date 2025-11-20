/**
 * Project-related types and utilities
 */

import { Project } from './api';

/**
 * Project Status Badge Props
 */
export interface ProjectStatusBadgeProps {
  status: Project['status'];
}

/**
 * Project Creation Form Data
 */
export interface CreateProjectData {
  name: string;
  description: string;
}

/**
 * Project Update Form Data
 */
export interface UpdateProjectData {
  name?: string;
  description?: string;
}

/**
 * Project Filter Options
 */
export interface ProjectFilterOptions {
  status?: Project['status'][];
  search?: string;
  sortBy?: 'name' | 'createdAt' | 'updatedAt' | 'documentCount';
  sortOrder?: 'asc' | 'desc';
}

/**
 * Project Stats
 */
export interface ProjectStats {
  totalDocuments: number;
  processedDocuments: number;
  extractedResults: number;
  averageConfidence: number;
  flaggedResults: number;
}

/**
 * Project with Stats
 */
export interface ProjectWithStats extends Project {
  stats?: ProjectStats;
}
