/**
 * Export Utilities
 * CSV generation and download functionality
 */

import { ExtractionResult, ExportConfig } from '../types/api';
import { CSVExportRowWide, CSVExportRowLong } from '../types/extraction';

/**
 * Convert array of objects to CSV string
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function objectsToCSV(objects: Record<string, any>[]): string {
  if (objects.length === 0) {
    return '';
  }

  // Get headers from first object
  const headers = Object.keys(objects[0]);

  // Create CSV header row
  const headerRow = headers.map(escapeCSVValue).join(',');

  // Create CSV data rows
  const dataRows = objects.map(obj =>
    headers.map(header => escapeCSVValue(obj[header] ?? '')).join(',')
  );

  return [headerRow, ...dataRows].join('\n');
}

/**
 * Escape CSV value (handle commas, quotes, newlines)
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function escapeCSVValue(value: any): string {
  if (value === null || value === undefined) {
    return '';
  }

  const stringValue = String(value);

  // If value contains comma, quote, or newline, wrap in quotes and escape quotes
  if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
    return `"${stringValue.replace(/"/g, '""')}"`;
  }

  return stringValue;
}

/**
 * Convert extraction results to CSV (Wide format)
 * One row per document with all variables as columns
 */
export function extractionResultsToCSVWide(
  results: ExtractionResult[],
  config: ExportConfig
): string {
  const rows: CSVExportRowWide[] = results.map(result => {
    const row: CSVExportRowWide = {
      document_name: result.documentName,
    };

    // Add each variable as a column
    Object.entries(result.data).forEach(([variableName, dataPoint]) => {
      const cleanVarName = variableName.replace(/[^a-zA-Z0-9_]/g, '_');

      row[cleanVarName] = dataPoint.value ?? '';

      if (config.includeConfidence) {
        row[`${cleanVarName}_confidence`] = dataPoint.confidence;
      }

      if (config.includeSourceText && dataPoint.sourceText) {
        row[`${cleanVarName}_source`] = dataPoint.sourceText;
      }
    });

    if (config.includeFlags) {
      row['flagged'] = result.flagged ? 'Yes' : 'No';
    }

    return row;
  });

  return objectsToCSV(rows);
}

/**
 * Convert extraction results to CSV (Long format)
 * One row per extracted variable
 */
export function extractionResultsToCSVLong(
  results: ExtractionResult[],
  config: ExportConfig
): string {
  const rows: CSVExportRowLong[] = [];

  results.forEach(result => {
    Object.entries(result.data).forEach(([variableName, dataPoint]) => {
      const row: CSVExportRowLong = {
        document_name: result.documentName,
        variable_name: variableName,
        value: dataPoint.value ?? '',
        confidence: dataPoint.confidence,
      };

      if (config.includeSourceText && dataPoint.sourceText) {
        row.source_text = dataPoint.sourceText;
      }

      rows.push(row);
    });
  });

  return objectsToCSV(rows);
}

/**
 * Filter extraction results based on export config
 */
export function filterExtractionResults(
  results: ExtractionResult[],
  config: ExportConfig
): ExtractionResult[] {
  let filtered = [...results];

  // Filter by minimum confidence
  if (config.minConfidenceThreshold !== undefined) {
    filtered = filtered.filter(result => {
      const avgConfidence = Object.values(result.data)
        .reduce((sum, dp) => sum + dp.confidence, 0) / Object.keys(result.data).length;
      return avgConfidence >= config.minConfidenceThreshold!;
    });
  }

  // Filter flagged only
  if (config.flaggedOnly) {
    filtered = filtered.filter(result => result.flagged);
  }

  return filtered;
}

/**
 * Export extraction results to CSV file
 */
export function exportExtractionResults(
  results: ExtractionResult[],
  config: ExportConfig,
  filename: string = 'extraction_results.csv'
): void {
  // Filter results
  const filteredResults = filterExtractionResults(results, config);

  if (filteredResults.length === 0) {
    throw new Error('No results to export after applying filters');
  }

  // Generate CSV
  const csv = (config.format === 'CSV_WIDE' || config.format === 'wide' as any)
    ? extractionResultsToCSVWide(filteredResults, config)
    : extractionResultsToCSVLong(filteredResults, config);

  // Trigger download
  downloadCSV(csv, filename);
}

/**
 * Trigger browser download of CSV file
 */
export function downloadCSV(csvContent: string, filename: string): void {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');

  if (link.download !== undefined) {
    // Create download link
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up
    URL.revokeObjectURL(url);
  } else {
    // Fallback for older browsers
    window.open(
      'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent),
      '_blank'
    );
  }
}

/**
 * Estimate CSV file size
 */
export function estimateCSVSize(
  results: ExtractionResult[],
  config: ExportConfig
): string {
  const filteredResults = filterExtractionResults(results, config);
  const csv = (config.format === 'CSV_WIDE' || config.format === 'wide' as any)
    ? extractionResultsToCSVWide(filteredResults, config)
    : extractionResultsToCSVLong(filteredResults, config);

  const bytes = new Blob([csv]).size;

  // Format file size
  const kb = bytes / 1024;
  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`;
  }

  const mb = kb / 1024;
  return `${mb.toFixed(1)} MB`;
}
