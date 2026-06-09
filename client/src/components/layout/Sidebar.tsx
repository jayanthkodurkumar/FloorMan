import { useEffect, useState } from 'react'
import { useAuthStore } from '../../store/authStore'
import { useChatStore } from '../../store/chatStore'
import { fetchSessions, fetchMessages } from '../../api/chat'

interface Session {
  id: string
  created_at: string
  first_message: string | null
}

export default function Sidebar() {
  const { email, role, clearAuth } = useAuthStore()
  const { sessionId, setSessionId, setMessages, resetChat } = useChatStore()
  const [sessions, setSessions] = useState<Session[]>([])

  const loadSessions = () => {
    fetchSessions()
      .then(({ data }) => setSessions(data))
      .catch(() => {})
  }

  useEffect(() => {
    loadSessions()
  }, [sessionId]) // reload when session changes (new conversation created)

  const handleSelectSession = (id: string) => {
    if (id === sessionId) return
    setSessionId(id)
    fetchMessages(id)
      .then(({ data }) =>
        setMessages(data.map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content })))
      )
      .catch(() => {})
  }

  const handleNewConversation = () => {
    resetChat()
  }

  const handleSignOut = () => {
    clearAuth()
    resetChat()
  }

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <aside className="w-64 shrink-0 bg-gray-950 text-white flex flex-col h-full">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-white/10">
        <p className="text-sm font-semibold tracking-tight">FloorMan</p>
        <p className="text-xs text-gray-400 mt-0.5">Knowledge Base</p>
      </div>

      {/* New conversation */}
      <div className="px-4 pt-4">
        <button
          onClick={handleNewConversation}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-300 hover:bg-white/10 transition-colors text-left"
        >
          <span className="text-base">+</span>
          New Conversation
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto px-4 py-2 flex flex-col gap-0.5 mt-2">
        {sessions.length === 0 && (
          <p className="text-xs text-gray-600 px-3 py-2">No conversations yet</p>
        )}
        {sessions.map((s) => (
          <button
            key={s.id}
            onClick={() => handleSelectSession(s.id)}
            className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors truncate ${
              s.id === sessionId
                ? 'bg-white/15 text-white'
                : 'text-gray-400 hover:bg-white/10 hover:text-gray-200'
            }`}
          >
            {s.first_message
              ? s.first_message.slice(0, 40) + (s.first_message.length > 40 ? '...' : '')
              : formatDate(s.created_at)}
          </button>
        ))}
      </div>

      {/* User info */}
      <div className="px-4 py-4 border-t border-white/10">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-semibold uppercase shrink-0">
            {email?.[0] ?? 'U'}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium truncate">{email}</p>
            <p className="text-xs text-gray-500 capitalize">{role}</p>
          </div>
        </div>
        <button
          onClick={handleSignOut}
          className="w-full px-3 py-2 text-xs text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors text-left"
        >
          Sign out
        </button>
      </div>
    </aside>
  )
}
