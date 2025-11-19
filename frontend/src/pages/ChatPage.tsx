import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon, TrashIcon, ArrowPathIcon, MicrophoneIcon, StopIcon } from '@heroicons/react/24/outline'
import { useChat } from '../hooks/useChat'
import ChatMessage from '../components/ChatMessage'
import LoadingSpinner from '../components/LoadingSpinner'

export default function ChatPage() {
  const [input, setInput] = useState('')
  const [userName, setUserName] = useState('')
  const [tempName, setTempName] = useState('')
  const [showNameModal, setShowNameModal] = useState(true)
  const [isRecording, setIsRecording] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const recognitionRef = useRef<any>(null)
  
  const {
    messages,
    sessionId,
    isConnected,
    isLoading,
    error,
    sendMessage,
    clearChat,
    resetSession,
  } = useChat()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus()
    
    // Load saved user name from localStorage
    const savedName = localStorage.getItem('mfAgentUserName')
    if (savedName) {
      setUserName(savedName)
      setShowNameModal(false)
    }
  }, [])

  const handleNameSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (tempName.trim()) {
      const name = tempName.trim()
      setUserName(name)
      localStorage.setItem('mfAgentUserName', name)
      setShowNameModal(false)
      inputRef.current?.focus()
    }
  }

  const handleSkipName = () => {
    setShowNameModal(false)
    inputRef.current?.focus()
  }

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsSupported(true)
      
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-IN' // Indian English
      
      recognition.onresult = (event: any) => {
        let interimTranscript = ''
        let finalTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' '
          } else {
            interimTranscript += transcript
          }
        }
        
        if (finalTranscript) {
          setInput((prev) => prev + finalTranscript)
        }
      }
      
      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsRecording(false)
      }
      
      recognition.onend = () => {
        setIsRecording(false)
      }
      
      recognitionRef.current = recognition
    }
  }, [])

  const toggleRecording = () => {
    if (!recognitionRef.current) return
    
    if (isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
    } else {
      recognitionRef.current.start()
      setIsRecording(true)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim() || isLoading) return

    const message = input.trim()
    setInput('')
    
    // If this is the first message and user has a name, send a greeting first
    if (messages.length === 0 && userName) {
      await sendMessage(`Hi! I'm ${userName}.`, userName)
      // Small delay before sending the actual question
      setTimeout(async () => {
        await sendMessage(message, userName)
      }, 500)
    } else {
      await sendMessage(message, userName || undefined)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const isFirstTime = messages.length === 0

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-[#0B1120]">
      {/* Name Modal */}
      {showNameModal && messages.length === 0 && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="card max-w-md w-full mx-4 animate-slide-up">
            <div className="text-center mb-6">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/50">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Welcome to MF Agent! 👋</h3>
              <p className="text-gray-400">What should I call you?</p>
            </div>
            
            <form onSubmit={handleNameSubmit} className="space-y-4">
              <input
                type="text"
                value={tempName}
                onChange={(e) => setTempName(e.target.value)}
                placeholder="Enter your name..."
                className="w-full px-4 py-3 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all duration-300"
                autoFocus
                maxLength={50}
              />
              
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={!tempName.trim()}
                  className="flex-1 btn-primary disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Continue
                </button>
                <button
                  type="button"
                  onClick={handleSkipName}
                  className="btn-secondary"
                >
                  Skip
                </button>
              </div>
            </form>
            
            <p className="text-xs text-gray-500 text-center mt-4">
              Your name helps me personalize your experience
            </p>
          </div>
        </div>
      )}

      {/* Welcome message for first-time users */}
      {isFirstTime && (
        <div className="flex-1 flex items-center justify-center p-6 animate-fade-in">
          <div className="max-w-2xl text-center">
            {/* Icon with gradient background */}
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full opacity-20 blur-xl animate-pulse"></div>
              <div className="relative w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-2xl shadow-purple-500/50">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-4l-4 4v-4z" />
                </svg>
              </div>
            </div>

            {/* Welcome text with gradient - personalized */}
            <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
              {userName ? `Hello ${userName}! 👋` : 'Welcome to MF Agent'}
            </h2>
            <p className="text-gray-400 mb-8 text-lg leading-relaxed">
              {userName 
                ? `I'm here to help you with mutual funds, ${userName}. Let's explore investment opportunities together!`
                : 'Your AI-powered mutual funds assistant. I can help you discover funds, analyze performance, compare options, and provide investment insights using real-time data.'
              }
            </p>
            
            {/* Suggestion cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-8">
              <button 
                onClick={() => {
                  setInput("What is the NAV of HDFC Top 100 Fund?")
                  inputRef.current?.focus()
                }}
                className="group p-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 text-left hover:scale-105"
              >
                <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">📊</div>
                <div className="text-sm text-gray-300 font-medium">Check NAV</div>
                <div className="text-xs text-gray-500 mt-1">Get current fund prices</div>
              </button>

              <button 
                onClick={() => {
                  setInput("Compare SBI Bluechip with ICICI Prudential Bluechip Fund")
                  inputRef.current?.focus()
                }}
                className="group p-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 text-left hover:scale-105"
              >
                <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">⚖️</div>
                <div className="text-sm text-gray-300 font-medium">Compare Funds</div>
                <div className="text-xs text-gray-500 mt-1">Side-by-side analysis</div>
              </button>

              <button 
                onClick={() => {
                  setInput("Show me top performing large cap funds")
                  inputRef.current?.focus()
                }}
                className="group p-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl hover:bg-white/10 hover:border-purple-500/30 transition-all duration-300 text-left hover:scale-105"
              >
                <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">🏆</div>
                <div className="text-sm text-gray-300 font-medium">Top Performers</div>
                <div className="text-xs text-gray-500 mt-1">Best funds by category</div>
              </button>
            </div>

            <div className="text-xs text-gray-500 flex items-center justify-center gap-2">
              <div className="h-1 w-1 bg-gray-600 rounded-full"></div>
              <span>Powered by real-time data and advanced AI</span>
              <div className="h-1 w-1 bg-gray-600 rounded-full"></div>
            </div>
          </div>
        </div>
      )}

      {/* Messages area */}
      {messages.length > 0 && (
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Session info with glassmorphism - personalized */}
          <div className="flex items-center justify-between mb-4 p-3 bg-white/5 backdrop-blur-xl rounded-xl border border-white/10">
            <div className="flex items-center space-x-3">
              <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-400 shadow-lg shadow-green-400/50' : 'bg-red-400 shadow-lg shadow-red-400/50'} animate-pulse`} />
              <div className="flex flex-col">
                <span className="text-sm text-white font-medium">
                  {userName ? `${userName}'s Session` : 'Active Session'}
                </span>
                <span className="text-xs text-gray-500">
                  {isConnected ? 'Connected' : 'Disconnected'}
                  {sessionId && ` • ${sessionId.substring(0, 8)}...`}
                </span>
              </div>
            </div>
            
            <div className="flex space-x-2">
              {userName && (
                <button
                  onClick={() => setShowNameModal(true)}
                  className="group flex items-center px-3 py-1.5 text-sm text-gray-400 hover:text-purple-400 transition-all duration-300 rounded-lg hover:bg-purple-500/10"
                  title="Change name"
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Edit
                </button>
              )}
              <button
                onClick={clearChat}
                className="group flex items-center px-3 py-1.5 text-sm text-gray-400 hover:text-red-400 transition-all duration-300 rounded-lg hover:bg-red-500/10"
                title="Clear chat"
              >
                <TrashIcon className="w-4 h-4 mr-1 group-hover:scale-110 transition-transform" />
                Clear
              </button>
              <button
                onClick={resetSession}
                className="group flex items-center px-3 py-1.5 text-sm text-gray-400 hover:text-purple-400 transition-all duration-300 rounded-lg hover:bg-purple-500/10"
                title="Reset session"
              >
                <ArrowPathIcon className="w-4 h-4 mr-1 group-hover:rotate-180 transition-transform duration-500" />
                Reset
              </button>
            </div>
          </div>

          {/* Messages */}
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              userName={userName}
            />
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="chat-bubble-bot flex items-center space-x-3">
                <LoadingSpinner size="small" />
                <span className="text-gray-400">
                  {userName ? `Let me help you with that, ${userName}...` : 'AI is thinking...'}
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="mx-4 mb-4 p-4 bg-red-500/10 backdrop-blur-xl border border-red-500/30 rounded-xl">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Input area with glassmorphism */}
      <div className="border-t border-white/10 bg-[#0B1120]/80 backdrop-blur-xl p-4">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={userName ? `Ask me anything, ${userName}...` : "Ask me anything about mutual funds..."}
              rows={1}
              className="w-full px-4 py-3 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 resize-none transition-all duration-300"
              style={{ minHeight: '48px', maxHeight: '120px' }}
              disabled={isLoading}
            />
          </div>
          
          {/* Microphone button */}
          {isSupported && (
            <button
              type="button"
              onClick={toggleRecording}
              disabled={isLoading}
              className={`flex items-center justify-center px-4 py-3 min-w-[48px] rounded-xl border transition-all duration-300 ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 border-red-500 shadow-lg shadow-red-500/50 animate-pulse'
                  : 'bg-white/5 hover:bg-white/10 border-white/10 hover:border-purple-500/30'
              } disabled:opacity-40 disabled:cursor-not-allowed`}
              title={isRecording ? 'Stop recording' : 'Start voice input'}
            >
              {isRecording ? (
                <StopIcon className="w-5 h-5 text-white" />
              ) : (
                <MicrophoneIcon className="w-5 h-5 text-gray-300 group-hover:text-white" />
              )}
            </button>
          )}
          
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center px-5 py-3 min-w-[48px]"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </form>
        
        <div className="mt-2 text-xs text-gray-500 text-center flex items-center justify-center gap-2">
          {isRecording && (
            <>
              <span className="flex items-center gap-1 text-red-400 animate-pulse">
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                Recording...
              </span>
              <span className="text-gray-600">•</span>
            </>
          )}
          <kbd className="px-2 py-0.5 bg-white/5 border border-white/10 rounded text-[10px]">Enter</kbd>
          <span>to send</span>
          <span className="text-gray-600">•</span>
          <kbd className="px-2 py-0.5 bg-white/5 border border-white/10 rounded text-[10px]">Shift+Enter</kbd>
          <span>for new line</span>
        </div>
      </div>
    </div>
  )
}
