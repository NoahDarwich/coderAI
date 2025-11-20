import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

// TODO(Phase 2): Replace with real authentication
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        // Mock authentication - always succeeds
        await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate API call

        const mockUser: User = {
          id: '1',
          email,
          name: email.split('@')[0],
        };

        set({ user: mockUser, isAuthenticated: true });
      },

      register: async (name: string, email: string, password: string) => {
        // Mock registration - always succeeds
        await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate API call

        const mockUser: User = {
          id: '1',
          email,
          name,
        };

        set({ user: mockUser, isAuthenticated: true });
      },

      logout: () => {
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
