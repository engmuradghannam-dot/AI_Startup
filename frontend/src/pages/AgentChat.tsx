import { useState, useRef, useEffect } from 'react'
import { useQuery } from 'react-query'
import { Send, Bot, User, Loader2, MessageSquare } from 'lucide-react'
import { agentsApi } from '../services/api'

interface Message {
  id: string
  role: string
  content: string
  timestamp: Date
}

export default function AgentChat() {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'system', content: 'Welcome! Select an agent and start chatting.', timestamp: new Date() }
  ])
  const [input, setInput] = useState('')
  const [selectedAgentId, setSelectedAgentId] = useState<string>('')
  const [isSending, setIsSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: agentsResponse, isLoading: agentsLoading } = useQuery(
    'agents-list',
    () => agentsApi.list(),
    { retry: 1 }
  )

  const agents = agentsResponse?.data || []

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return

    const text = input.trim()
    setInput('')
    setIsSending(true)

    // Add user message
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    }])

    try {
      let agentId = selectedAgentId
      if (!agentId && agents.length > 0) {
        agentId = agents[0].id
        setSelectedAgentId(agentId)
      }

      if (!agentId) {
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          role: 'system',
          content: 'No agents available. Please create an agent first.',
          timestamp: new Date()
        }])
        setIsSending(false)
        return
      }

      const response = await agentsApi.execute(agentId, {
        name: 'Chat',
        description: text,
        task_type: 'chat'
      })

      setMessages(prev => [...prev, {
        id: (Date.now() + 2).toString(),
        role: 'agent',
        content: response.data?.result || response.data?.response || 'No response',
        timestamp: new Date()
      }])
    } catch (error: any) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 3).toString(),
        role: 'system',
        content: 'Error: ' + (error.message || 'Failed to send message'),
        timestamp: new Date()
      }])
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] -mx-6 -mt-6">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 flex items-center">
            <Bot className="w-5 h-5 mr-2 text-primary-600" />
            Agents
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {agentsLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
            </div>
          ) : (
            <div className="space-y-1">
              {agents.map((agent: any) => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgentId(agent.id)}
                  className={selectedAgentId === agent.id 
                    ? 'w-full text-left p-3 rounded-lg bg-primary-50 border border-primary-200 text-sm'
                    : 'w-full text-left p-3 rounded-lg hover:bg-gray-50 border border-transparent text-sm'
                  }
                >
                  <div className="font-medium text-gray-900">{agent.name}</div>
                  <div className="text-xs text-gray-500 capitalize">{agent.role}</div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center">
          <MessageSquare className="w-5 h-5 text-primary-600 mr-2" />
          <h1 className="font-semibold text-gray-900">Agent Chat</h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
              <div className="max-w-2xl flex items-start space-x-2">
                {msg.role !== 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}
                <div className={msg.role === 'user' 
                  ? 'bg-primary-600 text-white rounded-2xl px-4 py-2'
                  : msg.role === 'system'
                  ? 'bg-gray-100 text-gray-700 rounded-2xl px-4 py-2 border border-gray-200'
                  : 'bg-white text-gray-800 rounded-2xl px-4 py-2 border border-gray-200 shadow-sm'
                }>
                  <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            </div>
          ))}
          {isSending && (
            <div className="flex justify-start">
              <div className="max-w-2xl flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                </div>
                <div className="bg-white rounded-2xl px-4 py-2 border border-gray-200">
                  <span className="text-sm text-gray-500">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-white border-t border-gray-200 px-6 py-4">
          <div className="flex items-end space-x-2 max-w-4xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              rows={1}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              style={{ minHeight: '44px' }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isSending}
              className="p-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
