import Sidebar from '../components/layout/Sidebar'
import ChatWindow from '../components/chat/ChatWindow'

export default function ChatPage() {
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatWindow />
      </main>
    </div>
  )
}
