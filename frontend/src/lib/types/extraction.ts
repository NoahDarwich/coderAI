/**
 * Extraction-related types and utilities
 */

import { ExtractionResult, ExtractionDataPoint } from './api';

/**
 * Confidence Level Categories
 */
export type ConfidenceLevel = 'high' | 'medium' | 'low';

/**
 * Get confidence level from score
 */
export function getConfidenceLevel(confidence: number): ConfidenceLevel {
  if (confidence >= 90) return 'high';
  if (confidence >= 70) return 'medium';
  return 'low';
}

/**
 * Confidence Level Colors (for badges/indicators)
 */
export const CONFIDENCE_COLORS: Record<ConfidenceLevel, string> = {
  high: 'bg-green-100 text-green-800 border-green-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  low: 'bg-red-100 text-red-800 border-red-200',
};

/**
 * Confidence Level Colors (dark mode)
 */
export const CONFIDENCE_COLORS_DARK: Record<ConfidenceLevel, string> = {
  high: 'dark:bg-green-900 dark:text-green-100 dark:border-green-800',
  medium: 'dark:bg-yellow-900 dark:text-yellow-100 dark:border-yellow-800',
  low: 'dark:bg-red-900 dark:text-red-100 dark:border-red-800',
};

/**
 * Extraction Table Row
 */
export interface ExtractionTableRow {
  id: string;
  documentName: string;
  [key: string]: string | number | boolean | ExtractionDataPoint;
}

/**
 * Extraction Filter Options
 */
export interface ExtractionFilterOptions {
  minConfidence?: number;
  maxConfidence?: number;
  flaggedOnly?: boolean;
  search?: string;
  sortBy?: string; // Can be any variable name
  sortOrder?: 'asc' | 'desc';
}

/**
 * Extraction Column Definition
 */
export interface ExtractionColumn {
  id: string;
  header: string;
  accessorKey: string;
  type: 'string' | 'number' | 'date' | 'confidence';
  sortable: boolean;
}

/**
 * Extraction Result with Calculated Fields
 */
export interface EnrichedExtractionResult extends ExtractionResult {
  averageConfidence: number;
  lowestConfidence: number;
  highestConfidence: number;
  confidenceLevel: ConfidenceLevel;
}

/**
 * Enrich extraction result with calculated fields
 */
export function enrichExtractionResult(result: ExtractionResult): EnrichedExtractionResult {
  const confidences = Object.values(result.data)
    .map(d => d.confidence)
    .filter(c => c !== null && c !== undefined);

  const averageConfidence = confidences.length > 0
    ? confidences.reduce((sum, c) => sum + c, 0) / confidences.length
    : 0;

  const lowestConfidence = confidences.length > 0 ? Math.min(...confidences) : 0;
  const highestConfidence = confidences.length > 0 ? Math.max(...confidences) : 0;

  return {
    ...result,
    averageConfidence,
    lowestConfidence,
    highestConfidence,
    confidenceLevel: getConfidenceLevel(averageConfidence),
  };
}

/**
 * CSV Export Row (Wide Format)
 */
export interface CSVExportRowWide {
  document_name: string;
  [variableName: string]: string | number;
}

/**
 * CSV Export Row (Long Format)
 */
export interface CSVExportRowLong {
  document_name: string;
  variable_name: string;
  value: string | number;
  confidence: number;
  source_text?: string;
}
