import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Project } from '@/lib/types/api';
import { mockProjects } from '@/mocks/projects';
import { apiClient } from './client';

// Mock API functions for Phase 1
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const mockProjectApi = {
  getAll: async (): Promise<Project[]> => {
    await delay(500);
    return mockProjects;
  },

  getById: async (id: string): Promise<Project | undefined> => {
    await delay(300);
    return mockProjects.find((p) => p.id === id);
  },

  create: async (data: {
    name: string;
    description: string;
  }): Promise<Project> => {
    await delay(500);
    return {
      id: `project-${Date.now()}`,
      userId: 'mock-user-1',
      name: data.name,
      description: data.description,
      status: 'draft',
      documentCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  },

  delete: async (id: string): Promise<void> => {
    await delay(500);
  },

  update: async (
    id: string,
    data: Partial<Project>
  ): Promise<Project | undefined> => {
    await delay(500);
    const project = mockProjects.find((p) => p.id === id);
    if (!project) return undefined;
    return { ...project, ...data, updatedAt: new Date().toISOString() };
  },
};

// Real API types matching backend schema
interface BackendProject {
  id: string;
  name: string;
  scale: 'SMALL' | 'LARGE';
  language: string;
  domain?: string | null;
  status: 'CREATED' | 'SCHEMA_DEFINED' | 'PROCESSING' | 'COMPLETED' | 'ERROR';
  created_at: string;
  updated_at: string;
  variable_count?: number;
  document_count?: number;
}

interface BackendProjectCreate {
  name: string;
  scale: 'SMALL' | 'LARGE';
  language?: string;
  domain?: string;
}

interface BackendProjectUpdate {
  name?: string;
  domain?: string;
}

// Transform backend project to frontend format
function transformBackendProject(backendProject: BackendProject): Project {
  // Map backend status to frontend status
  const statusMap: Record<BackendProject['status'], Project['status']> = {
    'CREATED': 'draft',
    'SCHEMA_DEFINED': 'draft',
    'PROCESSING': 'processing',
    'COMPLETED': 'completed',
    'ERROR': 'error',
  };

  return {
    id: backendProject.id,
    userId: 'backend-user', // Backend doesn't have user concept yet
    name: backendProject.name,
    description: backendProject.domain || '', // Use domain as description for now
    status: statusMap[backendProject.status] || 'draft',
    documentCount: backendProject.document_count || 0,
    createdAt: backendProject.created_at,
    updatedAt: backendProject.updated_at,
  };
}

// Transform frontend create data to backend format
function transformToBackendCreate(data: {
  name: string;
  description: string;
}): BackendProjectCreate {
  return {
    name: data.name,
    scale: 'SMALL', // Default to SMALL for now
    language: 'en',
    domain: data.description,
  };
}

// Transform frontend update data to backend format
function transformToBackendUpdate(data: Partial<Project>): BackendProjectUpdate {
  const update: BackendProjectUpdate = {};

  if (data.name !== undefined) {
    update.name = data.name;
  }

  if (data.description !== undefined) {
    update.domain = data.description;
  }

  return update;
}

// Real API functions
const realProjectApi = {
  getAll: async (): Promise<Project[]> => {
    const projects = await apiClient.get<BackendProject[]>('/api/v1/projects');
    return projects.map(transformBackendProject);
  },

  getById: async (id: string): Promise<Project | undefined> => {
    try {
      const project = await apiClient.get<BackendProject>(`/api/v1/projects/${id}`);
      return transformBackendProject(project);
    } catch (error) {
      // Return undefined if project not found (404)
      if (error instanceof Error && 'status' in error && (error as any).status === 404) {
        return undefined;
      }
      throw error;
    }
  },

  create: async (data: {
    name: string;
    description: string;
  }): Promise<Project> => {
    const backendData = transformToBackendCreate(data);
    const project = await apiClient.post<BackendProject>('/api/v1/projects', backendData);
    return transformBackendProject(project);
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/projects/${id}`);
  },

  update: async (
    id: string,
    data: Partial<Project>
  ): Promise<Project | undefined> => {
    const backendData = transformToBackendUpdate(data);
    const project = await apiClient.put<BackendProject>(`/api/v1/projects/${id}`, backendData);
    return transformBackendProject(project);
  },
};

// Select API based on environment
const projectApi = apiClient.useMockData ? mockProjectApi : realProjectApi;

// React Query hooks
export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.getAll,
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: () => projectApi.getById(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Project> }) =>
      projectApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['projects', variables.id] });
    },
  });
}
