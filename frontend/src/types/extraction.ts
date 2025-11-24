// types/extraction.ts
export interface ExtractionResult {
  id: string;                    // UUID
  projectId: string;             // Foreign key to Project
  documentId: string;            // Foreign key to Document
  values: ExtractedValue[];      // One per variable
  completedAt: string;           // ISO 8601 timestamp
}

export interface ExtractedValue {
  variableId: string;            // Foreign key to Variable
  value: string | number | boolean | null; // Extracted value
  confidence: number;            // 0-100 confidence score
  sourceText?: string;           // Text span that generated this value
}

export type ConfidenceLevel = 'high' | 'medium' | 'low';

export function getConfidenceLevel(score: number): ConfidenceLevel {
  if (score >= 85) return 'high';   // 🟢
  if (score >= 70) return 'medium'; // 🟡
  return 'low';                      // 🔴
}
