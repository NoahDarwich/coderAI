/**
 * API Service Abstraction
 * Central point for all API calls
 *
 * Phase 1: Imports mockApi
 * Phase 2: Switch to import realApi
 */

// TODO(Phase 2): Replace with real API implementation
import {
  mockAuthApi,
  mockProjectsApi,
  mockDocumentsApi,
  mockChatApi,
  mockResultsApi,
  mockProcessingApi,
  mockExportApi,
} from './mockApi';

/**
 * Authentication API
 */
export const authApi = mockAuthApi;

/**
 * Projects API
 */
export const projectsApi = mockProjectsApi;

/**
 * Documents API
 */
export const documentsApi = mockDocumentsApi;

/**
 * Chat/Schema API
 */
export const chatApi = mockChatApi;

/**
 * Results API
 */
export const resultsApi = mockResultsApi;

/**
 * Processing API
 */
export const processingApi = mockProcessingApi;

/**
 * Export API
 */
export const exportApi = mockExportApi;

/**
 * Centralized API object for easy import
 */
export const api = {
  auth: authApi,
  projects: projectsApi,
  documents: documentsApi,
  chat: chatApi,
  results: resultsApi,
  processing: processingApi,
  export: exportApi,
};

export default api;
