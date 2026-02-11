/**
 * Schema API Client
 * TanStack Query hooks for schema operations (variables)
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { SchemaConfig, ChatMessage, SchemaVariable } from '@/lib/types/api';
import {
  getMockSchemaByProjectId,
  saveMockSchema,
} from '@/mocks/schema';
import { apiClient } from './client';
import {
  BackendVariable,
  BackendVariableUpdate,
  transformVariable,
  toBackendVariableCreate,
  toBackendVariableUpdate,
} from './transforms';

/**
 * Query Keys
 */
export const schemaKeys = {
  all: ['schemas'] as const,
  lists: () => [...schemaKeys.all, 'list'] as const,
  list: (projectId: string) => [...schemaKeys.lists(), projectId] as const,
  details: () => [...schemaKeys.all, 'detail'] as const,
  detail: (id: string) => [...schemaKeys.details(), id] as const,
};

// Mock API functions
const mockSchemaApi = {
  get: async (projectId: string): Promise<SchemaConfig | null> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return getMockSchemaByProjectId(projectId) || null;
  },

  save: async (
    projectId: string,
    data: {
      conversationHistory: ChatMessage[];
      variables: SchemaVariable[];
      prompts: Record<string, string>;
    }
  ): Promise<SchemaConfig> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return saveMockSchema(projectId, data);
  },

  approve: async (projectId: string): Promise<SchemaConfig> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const schema = getMockSchemaByProjectId(projectId);
    if (!schema) {
      throw new Error('Schema not found');
    }
    return saveMockSchema(projectId, {
      ...schema,
      approved: true,
    });
  },

  listVariables: async (projectId: string): Promise<SchemaVariable[]> => {
    const schema = getMockSchemaByProjectId(projectId);
    return schema?.variables || [];
  },

  createVariable: async (
    _projectId: string,
    variable: Omit<SchemaVariable, 'id'>
  ): Promise<SchemaVariable> => {
    const newVar: SchemaVariable = {
      ...variable,
      id: `var-${Date.now()}`,
    };
    return newVar;
  },

  updateVariable: async (
    variableId: string,
    updates: Partial<SchemaVariable>
  ): Promise<SchemaVariable> => {
    return { id: variableId, ...updates } as SchemaVariable;
  },

  deleteVariable: async (_variableId: string): Promise<void> => {
    // Mock implementation
  },
};

