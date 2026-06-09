import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '../../store/chatStore'
import { createSession, sendMessage, fetchMessages } from '../../api/chat'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

export default function ChatWindow() {
  const { sessionId, messages, loading, setSessionId, setMessages, addMessage, setLoading } =
    useChatStore()
  const [input, setInput] = useState('')
  const [hydrating, setHydrating] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  // On mount, if we have a persisted sessionId, load its messages from Supabase
  useEffect(() => {
    if (sessionId && messages.length === 0) {
      setHydrating(true)
      fetchMessages(sessionId)
        .then(({ data }) => {
          setMessages(data.map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content })))
        })
        .catch(() => {
          // Session may have expired or been deleted — reset
          useChatStore.getState().resetChat()
        })
        .finally(() => setHydrating(false))
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const ensureSession = async () => {
    if (sessionId) return sessionId
    const { data } = await createSession()
    setSessionId(data.session_id)
    return data.session_id
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    const question = input.trim()
    if (!question || loading) return

    setInput('')
    addMessage({ role: 'user', content: question })
    setLoading(true)

    try {
      const sid = await ensureSession()
      const { data } = await sendMessage(question, sid)
      addMessage({ role: 'assistant', content: data.answer, sources: data.sources })
    } catch {
      addMessage({
        role: 'assistant',
        content: 'Something went wrong. Please try again.',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-4">
        {hydrating && (
          <div className="flex-1 flex items-center justify-center text-sm text-gray-400">
            Loading conversation...
          </div>
        )}
        {!hydrating && messages.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center text-center gap-3 text-gray-400 select-none">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 flex items-center justify-center text-2xl">
              🏭
            </div>
            <p className="text-sm font-medium text-gray-500">Manufacturing Assistant</p>
            <p className="text-xs max-w-xs">
              Ask about SOPs, safety procedures, maintenance, quality control, or
              compliance requirements.
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-100 px-4 py-3 bg-white">
        <form onSubmit={handleSend} className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 disabled:text-gray-400 text-white text-sm font-medium rounded-xl transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
