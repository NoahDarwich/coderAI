// services/newMockApi.ts - Complete Mock API implementation for Phase 1
import {
  Project,
  Document,
  Schema,
  Variable,
  ExtractionResult,
  ProcessingJob,
  ExportConfig,
  ExportResult,
  ApiResponse,
  PaginatedResponse,
  CreateProjectRequest,
  UpdateProjectRequest,
  SaveSchemaRequest,
  CreateVariableRequest,
  UpdateVariableRequest,
  ResultsListOptions,
} from '@/types';

import { mockProjects } from '@/mocks/mockProjects';
import { mockDocuments } from '@/mocks/mockDocuments';
import { mockSchemas } from '@/mocks/mockSchemas';
import { mockExtractionResults } from '@/mocks/mockExtractions';
import { mockProcessingJobs } from '@/mocks/mockProcessingJobs';

// Utility function to simulate network delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// In-memory storage (persists during session)
let projects = [...mockProjects];
let documents = [...mockDocuments];
let schemas = [...mockSchemas];
let extractions = [...mockExtractionResults];
let jobs = [...mockProcessingJobs];

// ============================================================================
// Projects API Implementation
// ============================================================================

export const projectsApi = {
  async list(): Promise<ApiResponse<Project[]>> {
    await delay(300);
    return { data: projects };
  },

  async get(id: string): Promise<ApiResponse<Project>> {
    await delay(200);
    const project = projects.find(p => p.id === id);
    if (!project) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Project with id ${id} not found`,
        },
      };
    }
    return { data: project };
  },

  async create(data: CreateProjectRequest): Promise<ApiResponse<Project>> {
    await delay(400);
    const newProject: Project = {
      id: `proj-${Date.now()}`,
      name: data.name,
      scale: data.scale,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      status: 'setup',
      documentCount: 0,
      schemaComplete: false,
      processingComplete: false,
    };
    projects.push(newProject);
    return { data: newProject };
  },

  async update(id: string, data: UpdateProjectRequest): Promise<ApiResponse<Project>> {
    await delay(300);
    const index = projects.findIndex(p => p.id === id);
    if (index === -1) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Project with id ${id} not found`,
        },
      };
    }
    projects[index] = {
      ...projects[index],
      ...data,
      updatedAt: new Date().toISOString(),
    };
    return { data: projects[index] };
  },

  async delete(id: string): Promise<ApiResponse<void>> {
    await delay(300);
    const index = projects.findIndex(p => p.id === id);
    if (index === -1) {
      return {
        data: undefined as any,
        error: {
          code: 'NOT_FOUND',
          message: `Project with id ${id} not found`,
        },
      };
    }
    projects.splice(index, 1);
    documents = documents.filter(d => d.projectId !== id);
    schemas = schemas.filter(s => s.projectId !== id);
    return { data: undefined as any };
  },
};

// ============================================================================
// Documents API Implementation
// ============================================================================

