export default function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white border border-gray-100 shadow-xs px-4 py-3 rounded-2xl rounded-bl-sm flex items-center gap-1">
        <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
        <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
        <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" />
      </div>
    </div>
  )
}
