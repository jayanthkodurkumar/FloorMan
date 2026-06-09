import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Message } from '../types'

interface ChatState {
  sessionId: string | null
  messages: Message[]
  loading: boolean
  setSessionId: (id: string) => void
  setMessages: (msgs: Message[]) => void
  addMessage: (msg: Message) => void
  setLoading: (v: boolean) => void
  resetChat: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      sessionId: null,
      messages: [],
      loading: false,
      setSessionId: (id) => set({ sessionId: id }),
      setMessages: (msgs) => set({ messages: msgs }),
      addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
      setLoading: (v) => set({ loading: v }),
      resetChat: () => set({ sessionId: null, messages: [] }),
    }),
    {
      name: 'chat',
      partialize: (s) => ({ sessionId: s.sessionId }),
    }
  )
)