export const documentsApi = {
  async list(projectId: string): Promise<ApiResponse<Document[]>> {
    await delay(300);
    const projectDocs = documents.filter(d => d.projectId === projectId);
    return { data: projectDocs };
  },

  async get(documentId: string): Promise<ApiResponse<Document>> {
    await delay(200);
    const document = documents.find(d => d.id === documentId);
    if (!document) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Document with id ${documentId} not found`,
        },
      };
    }
    return { data: document };
  },

  async upload(projectId: string, files: File[]): Promise<ApiResponse<Document[]>> {
    await delay(800);
    const uploadedDocs: Document[] = files.map((file, index) => {
      const fileType = file.name.endsWith('.pdf')
        ? 'pdf'
        : file.name.endsWith('.docx')
        ? 'docx'
        : 'txt';

      const newDoc: Document = {
        id: `doc-${Date.now()}-${index}`,
        projectId,
        fileName: file.name,
        fileType,
        fileSize: file.size,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded',
      };
      documents.push(newDoc);
      return newDoc;
    });

    const projectIndex = projects.findIndex(p => p.id === projectId);
    if (projectIndex !== -1) {
      projects[projectIndex].documentCount += files.length;
      projects[projectIndex].updatedAt = new Date().toISOString();
    }

    return { data: uploadedDocs };
  },

  async delete(documentId: string): Promise<ApiResponse<void>> {
    await delay(200);
    const index = documents.findIndex(d => d.id === documentId);
    if (index === -1) {
      return {
        data: undefined as any,
        error: {
          code: 'NOT_FOUND',
          message: `Document with id ${documentId} not found`,
        },
      };
    }
    const doc = documents[index];
    documents.splice(index, 1);

    const projectIndex = projects.findIndex(p => p.id === doc.projectId);
    if (projectIndex !== -1) {
      projects[projectIndex].documentCount = Math.max(
        0,
        projects[projectIndex].documentCount - 1
      );
      projects[projectIndex].updatedAt = new Date().toISOString();
    }

    return { data: undefined as any };
  },

  async getContent(documentId: string): Promise<ApiResponse<string>> {
    await delay(400);
    const document = documents.find(d => d.id === documentId);
    if (!document) {
      return {
        data: '',
        error: {
          code: 'NOT_FOUND',
          message: `Document with id ${documentId} not found`,
        },
      };
    }
    const mockContent =
      document.contentPreview ||
      `Mock content for ${document.fileName}. This would be the full extracted text from the document in a real implementation.`;
    return { data: mockContent };
  },
};

// ============================================================================
// Schema API Implementation
// ============================================================================

export const schemaApi = {
  async get(projectId: string): Promise<ApiResponse<Schema | null>> {
    await delay(250);
    const schema = schemas.find(s => s.projectId === projectId);
    return { data: schema || null };
  },

  async save(projectId: string, data: SaveSchemaRequest): Promise<ApiResponse<Schema>> {
    await delay(400);
    const existingIndex = schemas.findIndex(s => s.projectId === projectId);

    if (existingIndex !== -1) {
      schemas[existingIndex] = {
        ...schemas[existingIndex],
        variables: data.variables.map((v, index) => ({
          id: `var-${Date.now()}-${index}`,
          ...v,
          order: index,
        })),
        createdAt: schemas[existingIndex].createdAt,
      };
      return { data: schemas[existingIndex] };
    } else {
      const newSchema: Schema = {
        id: `schema-${Date.now()}`,
        projectId,
        variables: data.variables.map((v, index) => ({
          id: `var-${Date.now()}-${index}`,
          ...v,
          order: index,
        })),
        createdAt: new Date().toISOString(),
      };
      schemas.push(newSchema);
      return { data: newSchema };
    }
  },

  async confirm(projectId: string): Promise<ApiResponse<Schema>> {
    await delay(300);
    const index = schemas.findIndex(s => s.projectId === projectId);
    if (index === -1) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Schema for project ${projectId} not found`,
        },
      };
    }
    schemas[index].confirmedAt = new Date().toISOString();

    const projectIndex = projects.findIndex(p => p.id === projectId);
    if (projectIndex !== -1) {
      projects[projectIndex].schemaComplete = true;
      projects[projectIndex].status = 'processing';
      projects[projectIndex].updatedAt = new Date().toISOString();
    }

    return { data: schemas[index] };
  },

  async addVariable(
    projectId: string,
    variable: CreateVariableRequest
  ): Promise<ApiResponse<Variable>> {
    await delay(300);
    const schema = schemas.find(s => s.projectId === projectId);
    if (!schema) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Schema for project ${projectId} not found`,
        },
      };
    }

    const newVariable: Variable = {
      id: `var-${Date.now()}`,
      ...variable,
      order: schema.variables.length,
    };
    schema.variables.push(newVariable);
    return { data: newVariable };
  },

  async updateVariable(
    projectId: string,
    variableId: string,
    data: UpdateVariableRequest
  ): Promise<ApiResponse<Variable>> {
    await delay(300);
    const schema = schemas.find(s => s.projectId === projectId);
    if (!schema) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Schema for project ${projectId} not found`,
        },
      };
    }

    const varIndex = schema.variables.findIndex(v => v.id === variableId);
    if (varIndex === -1) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Variable with id ${variableId} not found`,
        },
      };
    }

    schema.variables[varIndex] = {
      ...schema.variables[varIndex],
      ...data,
    };
    return { data: schema.variables[varIndex] };
  },

  async deleteVariable(projectId: string, variableId: string): Promise<ApiResponse<void>> {
    await delay(250);
    const schema = schemas.find(s => s.projectId === projectId);
    if (!schema) {
      return {
        data: undefined as any,
        error: {
          code: 'NOT_FOUND',
          message: `Schema for project ${projectId} not found`,
        },
      };
    }

    const varIndex = schema.variables.findIndex(v => v.id === variableId);
    if (varIndex === -1) {
      return {
        data: undefined as any,
        error: {
          code: 'NOT_FOUND',
          message: `Variable with id ${variableId} not found`,
        },
      };
    }

    schema.variables.splice(varIndex, 1);
    schema.variables.forEach((v, index) => {
      v.order = index;
    });
    return { data: undefined as any };
  },

  async reorderVariables(projectId: string, variableIds: string[]): Promise<ApiResponse<Schema>> {
    await delay(200);
    const schema = schemas.find(s => s.projectId === projectId);
    if (!schema) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Schema for project ${projectId} not found`,
        },
      };
    }

    const reordered: Variable[] = [];
    variableIds.forEach((id, index) => {
      const variable = schema.variables.find(v => v.id === id);
      if (variable) {
        reordered.push({ ...variable, order: index });
      }
    });
    schema.variables = reordered;
    return { data: schema };
  },
};

