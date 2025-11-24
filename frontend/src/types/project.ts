// types/project.ts
export interface Project {
  id: string;                    // UUID
  name: string;                  // User-defined project name
  scale: 'small' | 'large';      // Project scale
  createdAt: string;             // ISO 8601 timestamp
  updatedAt: string;             // ISO 8601 timestamp
  status: ProjectStatus;         // Current workflow step
  documentCount: number;         // Number of uploaded documents
  schemaComplete: boolean;       // Has schema been confirmed?
  processingComplete: boolean;   // Has processing finished?
}

export type ProjectStatus =
  | 'setup'           // Step 1: Document upload
  | 'schema'          // Step 2: Schema definition
  | 'review'          // Step 3: Schema review
  | 'processing'      // Step 4: Processing
  | 'complete';       // Step 5: Results ready
