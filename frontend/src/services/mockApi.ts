/**
 * Mock API Service
 * Simulates backend API calls with mock data for Phase 1
 */

import {
  Project,
  Document,
  ChatMessage,
  SchemaConfig,
  ExtractionResult,
  ProcessingJob,
  ApiResponse,
  PaginatedResponse,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  ExportConfig,
} from '@/lib/types/api';

import {
  getMockProjects,
  getMockProjectById,
  createMockProject,
  deleteMockProject,
} from '@/mocks/projects';

import {
  getMockDocumentsByProjectId,
  getMockDocumentById,
  uploadMockDocument,
  deleteMockDocument,
} from '@/mocks/documents';

import {
  getMockConversation,
  addMockMessage,
} from '@/mocks/conversations';

import {
  getMockSchemaByProjectId,
  saveMockSchema,
} from '@/mocks/schema';

import {
  getMockResultsByProjectId,
  getMockResultById,
  toggleMockResultFlag,
} from '@/mocks/results';

/**
 * Simulate API delay
 */
const delay = (ms: number = 300) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Authentication API
 */
export const mockAuthApi = {
  async login(data: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    await delay();

    // Mock authentication - accept any email/password
    return {
      success: true,
      data: {
        user: {
          id: 'user-001',
          email: data.email,
          name: 'Test User',
          createdAt: new Date().toISOString(),
        },
        token: 'mock-jwt-token-' + Date.now(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      },
    };
  },

  async register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    await delay();

    return {
      success: true,
      data: {
        user: {
          id: 'user-' + Date.now(),
          email: data.email,
          name: data.name,
          createdAt: new Date().toISOString(),
        },
        token: 'mock-jwt-token-' + Date.now(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      },
    };
  },

  async logout(): Promise<ApiResponse<void>> {
    await delay(100);
    return { success: true };
  },
};

/**
 * Projects API
 */
export const mockProjectsApi = {
  async getAll(): Promise<ApiResponse<Project[]>> {
    await delay();
    return {
      success: true,
      data: getMockProjects(),
    };
  },

  async getById(id: string): Promise<ApiResponse<Project>> {
    await delay();
    const project = getMockProjectById(id);

    if (!project) {
      return {
        success: false,
        error: 'Project not found',
      };
    }

    return {
      success: true,
      data: project,
    };
  },

  async create(data: { name: string; description: string }): Promise<ApiResponse<Project>> {
    await delay(500);
    const project = createMockProject(data);

    return {
      success: true,
      data: project,
      message: 'Project created successfully',
    };
  },

  async delete(id: string): Promise<ApiResponse<void>> {
    await delay(300);
    const success = deleteMockProject(id);

    if (!success) {
      return {
        success: false,
        error: 'Project not found',
      };
    }

    return {
      success: true,
      message: 'Project deleted successfully',
    };
  },
};

/**
 * Documents API
 */
export const mockDocumentsApi = {
  async getByProjectId(projectId: string): Promise<ApiResponse<Document[]>> {
    await delay();
    return {
      success: true,
      data: getMockDocumentsByProjectId(projectId),
    };
  },

  async getById(id: string): Promise<ApiResponse<Document>> {
    await delay();
    const document = getMockDocumentById(id);

    if (!document) {
      return {
        success: false,
        error: 'Document not found',
      };
    }

    return {
      success: true,
      data: document,
    };
  },

  async upload(projectId: string, files: File[]): Promise<ApiResponse<Document[]>> {
    await delay(1000); // Simulate upload time

    const uploadedDocs = files.map(file =>
      uploadMockDocument(projectId, {
        name: file.name,
        size: file.size,
        type: file.type,
      })
    );

    return {
      success: true,
      data: uploadedDocs,
      message: `${files.length} document(s) uploaded successfully`,
    };
  },

  async delete(id: string): Promise<ApiResponse<void>> {
    await delay(200);
    const success = deleteMockDocument(id);

    if (!success) {
      return {
        success: false,
        error: 'Document not found',
      };
    }

    return {
      success: true,
      message: 'Document deleted successfully',
    };
  },
};

/**
 * Chat/Schema API
 */
export const mockChatApi = {
  async getConversation(projectId: string): Promise<ApiResponse<ChatMessage[]>> {
    await delay();
    return {
      success: true,
      data: getMockConversation(projectId),
    };
  },

  async sendMessage(projectId: string, message: string): Promise<ApiResponse<ChatMessage>> {
    await delay(800); // Simulate AI thinking time

    const userMessage = addMockMessage(message);

    // Simulate AI response (mock)
    const aiResponse: ChatMessage = {
      id: 'msg-' + Date.now(),
      role: 'assistant',
      content: 'Thank you for that information. I\'m processing your request...',
      timestamp: new Date().toISOString(),
    };

    return {
      success: true,
      data: aiResponse,
    };
  },

  async getSchema(projectId: string): Promise<ApiResponse<SchemaConfig>> {
    await delay();
    const schema = getMockSchemaByProjectId(projectId);

    if (!schema) {
      return {
        success: false,
        error: 'Schema not found for this project',
      };
    }

    return {
      success: true,
      data: schema,
    };
  },

  async saveSchema(projectId: string, data: Partial<SchemaConfig>): Promise<ApiResponse<SchemaConfig>> {
    await delay(500);
    const schema = saveMockSchema(projectId, data);

    return {
      success: true,
      data: schema,
      message: 'Schema saved successfully',
    };
  },
};

/**
 * Extraction Results API
 */
export const mockResultsApi = {
  async getByProjectId(projectId: string): Promise<ApiResponse<ExtractionResult[]>> {
    await delay();
    return {
      success: true,
      data: getMockResultsByProjectId(projectId),
    };
  },

  async getById(id: string): Promise<ApiResponse<ExtractionResult>> {
    await delay();
    const result = getMockResultById(id);

    if (!result) {
      return {
        success: false,
        error: 'Result not found',
      };
    }

    return {
      success: true,
      data: result,
    };
  },

  async toggleFlag(id: string): Promise<ApiResponse<ExtractionResult>> {
    await delay(200);
    const result = toggleMockResultFlag(id);

    if (!result) {
      return {
        success: false,
        error: 'Result not found',
      };
    }

    return {
      success: true,
      data: result,
    };
  },
};

/**
 * Processing API
 */
export const mockProcessingApi = {
  async startSample(projectId: string): Promise<ApiResponse<ProcessingJob>> {
    await delay(500);

    const job: ProcessingJob = {
      id: 'job-' + Date.now(),
      projectId,
      type: 'sample',
      status: 'running',
      progress: 0,
      totalDocuments: 10,
      processedDocuments: 0,
      startedAt: new Date().toISOString(),
    };

    return {
      success: true,
      data: job,
      message: 'Sample processing started',
    };
  },

  async startFull(projectId: string): Promise<ApiResponse<ProcessingJob>> {
    await delay(500);

    const job: ProcessingJob = {
      id: 'job-' + Date.now(),
      projectId,
      type: 'full',
      status: 'running',
      progress: 0,
      totalDocuments: 45,
      processedDocuments: 0,
      startedAt: new Date().toISOString(),
    };

    return {
      success: true,
      data: job,
      message: 'Full processing started',
    };
  },

  async getJobStatus(jobId: string): Promise<ApiResponse<ProcessingJob>> {
    await delay(100);

    // Mock job with incremental progress
    const job: ProcessingJob = {
      id: jobId,
      projectId: 'proj-001',
      type: 'sample',
      status: 'running',
      progress: Math.min(Math.floor(Math.random() * 100), 95),
      totalDocuments: 10,
      processedDocuments: Math.floor(Math.random() * 10),
      currentDocument: 'processing_document_' + Math.floor(Math.random() * 10) + '.pdf',
      estimatedTimeRemaining: Math.floor(Math.random() * 300),
      startedAt: new Date(Date.now() - 60000).toISOString(),
    };

    return {
      success: true,
      data: job,
    };
  },
};

/**
 * Export API
 */
export const mockExportApi = {
  async exportToCSV(projectId: string, config: ExportConfig): Promise<ApiResponse<{ url: string; filename: string }>> {
    await delay(1000);

    // In Phase 1, this will trigger client-side CSV generation
    // For now, just return success
    return {
      success: true,
      data: {
        url: '/mock-export/' + projectId + '.csv',
        filename: `export_${projectId}_${Date.now()}.csv`,
      },
      message: 'Export prepared successfully',
    };
  },
};
