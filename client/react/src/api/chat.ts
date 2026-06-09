import api from './client'
import type { ChatResponse } from '../types'

export const createSession = () =>
  api.post<{ session_id: string }>('/api/chat/session')

export const sendMessage = (question: string, session_id: string, k = 3) =>
  api.post<ChatResponse>('/api/chat', { question, session_id, k })

export const fetchSessions = () =>
  api.get<{ id: string; created_at: string; first_message: string | null }[]>('/api/chat/sessions')

export const fetchMessages = (session_id: string) =>
  api.get<{ role: string; content: string; created_at: string }[]>(
    `/api/chat/sessions/${session_id}/messages`
  )

