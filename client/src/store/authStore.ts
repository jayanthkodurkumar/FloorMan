import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  token: string | null
  userId: string | null
  email: string | null
  role: string | null
  setAuth: (token: string, userId: string, email: string, role: string) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      userId: null,
      email: null,
      role: null,
      setAuth: (token, userId, email, role) =>
        set({ token, userId, email, role }),
      clearAuth: () =>
        set({ token: null, userId: null, email: null, role: null }),
    }),
    { name: 'auth' }
  )
)
