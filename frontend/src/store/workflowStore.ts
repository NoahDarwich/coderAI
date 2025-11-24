import { create } from 'zustand';

interface WorkflowState {
  currentStep: number;           // 1-5
  canProceed: boolean;

  // Actions
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setCanProceed: (canProceed: boolean) => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  currentStep: 1,
  canProceed: false,

  setStep: (step) => set({ currentStep: Math.max(1, Math.min(5, step)) }),
  nextStep: () => set((state) => ({
    currentStep: Math.min(5, state.currentStep + 1)
  })),
  prevStep: () => set((state) => ({
    currentStep: Math.max(1, state.currentStep - 1)
  })),
  setCanProceed: (canProceed) => set({ canProceed }),
}));
