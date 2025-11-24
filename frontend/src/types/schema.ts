// types/schema.ts
export interface Schema {
  id: string;                    // UUID
  projectId: string;             // Foreign key to Project
  variables: Variable[];         // Ordered list of variables
  createdAt: string;             // ISO 8601 timestamp
  confirmedAt?: string;          // When user confirmed schema (Step 3)
}

export interface Variable {
  id: string;                    // UUID
  name: string;                  // Variable name (user-defined)
  type: VariableType;            // Data type
  instructions: string;          // Extraction instructions
  classificationRules?: string[]; // For categorical variables
  order: number;                 // Display order (0-indexed)
}

export type VariableType =
  | 'text'
  | 'number'
  | 'date'
  | 'category'
  | 'boolean';
