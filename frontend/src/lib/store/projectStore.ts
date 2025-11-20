import { create } from 'zustand';
import { Project } from '@/lib/types/api';
import { mockProjects } from '@/mocks/projects';

interface ProjectState {
  projects: Project[];
  isLoading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  createProject: (name: string, description: string) => Promise<Project>;
  deleteProject: (id: string) => Promise<void>;
  getProjectById: (id: string) => Project | undefined;
}

// TODO(Phase 2): Replace with real API calls
export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  isLoading: false,
  error: null,

  fetchProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));
      set({ projects: mockProjects, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch projects', isLoading: false });
    }
  },

  createProject: async (name: string, description: string) => {
    set({ isLoading: true, error: null });
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      const newProject: Project = {
        id: `project-${Date.now()}`,
        userId: 'mock-user-1', // TODO(Phase 2): Get from auth context
        name,
        description,
        status: 'draft',
        documentCount: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      set((state) => ({
        projects: [newProject, ...state.projects],
        isLoading: false,
      }));

      return newProject;
    } catch (error) {
      set({ error: 'Failed to create project', isLoading: false });
      throw error;
    }
  },

  deleteProject: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      set((state) => ({
        projects: state.projects.filter((p) => p.id !== id),
        isLoading: false,
      }));
    } catch (error) {
      set({ error: 'Failed to delete project', isLoading: false });
      throw error;
    }
  },

  getProjectById: (id: string) => {
    return get().projects.find((p) => p.id === id);
  },
}));