// ============================================================================
// Processing API Implementation
// ============================================================================

export const processingApi = {
  async startSample(projectId: string, sampleSize: number): Promise<ApiResponse<ProcessingJob>> {
    await delay(500);
    const newJob: ProcessingJob = {
      id: `job-${Date.now()}`,
      projectId,
      type: 'sample',
      status: 'queued',
      progress: 0,
      totalDocuments: sampleSize,
      processedDocuments: 0,
      startedAt: new Date().toISOString(),
      logs: [
        {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: `Sample processing queued for ${sampleSize} documents`,
        },
      ],
    };
    jobs.push(newJob);

    setTimeout(() => {
      const jobIndex = jobs.findIndex(j => j.id === newJob.id);
      if (jobIndex !== -1) {
        jobs[jobIndex].status = 'processing';
      }
    }, 1000);

    return { data: newJob };
  },

  async startFull(projectId: string): Promise<ApiResponse<ProcessingJob>> {
    await delay(500);
    const projectDocs = documents.filter(d => d.projectId === projectId);
    const newJob: ProcessingJob = {
      id: `job-${Date.now()}`,
      projectId,
      type: 'full',
      status: 'queued',
      progress: 0,
      totalDocuments: projectDocs.length,
      processedDocuments: 0,
      startedAt: new Date().toISOString(),
      logs: [
        {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: `Full processing started for ${projectDocs.length} documents`,
        },
      ],
    };
    jobs.push(newJob);

    setTimeout(() => {
      const jobIndex = jobs.findIndex(j => j.id === newJob.id);
      if (jobIndex !== -1) {
        jobs[jobIndex].status = 'processing';
      }
    }, 1000);

    return { data: newJob };
  },

  async getJob(jobId: string): Promise<ApiResponse<ProcessingJob>> {
    await delay(150);
    const job = jobs.find(j => j.id === jobId);
    if (!job) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Job with id ${jobId} not found`,
        },
      };
    }
    return { data: job };
  },

  async cancelJob(jobId: string): Promise<ApiResponse<void>> {
    await delay(200);
    const index = jobs.findIndex(j => j.id === jobId);
    if (index === -1) {
      return {
        data: undefined as any,
        error: {
          code: 'NOT_FOUND',
          message: `Job with id ${jobId} not found`,
        },
      };
    }
    jobs[index].status = 'failed';
    jobs[index].logs.push({
      timestamp: new Date().toISOString(),
      level: 'warning',
      message: 'Job cancelled by user',
    });
    return { data: undefined as any };
  },
};

// ============================================================================
// Results API Implementation
// ============================================================================

export const resultsApi = {
  async list(
    projectId: string,
    options?: ResultsListOptions
  ): Promise<ApiResponse<PaginatedResponse<ExtractionResult>>> {
    await delay(350);
    let filtered = extractions.filter(e => e.projectId === projectId);

    if (options?.documentId) {
      filtered = filtered.filter(e => e.documentId === options.documentId);
    }

    if (options?.minConfidence !== undefined) {
      filtered = filtered.filter(e => {
        return e.values.some(v => v.confidence >= options.minConfidence!);
      });
    }

    const page = options?.page || 1;
    const pageSize = options?.pageSize || 50;
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const paginatedData = filtered.slice(start, end);

    return {
      data: {
        data: paginatedData,
        pagination: {
          page,
          pageSize,
          total: filtered.length,
          totalPages: Math.ceil(filtered.length / pageSize),
        },
      },
    };
  },

  async get(extractionId: string): Promise<ApiResponse<ExtractionResult>> {
    await delay(200);
    const extraction = extractions.find(e => e.id === extractionId);
    if (!extraction) {
      return {
        data: null as any,
        error: {
          code: 'NOT_FOUND',
          message: `Extraction with id ${extractionId} not found`,
        },
      };
    }
    return { data: extraction };
  },

  async flag(extractionId: string, isCorrect: boolean): Promise<ApiResponse<void>> {
    await delay(200);
    return { data: undefined as any };
  },
};

// ============================================================================
// Export API Implementation
// ============================================================================

export const exportApi = {
  async generate(projectId: string, config: ExportConfig): Promise<ApiResponse<ExportResult>> {
    await delay(800);
    const projectExtractions = extractions.filter(e => e.projectId === projectId);

    let csvContent = '';
    if (config.structure === 'wide') {
      csvContent = generateWideCSV(projectExtractions, config);
    } else {
      csvContent = generateLongCSV(projectExtractions, config);
    }

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);

    const result: ExportResult = {
      id: `export-${Date.now()}`,
      fileName: `extraction_results_${projectId}_${Date.now()}.csv`,
      fileSize: blob.size,
      createdAt: new Date().toISOString(),
      downloadUrl: url,
    };

    return { data: result };
  },

  async download(exportId: string): Promise<ApiResponse<Blob>> {
    await delay(300);
    const blob = new Blob(['Mock CSV content'], { type: 'text/csv' });
    return { data: blob };
  },
};

function generateWideCSV(extractions: ExtractionResult[], config: ExportConfig): string {
  if (extractions.length === 0) return '';

  const variables = extractions[0].values.map((v, i) => `Variable_${i + 1}`);
  let headers = ['Document ID', ...variables];

  if (config.includeConfidence) {
    headers = headers.concat(variables.map(v => `${v}_Confidence`));
  }

  const rows = [headers.join(',')];

  extractions.forEach(ext => {
    const values = ext.values.map(v => `"${v.value}"`);
    let row = [ext.documentId, ...values];

    if (config.includeConfidence) {
      const confidences = ext.values.map(v => v.confidence);
      row = row.concat(confidences.map(String));
    }

    rows.push(row.join(','));
  });

  return rows.join('\n');
}

function generateLongCSV(extractions: ExtractionResult[], config: ExportConfig): string {
  const headers = ['Document ID', 'Variable ID', 'Value'];
  if (config.includeConfidence) headers.push('Confidence');
  if (config.includeSourceText) headers.push('Source Text');

  const rows = [headers.join(',')];

  extractions.forEach(ext => {
    ext.values.forEach(val => {
      let row = [ext.documentId, val.variableId, `"${val.value}"`];
      if (config.includeConfidence) row.push(String(val.confidence));
      if (config.includeSourceText) row.push(`"${val.sourceText || ''}"`);
      rows.push(row.join(','));
    });
  });

  return rows.join('\n');
}

// ============================================================================
// Combined API Client Export
// ============================================================================

export const api = {
  projects: projectsApi,
  documents: documentsApi,
  schema: schemaApi,
  processing: processingApi,
  results: resultsApi,
  export: exportApi,
};
