import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Project } from '@/lib/types/api';
import { mockProjects } from '@/mocks/projects';
import { apiClient } from './client';
import {
  BackendProject,
  transformProject,
  toBackendProjectCreate,
  toBackendProjectUpdate,
} from './transforms';

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

  delete: async (_id: string): Promise<void> => {
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

// Real API functions
const realProjectApi = {
  getAll: async (): Promise<Project[]> => {
    const projects = await apiClient.get<BackendProject[]>('/api/v1/projects');
    return projects.map(transformProject);
  },

  getById: async (id: string): Promise<Project | undefined> => {
    try {
      const project = await apiClient.get<BackendProject>(`/api/v1/projects/${id}`);
      return transformProject(project);
    } catch (error) {
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
    const backendData = toBackendProjectCreate(data);
    const project = await apiClient.post<BackendProject>('/api/v1/projects', backendData);
    return transformProject(project);
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/projects/${id}`);
  },

  update: async (
    id: string,
    data: Partial<Project>
  ): Promise<Project | undefined> => {
    const backendData = toBackendProjectUpdate(data);
    const project = await apiClient.put<BackendProject>(`/api/v1/projects/${id}`, backendData);
    return transformProject(project);
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
