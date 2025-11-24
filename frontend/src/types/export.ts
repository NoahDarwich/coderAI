// types/export.ts
export interface ExportConfig {
  format: ExportFormat;          // CSV only (Phase 1)
  structure: ExportStructure;    // Wide or long
  includeConfidence: boolean;    // Include confidence scores?
  includeSourceText: boolean;    // Include source text spans?
  minConfidence?: number;        // Filter by minimum confidence (0-100)
}

export type ExportFormat = 'csv';  // Phase 2: 'excel' | 'json'

export type ExportStructure =
  | 'wide'   // One row per document (columns = variables)
  | 'long';  // One row per extracted value

export interface ExportResult {
  id: string;
  fileName: string;
  fileSize: number;
  createdAt: string;
  downloadUrl?: string;          // Available in Phase 1 (blob URL)
}
