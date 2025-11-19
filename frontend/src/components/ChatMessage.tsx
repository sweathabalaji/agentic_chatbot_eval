import { formatDate } from '../utils'

interface ChatMessageProps {
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    isLoading?: boolean
  }
  userName?: string
}

export default function ChatMessage({ message, userName }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`chat-message flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'chat-bubble-user' : 'chat-bubble-bot'}`}>
        {/* Name header */}
        {isUser && userName && (
          <div className="text-xs font-semibold text-purple-600 mb-1">
            {userName}
          </div>
        )}
        {!isUser && (
          <div className="text-xs font-semibold text-purple-400 mb-1 flex items-center gap-1">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            MF Agent
          </div>
        )}
        
        {isUser ? (
          <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">{message.content}</p>
        ) : (
          <div className="text-white">
            <div className="whitespace-pre-wrap leading-relaxed prose prose-invert prose-sm max-w-none">
              {message.content}
            </div>
          </div>
        )}
        
        {/* Timestamp */}
        <div className={`text-[10px] mt-2 ${isUser ? 'text-gray-600' : 'text-gray-500'}`}>
          {formatDate(message.timestamp)}
        </div>
      </div>
    </div>
  )
}
