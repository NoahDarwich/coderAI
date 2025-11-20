import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Project } from '@/lib/types/api';
import { mockProjects } from '@/mocks/projects';

// TODO(Phase 2): Replace with real API calls

// Simulated API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Mock API functions
const projectApi = {
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
      userId: 'mock-user-1', // TODO(Phase 2): Get from auth context
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
    // In a real app, this would delete from the database
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