// Real API functions
const realSchemaApi = {
  get: async (projectId: string): Promise<SchemaConfig | null> => {
    try {
      const variables = await apiClient.get<BackendVariable[]>(
        `/api/v1/projects/${projectId}/variables`
      );

      if (variables.length === 0) {
        return null;
      }

      return {
        id: projectId,
        projectId,
        variables: variables.map(transformVariable),
        prompts: {},
        conversationHistory: [],
        approved: false,
        version: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    } catch {
      return null;
    }
  },

  save: async (
    projectId: string,
    data: {
      conversationHistory: ChatMessage[];
      variables: SchemaVariable[];
      prompts: Record<string, string>;
    }
  ): Promise<SchemaConfig> => {
    const createdVariables: SchemaVariable[] = [];

    for (let index = 0; index < data.variables.length; index++) {
      const variable = data.variables[index];
      const order = index + 1;

      if (variable.id && variable.id.startsWith('var-')) {
        // New variable (mock ID) — create it
        const backendData = toBackendVariableCreate(variable, order);
        const created = await apiClient.post<BackendVariable>(
          `/api/v1/projects/${projectId}/variables`,
          backendData
        );
        createdVariables.push(transformVariable(created));
      } else if (variable.id) {
        // Existing variable — update it
        const update: BackendVariableUpdate = {
          name: variable.name,
          instructions: variable.instructions || variable.description || variable.prompt || '',
          order,
        };

        if (variable.type === 'CATEGORY' && variable.categories) {
          update.classification_rules = {
            categories: variable.categories,
            allow_multiple: false,
          };
        }

        const updated = await apiClient.put<BackendVariable>(
          `/api/v1/variables/${variable.id}`,
          update
        );
        createdVariables.push(transformVariable(updated));
      }
    }

    return {
      id: projectId,
      projectId,
      variables: createdVariables,
      prompts: data.prompts,
      conversationHistory: data.conversationHistory,
      approved: false,
      version: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  },

  approve: async (projectId: string): Promise<SchemaConfig> => {
    // Wire to real backend endpoint
    await apiClient.post(`/api/v1/projects/${projectId}/schema/approve`);

    // Fetch current schema to return
    const schema = await realSchemaApi.get(projectId);
    if (!schema) {
      throw new Error('Schema not found');
    }
    return { ...schema, approved: true };
  },

  listVariables: async (projectId: string): Promise<SchemaVariable[]> => {
    const variables = await apiClient.get<BackendVariable[]>(
      `/api/v1/projects/${projectId}/variables`
    );
    return variables.map(transformVariable);
  },

  createVariable: async (
    projectId: string,
    variable: Omit<SchemaVariable, 'id'>
  ): Promise<SchemaVariable> => {
    const existingVariables = await realSchemaApi.listVariables(projectId);
    const nextOrder = existingVariables.length + 1;

    const backendData = toBackendVariableCreate(variable, nextOrder);
    const created = await apiClient.post<BackendVariable>(
      `/api/v1/projects/${projectId}/variables`,
      backendData
    );
    return transformVariable(created);
  },

  updateVariable: async (
    variableId: string,
    updates: Partial<SchemaVariable>
  ): Promise<SchemaVariable> => {
    const backendUpdate = toBackendVariableUpdate(updates);
    const updated = await apiClient.put<BackendVariable>(
      `/api/v1/variables/${variableId}`,
      backendUpdate
    );
    return transformVariable(updated);
  },

  deleteVariable: async (variableId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/variables/${variableId}`);
  },
};

// Select API based on environment
const schemaApi = apiClient.useMockData ? mockSchemaApi : realSchemaApi;

/**
 * Fetch schema for a project
 */
export function useSchema(projectId: string) {
  return useQuery({
    queryKey: schemaKeys.list(projectId),
    queryFn: () => schemaApi.get(projectId),
    staleTime: 1000 * 60 * 5, // 5 minutes
    enabled: !!projectId,
  });
}

/**
 * Save schema mutation
 */
export function useSaveSchema(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      conversationHistory: ChatMessage[];
      variables: SchemaVariable[];
      prompts: Record<string, string>;
    }) => schemaApi.save(projectId, data),
    onSuccess: (savedSchema) => {
      queryClient.setQueryData(
        schemaKeys.list(projectId),
        savedSchema
      );
      queryClient.invalidateQueries({ queryKey: schemaKeys.list(projectId) });
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] });
    },
  });
}

/**
 * Approve schema mutation
 */
export function useApproveSchema(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => schemaApi.approve(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: schemaKeys.list(projectId) });
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] });
    },
  });
}

/**
 * Individual variable operations
 */
export function useVariables(projectId: string) {
  return useQuery({
    queryKey: ['variables', projectId],
    queryFn: () => schemaApi.listVariables(projectId),
    enabled: !!projectId,
  });
}

export function useCreateVariable(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (variable: Omit<SchemaVariable, 'id'>) =>
      schemaApi.createVariable(projectId, variable),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variables', projectId] });
      queryClient.invalidateQueries({ queryKey: schemaKeys.list(projectId) });
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] });
    },
  });
}

export function useUpdateVariable() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<SchemaVariable> }) =>
      schemaApi.updateVariable(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variables'] });
      queryClient.invalidateQueries({ queryKey: schemaKeys.all });
    },
  });
}

export function useDeleteVariable(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (variableId: string) => schemaApi.deleteVariable(variableId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variables', projectId] });
      queryClient.invalidateQueries({ queryKey: schemaKeys.list(projectId) });
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] });
    },
  });
}
