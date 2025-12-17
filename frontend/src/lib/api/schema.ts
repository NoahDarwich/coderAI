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

// Backend variable types
interface BackendVariable {
  id: string;
  project_id: string;
  name: string;
  type: 'TEXT' | 'NUMBER' | 'DATE' | 'BOOLEAN' | 'CATEGORY' | 'LOCATION';
  instructions: string;
  classification_rules: Record<string, any> | null;
  order: number;
  created_at: string;
  updated_at: string;
}

interface BackendVariableCreate {
  name: string;
  type: 'TEXT' | 'NUMBER' | 'DATE' | 'BOOLEAN' | 'CATEGORY' | 'LOCATION';
  instructions: string;
  classification_rules?: Record<string, any>;
  order: number;
}

interface BackendVariableUpdate {
  name?: string;
  instructions?: string;
  classification_rules?: Record<string, any>;
  order?: number;
}

// Transform backend variable to frontend schema variable
function transformBackendVariable(backendVar: BackendVariable): SchemaVariable {
  // Map backend types to frontend types
  const typeMap: Record<BackendVariable['type'], SchemaVariable['type']> = {
    'TEXT': 'custom',
    'NUMBER': 'custom',
    'DATE': 'date',
    'BOOLEAN': 'custom',
    'CATEGORY': 'classification',
    'LOCATION': 'location',
  };

  const result: SchemaVariable = {
    id: backendVar.id,
    name: backendVar.name,
    type: typeMap[backendVar.type] || 'custom',
    description: backendVar.instructions,
    prompt: backendVar.instructions, // Use instructions as prompt for now
  };

  if (backendVar.classification_rules && (backendVar.classification_rules as any).categories) {
    result.categories = (backendVar.classification_rules as any).categories;
  }

  return result;
}

// Transform frontend schema variable to backend format
function transformToBackendCreate(
  variable: Omit<SchemaVariable, 'id'>,
  projectId: string,
  order: number = 1
): BackendVariableCreate {
  // Map frontend types to backend types
  const reverseTypeMap: Record<SchemaVariable['type'], BackendVariableCreate['type']> = {
    'custom': 'TEXT',
    'date': 'DATE',
    'location': 'LOCATION',
    'entity': 'TEXT',
    'classification': 'CATEGORY',
  };

  const create: BackendVariableCreate = {
    name: variable.name,
    type: reverseTypeMap[variable.type] || 'TEXT',
    instructions: variable.description || variable.prompt || '',
    order: order,
  };

  // Add classification rules for CATEGORY type
  if (variable.type === 'classification' && variable.categories) {
    create.classification_rules = {
      categories: variable.categories,
      allow_multiple: false,
    };
  }

  return create;
}

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

  // Individual variable operations
  listVariables: async (projectId: string): Promise<SchemaVariable[]> => {
    const schema = getMockSchemaByProjectId(projectId);
    return schema?.variables || [];
  },

  createVariable: async (
    projectId: string,
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
    // Mock implementation
    return { id: variableId, ...updates } as SchemaVariable;
  },

  deleteVariable: async (variableId: string): Promise<void> => {
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

      // Convert backend variables to frontend schema config format
      return {
        id: projectId,
        projectId,
        variables: variables.map(transformBackendVariable),
        prompts: {},
        conversationHistory: [],
        approved: false, // Backend doesn't track this yet
        version: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    } catch (error) {
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
    // Create/update each variable
    const createdVariables: SchemaVariable[] = [];

    for (let index = 0; index < data.variables.length; index++) {
      const variable = data.variables[index];
      const order = index + 1;

      if (variable.id && variable.id.startsWith('var-')) {
        // New variable (mock ID) - create it
        const backendData = transformToBackendCreate(variable, projectId, order);
        const created = await apiClient.post<BackendVariable>(
          `/api/v1/projects/${projectId}/variables`,
          backendData
        );
        createdVariables.push(transformBackendVariable(created));
      } else if (variable.id) {
        // Existing variable - update it
        const update: BackendVariableUpdate = {
          name: variable.name,
          instructions: variable.description || variable.prompt,
          order: order,
        };

        if (variable.type === 'classification' && variable.categories) {
          update.classification_rules = {
            categories: variable.categories,
            allow_multiple: false,
          };
        }

        const updated = await apiClient.put<BackendVariable>(
          `/api/v1/variables/${variable.id}`,
          update
        );
        createdVariables.push(transformBackendVariable(updated));
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
    // Backend doesn't have schema approval endpoint yet
    // For now, just return the current schema
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
    return variables.map(transformBackendVariable);
  },

  createVariable: async (
    projectId: string,
    variable: Omit<SchemaVariable, 'id'>
  ): Promise<SchemaVariable> => {
    // Get current variables to determine next order
    const existingVariables = await realSchemaApi.listVariables(projectId);
    const nextOrder = existingVariables.length + 1;

    const backendData = transformToBackendCreate(variable, projectId, nextOrder);
    const created = await apiClient.post<BackendVariable>(
      `/api/v1/projects/${projectId}/variables`,
      backendData
    );
    return transformBackendVariable(created);
  },

  updateVariable: async (
    variableId: string,
    updates: Partial<SchemaVariable>
  ): Promise<SchemaVariable> => {
    const backendUpdate: BackendVariableUpdate = {};

    if (updates.name) backendUpdate.name = updates.name;
    if (updates.description || updates.prompt) {
      backendUpdate.instructions = updates.description || updates.prompt || '';
    }
    if (updates.type === 'classification' && updates.categories) {
      backendUpdate.classification_rules = {
        categories: updates.categories,
        allow_multiple: false,
      };
    }

    const updated = await apiClient.put<BackendVariable>(
      `/api/v1/variables/${variableId}`,
      backendUpdate
    );
    return transformBackendVariable(updated);
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
      // Update cache
      queryClient.setQueryData(
        schemaKeys.list(projectId),
        savedSchema
      );

      // Invalidate to ensure fresh data
      queryClient.invalidateQueries({ queryKey: schemaKeys.list(projectId) });

      // Also invalidate project to update variable count
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
    onSuccess: (_, variables) => {
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
