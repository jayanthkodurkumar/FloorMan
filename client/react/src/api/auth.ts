import api from './client'
import type { AuthResponse } from '../types'

export const signIn = (email: string, password: string) =>
  api.post<AuthResponse>('/api/auth/signin', { email, password })

export const signUp = (email: string, password: string, role: string) =>
  api.post<AuthResponse>('/api/auth/signup', { email, password, role })
