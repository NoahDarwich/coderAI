import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Variable } from '@/types';

interface SchemaWizardState {
  variables: Variable[];
  currentVariableIndex: number;
  isDraft: boolean;
  projectId: string | null;

  // Actions
  setProjectId: (projectId: string) => void;
  addVariable: (variable: Omit<Variable, 'id' | 'order'>) => void;
  updateVariable: (index: number, variable: Partial<Variable>) => void;
  deleteVariable: (index: number) => void;
  duplicateVariable: (index: number) => void;
  reorderVariables: (startIndex: number, endIndex: number) => void;
  setCurrentIndex: (index: number) => void;
  saveDraft: () => void;
  loadDraft: (projectId: string) => void;
  clearDraft: () => void;
  reset: () => void;
}

export const useSchemaWizardStore = create<SchemaWizardState>()(
  persist(
    (set, get) => ({
      variables: [],
      currentVariableIndex: 0,
      isDraft: false,
      projectId: null,

      setProjectId: (projectId) => set({ projectId }),

      addVariable: (variable) => set((state) => {
        const newVariable: Variable = {
          id: `var-temp-${Math.random().toString(36).substring(2, 9)}`,
          ...variable,
          order: state.variables.length,
        };
        return {
          variables: [...state.variables, newVariable],
          isDraft: true,
        };
      }),

      updateVariable: (index, updates) => set((state) => ({
        variables: state.variables.map((v, i) =>
          i === index ? { ...v, ...updates } : v
        ),
        isDraft: true,
      })),

      deleteVariable: (index) => set((state) => ({
        variables: state.variables
          .filter((_, i) => i !== index)
          .map((v, i) => ({ ...v, order: i })),
        isDraft: true,
      })),

      duplicateVariable: (index) => set((state) => {
        const source = state.variables[index];
        if (!source) return state;
        const copy: Variable = {
          ...source,
          id: `var-temp-${Math.random().toString(36).substring(2, 9)}`,
          name: `${source.name}_copy`,
          order: state.variables.length,
        };
        return { variables: [...state.variables, copy], isDraft: true };
      }),

      reorderVariables: (startIndex, endIndex) => set((state) => {
        const result = Array.from(state.variables);
        const [removed] = result.splice(startIndex, 1);
        result.splice(endIndex, 0, removed);
        return {
          variables: result.map((v, i) => ({ ...v, order: i })),
          isDraft: true,
        };
      }),

      setCurrentIndex: (index) => set({ currentVariableIndex: index }),

      saveDraft: () => set({ isDraft: false }),

      loadDraft: (projectId) => {
        const state = get();
        if (state.projectId === projectId) {
          return;
        }
        set({ variables: [], currentVariableIndex: 0, projectId, isDraft: false });
      },

      clearDraft: () => set({
        variables: [],
        currentVariableIndex: 0,
        isDraft: false,
      }),

      reset: () => set({
        variables: [],
        currentVariableIndex: 0,
        isDraft: false,
        projectId: null,
      }),
    }),
    {
      name: 'research-tool-schema-wizard',
      version: 1,
    }
  )
);
