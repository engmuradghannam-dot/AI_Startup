import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation } from 'react-query'
import { Send, Bot, User, Sparkles, Loader2, MessageSquare, Zap, Brain, Trash2, Copy, Check } from 'lucide-react'
import { agentsApi } from '../services/api'
import toast from 'react-hot-toast'

interface Message {
  id: string
  role: 'user' | 'agent' | 'system'
  content: string
  timestamp: Date
  agentName?: string
  isLoading?: boolean
}

interface Agent {
  id: string
  name: string
  role: string
  status: string
}

export default function AgentChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'system',
      content: '👋 Welcome to AI Startup Agent Console! Select an agent from the sidebar or enable Auto-Select.',
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [autoSelect, setAutoSelect] = useState(true)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: agents, isLoading: agentsLoading } = useQuery(
    'agents',
    () => agentsApi.list().then(r => r.data),
    { refetchInterval: 30000 }
  )

  const executeMutation = useMutation(
    async ({ agentId, task }: { agentId: string; task: any }) => {
      const response = await agentsApi.execute(agentId, task)
      return response.data
    },
    {
      onSuccess: (data) => {
        const newMessage: Message = {
          id: Date.now().toString(),
          role: 'agent',
          content: data.result || data.response || JSON.stringify(data, null, 2),
          timestamp: new Date(),
          agentName: selectedAgent?.name || 'AI Agent',
        }
        setMessages(prev => [...prev.filter(m => !m.isLoading), newMessage])
      },
      onError: (error: any) => {
        const errorMessage: Message = {
          id: Date.now().toString(),
          role: 'system',
          content: `❌ Error: ${error.response?.data?.detail || error.message || 'Failed to get response'}`,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev.filter(m => !m.isLoading), errorMessage])
      },
    }
  )

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    const loadingMessage: Message = {
      id: 'loading',
      role: 'agent',
      content: '',
      timestamp: new Date(),
      isLoading: true,
      agentName: selectedAgent?.name || 'AI Agent',
    }

    setMessages(prev => [...prev, userMessage, loadingMessage])
    setInput('')

    let targetAgent = selectedAgent
    if (autoSelect && !selectedAgent && agents?.length > 0) {
      targetAgent = agents[0]
      setSelectedAgent(targetAgent)
    }

    if (!targetAgent) {
      setMessages(prev => [
        ...prev.filter(m => !m.isLoading),
        {
          id: Date.now().toString(),
          role: 'system',
          content: '⚠️ No agent available. Please create an agent first.',
          timestamp: new Date(),
        }
      ])
      return
    }

    executeMutation.mutate({
      agentId: targetAgent.id,
      task: {
        name: 'Chat Task',
        description: input.trim(),
        task_type: 'chat',
        parameters: { mode: 'interactive' },
        context: { auto_selected: autoSelect },
      }
    })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const copyMessage = (content: string, id: string) => {
    navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
    toast.success('Copied to clipboard')
  }

  const clearChat = () => {
    setMessages([{
      id: 'welcome',
      role: 'system',
      content: '👋 Chat cleared! Start a new conversation.',
      timestamp: new Date(),
    }])
    setSelectedAgent(null)
  }

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Helper for agent card class
  const getAgentCardClass = (agent: Agent) => {
    if (selectedAgent?.id === agent.id) {
      return 'w-full text-left p-3 rounded-lg bg-primary-50 border border-primary-200'
    }
    return 'w-full text-left p-3 rounded-lg hover:bg-gray-50 border border-transparent'
  }

  // Helper for status dot
  const getStatusDot = (status: string) => {
    if (status === 'active') return 'w-2 h-2 rounded-full bg-green-500'
    return 'w-2 h-2 rounded-full bg-gray-400'
  }

  // Helper for status badge
  const getStatusBadge = (status: string) => {
    if (status === 'active') return 'text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700'
    return 'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600'
  }

  // Helper for message alignment
  const getMessageAlign = (role: string) => {
    if (role === 'user') return 'flex justify-end'
    return 'flex justify-start'
  }

  // Helper for avatar class
  const getAvatarClass = (role: string) => {
    if (role === 'user') return 'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-primary-600'
    if (role === 'system') return 'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-500'
    return 'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-br from-purple-500 to-blue-500'
  }

  // Helper for bubble class
  const getBubbleClass = (role: string) => {
    if (role === 'user') return 'rounded-2xl px-4 py-3 bg-primary-600 text-white'
    if (role === 'system') return 'rounded-2xl px-4 py-3 bg-gray-100 text-gray-700 border border-gray-200'
    return 'rounded-2xl px-4 py-3 bg-white border border-gray-200 text-gray-800 shadow-sm'
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] -mx-6 -mt-6">
      {/* Sidebar */}
      <div className="w-72 bg-white border-r border-gray-200 flex flex-col">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 flex items-center">
            <Bot className="w-5 h-5 mr-2 text-primary-600" />
            AI Agents
          </h2>
          <p className="text-xs text-gray-500 mt-1">{agents?.length || 0} agents available</p>
        </div>

        {/* Auto Select */}
        <div className="p-3">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input type="checkbox" checked={autoSelect} onChange={(e) => { setAutoSelect(e.target.checked); if (e.target.checked) setSelectedAgent(null) }} className="w-4 h-4 text-primary-600 rounded border-gray-300" />
            <span className="text-sm text-gray-700">Auto-Select Agent</span>
            <Sparkles className="w-4 h-4 text-yellow-500" />
          </label>
        </div>

        {/* Agent List */}
        <div className="flex-1 overflow-y-auto">
          {agentsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
            </div>
          ) : (
            <div className="space-y-1 px-2">
              {agents?.map((agent: Agent) => (
                <button key={agent.id} onClick={() => { setSelectedAgent(agent); setAutoSelect(false) }} className={getAgentCardClass(agent)}>
                  <div className="flex items-center space-x-2">
                    <div className={getStatusDot(agent.status)} />
                    <span className="font-medium text-sm text-gray-900 truncate">{agent.name}</span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-500 capitalize">{agent.role}</span>
                    <span className={getStatusBadge(agent.status)}>{agent.status}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Clear Chat */}
        <div className="p-3 border-t border-gray-200">
          <button onClick={clearChat} className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg">
            <Trash2 className="w-4 h-4" />
            <span>Clear Chat</span>
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <MessageSquare className="w-5 h-5 text-primary-600" />
            <div>
              <h1 className="font-semibold text-gray-900">Agent Console</h1>
              {selectedAgent ? (
                <p className="text-xs text-gray-500">
                  Talking with <span className="font-medium text-primary-600">{selectedAgent.name}</span> ({selectedAgent.role})
                </p>
              ) : autoSelect ? (
                <p className="text-xs text-gray-500 flex items-center">
                  <Sparkles className="w-3 h-3 mr-1 text-yellow-500" />
                  Auto-selecting best agent
                </p>
              ) : (
                <p className="text-xs text-gray-500">Select an agent to start</p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-yellow-500" />
            <span className="text-xs text-gray-500">Powered by Groq AI</span>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={getMessageAlign(message.role)}>
              <div className="max-w-3xl flex items-start space-x-3">
                {/* Avatar */}
                <div className={getAvatarClass(message.role)}>
                  {message.role === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : message.role === 'system' ? (
                    <Brain className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>

                {/* Message Bubble */}
                <div className="flex-1 flex flex-col">
                  <div className={getBubbleClass(message.role)}>
                    {message.isLoading ? (
                      <div className="flex items-center space-x-2 py-2">
                        <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                        <span className="text-sm text-gray-500">Thinking...</span>
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </div>
                    )}
                  </div>

                  {/* Meta Info */}
                  <div className="flex items-center space-x-2 mt-1 px-1">
                    <span className="text-xs text-gray-400">{formatTime(message.timestamp)}</span>
                    {message.agentName && (
                      <span className="text-xs text-primary-500 font-medium">{message.agentName}</span>
                    )}
                    {!message.isLoading && message.role !== 'user' && (
                      <button onClick={() => copyMessage(message.content, message.id)} className="text-gray-400 hover:text-gray-600">
                        {copiedId === message.id ? (
                          <Check className="w-3 h-3 text-green-500" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 px-6 py-4">
          <div className="flex items-end space-x-3 max-w-4xl mx-auto">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={selectedAgent ? `Ask ${selectedAgent.name} anything...` : autoSelect ? "Describe your task..." : "Select an agent first..."}
                rows={1}
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none max-h-32"
                style={{ minHeight: '48px' }}
              />
              <div className="absolute right-3 bottom-3 text-xs text-gray-400">
                {input.length > 0 && `${input.length} chars`}
              </div>
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || executeMutation.isLoading}
              className="flex-shrink-0 p-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {executeMutation.isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-400 text-center mt-2">Press Enter to send, Shift+Enter for new line</p>
        </div>
      </div>
    </div>
  )
}
