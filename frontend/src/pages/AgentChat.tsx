import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery } from 'react-query'
import { 
  Send, Bot, User, Settings, Mic, MicOff, Paperclip, 
  Image, Video, FileText, Monitor, X, Volume2, VolumeX,
  Brain, Sparkles, Trash2, Download, Cpu, Cloud, Zap,
  Server, CheckCircle, AlertCircle, Loader2
} from 'lucide-react'
import { aiChatApi, localLlmApi } from '../services/api'
import axios from 'axios'
import toast from 'react-hot-toast'

interface ChatMessage {
  id: string
  role: 'user' | 'agent' | 'system'
  content: string
  agentName?: string
  agentId?: string
  timestamp: string
  source?: string
  provider?: string
  agentTrace?: any[]
}

interface AIModel {
  id: string
  name: string
  provider: string
  size: string
  parameters: string
  speed: string
  capabilities: string[]
  best_for: string[]
  ram_required_mb: number
  installed?: boolean
}

interface AIAgent {
  name: string
  specialty: string
  description: string
  skills: string[]
  model: string
}

export default function AgentChat() {
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string>('auto')
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [agentMode, setAgentMode] = useState<string>('auto')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showAgentTrace, setShowAgentTrace] = useState(false)
  const [lastTrace, setLastTrace] = useState<any[]>([])
  const [localLlmStatus, setLocalLlmStatus] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Fetch AI health status
  const { data: healthData } = useQuery(
    'ai-health',
    () => aiChatApi.getHealth(),
    { refetchInterval: 30000 }
  )

  // Fetch available models
  const { data: modelsData } = useQuery(
    'ai-models',
    () => aiChatApi.getModels(),
    { refetchInterval: 60000 }
  )

  // Fetch available agents
  const { data: agentsData } = useQuery(
    'ai-agents',
    () => aiChatApi.getAgents(),
    { refetchInterval: 60000 }
  )

  const models: AIModel[] = modelsData || []
  const agents: AIAgent[] = agentsData || []

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  // Check local LLM status
  useEffect(() => {
    const checkLocalLlm = async () => {
      try {
        const status = await localLlmApi.getHealth()
        setLocalLlmStatus(status)
      } catch (e) {
        setLocalLlmStatus({ status: 'unavailable' })
      }
    }
    checkLocalLlm()
  }, [])

  const generateId = () => Math.random().toString(36).substring(2, 10)

  const handleSend = async () => {
    if (!message.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    }

    setChatHistory(prev => [...prev, userMessage])
    setMessage('')
    setIsLoading(true)

    try {
      const messages = chatHistory
        .filter(m => m.role !== 'system')
        .map(m => ({ role: m.role === 'agent' ? 'assistant' : m.role, content: m.content }))
        .concat([{ role: 'user', content: message }])

      const response = await aiChatApi.chat(messages, {
        model: selectedModel || undefined,
        agent_mode: agentMode,
      })

      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'agent',
        content: response.choices?.[0]?.message?.content || 'No response',
        timestamp: new Date().toISOString(),
        source: response.source,
        provider: response.provider,
        agentTrace: response.agent_trace,
      }

      if (response.agent_trace) {
        setLastTrace(response.agent_trace)
      }

      setChatHistory(prev => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Chat error:', error)
      toast.error(error.response?.data?.detail || 'Failed to get response')

      const errorMessage: ChatMessage = {
        id: generateId(),
        role: 'system',
        content: `Error: ${error.response?.data?.detail || error.message}. Make sure Ollama is running locally or configure GROQ_API_KEY.`,
        timestamp: new Date().toISOString(),
      }
      setChatHistory(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    setChatHistory([])
    setLastTrace([])
    toast.success('Chat cleared')
  }

  const exportChat = () => {
    const data = JSON.stringify(chatHistory, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chat-export-${new Date().toISOString()}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Chat exported')
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col">
        {/* Status Panel */}
        <div className="p-4 border-b border-gray-800">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            AI Status
          </h3>

          {/* Local LLM Status */}
          <div className="mb-3">
            <div className="flex items-center gap-2 mb-1">
              <Cpu className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-gray-300">Local LLM</span>
              {localLlmStatus?.status === 'healthy' ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <AlertCircle className="w-4 h-4 text-yellow-400" />
              )}
            </div>
            <div className="text-xs text-gray-500 ml-6">
              {localLlmStatus?.provider || 'Not connected'}
            </div>
          </div>

          {/* Groq Status */}
          <div className="mb-3">
            <div className="flex items-center gap-2 mb-1">
              <Cloud className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-gray-300">Groq Cloud</span>
              {healthData?.groq?.available ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <AlertCircle className="w-4 h-4 text-gray-500" />
              )}
            </div>
            <div className="text-xs text-gray-500 ml-6">
              {healthData?.groq?.available ? 'Available' : 'Not configured'}
            </div>
          </div>

          {/* Mode */}
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-gray-300">Mode:</span>
            <span className="text-xs px-2 py-0.5 bg-blue-900 text-blue-300 rounded-full">
              {healthData?.mode || 'auto'}
            </span>
          </div>
        </div>

        {/* Models */}
        <div className="p-4 border-b border-gray-800">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Models
          </h3>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">Auto-select</option>
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name} {model.installed ? '✓' : ''} ({model.provider})
              </option>
            ))}
          </select>

          {models.length === 0 && (
            <div className="mt-2 text-xs text-yellow-500">
              No models detected. Install Ollama and pull models.
            </div>
          )}
        </div>

        {/* Agent Mode */}
        <div className="p-4 border-b border-gray-800">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Agent Mode
          </h3>
          <select
            value={agentMode}
            onChange={(e) => setAgentMode(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-blue-500"
          >
            <option value="auto">Auto (detect complexity)</option>
            <option value="single">Single Agent (fast)</option>
            <option value="multi">Multi-Agent (hierarchical)</option>
            <option value="parallel">Multi-Agent (parallel)</option>
            <option value="swarm">Swarm (collaborative)</option>
          </select>
        </div>

        {/* Agents */}
        <div className="p-4 flex-1 overflow-y-auto">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Specialized Agents
          </h3>
          <div className="space-y-2">
            {agents.map((agent) => (
              <div
                key={agent.name}
                className="p-3 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-2 mb-1">
                  <Bot className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-medium text-gray-200 capitalize">
                    {agent.name}
                  </span>
                </div>
                <div className="text-xs text-gray-500">{agent.specialty}</div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {agent.skills.slice(0, 3).map((skill) => (
                    <span
                      key={skill}
                      className="text-xs px-1.5 py-0.5 bg-gray-700 text-gray-400 rounded"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-gray-950">
        {/* Header */}
        <div className="h-14 border-b border-gray-800 flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-blue-400" />
            <div>
              <h1 className="text-lg font-semibold text-white">AI Agent Chat</h1>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>Local LLM First</span>
                <span>•</span>
                <span>Multi-Agent</span>
                <span>•</span>
                <span>10 Skills</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {lastTrace.length > 0 && (
              <button
                onClick={() => setShowAgentTrace(!showAgentTrace)}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                title="View Agent Trace"
              >
                <Sparkles className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={clearChat}
              className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
              title="Clear Chat"
            >
              <Trash2 className="w-5 h-5" />
            </button>
            <button
              onClick={exportChat}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              title="Export Chat"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Agent Trace Panel */}
        {showAgentTrace && lastTrace.length > 0 && (
          <div className="h-48 bg-gray-900 border-b border-gray-800 overflow-y-auto p-4">
            <h4 className="text-sm font-semibold text-gray-400 mb-2">Agent Execution Trace</h4>
            <div className="space-y-2">
              {lastTrace.map((trace, idx) => (
                <div key={idx} className="p-2 bg-gray-800 rounded text-xs">
                  <div className="flex items-center gap-2 mb-1">
                    <Bot className="w-3 h-3 text-blue-400" />
                    <span className="font-medium text-gray-300 capitalize">{trace.agent}</span>
                    {trace.provider && (
                      <span className="text-gray-500">({trace.provider})</span>
                    )}
                  </div>
                  <div className="text-gray-400 ml-5">{trace.thought_preview || trace.thought?.substring(0, 100)}...</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {chatHistory.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <Brain className="w-16 h-16 mb-4 text-gray-700" />
              <h2 className="text-xl font-semibold mb-2">Welcome to AI Agent Chat</h2>
              <p className="text-center max-w-md mb-4">
                Start a conversation with our multi-agent system powered by local LLMs.
                The system automatically detects task complexity and routes to the right agents.
              </p>
              <div className="flex gap-2">
                <span className="text-xs px-3 py-1 bg-gray-800 rounded-full">Local LLM</span>
                <span className="text-xs px-3 py-1 bg-gray-800 rounded-full">4 Agents</span>
                <span className="text-xs px-3 py-1 bg-gray-800 rounded-full">10 Skills</span>
              </div>
            </div>
          )}

          {chatHistory.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role !== 'user' && (
                <div className="w-8 h-8 rounded-lg bg-blue-900 flex items-center justify-center flex-shrink-0">
                  {msg.role === 'system' ? (
                    <AlertCircle className="w-4 h-4 text-yellow-400" />
                  ) : (
                    <Bot className="w-4 h-4 text-blue-400" />
                  )}
                </div>
              )}

              <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : msg.role === 'system'
                    ? 'bg-yellow-900/30 border border-yellow-800 text-yellow-200'
                    : 'bg-gray-800 text-gray-200'
                }`}
              >
                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>

                {msg.source && (
                  <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                    {msg.source === 'local' ? (
                      <Cpu className="w-3 h-3" />
                    ) : (
                      <Cloud className="w-3 h-3" />
                    )}
                    <span>{msg.provider} ({msg.source})</span>
                    {msg.agentTrace && (
                      <span>• {msg.agentTrace.length} agents</span>
                    )}
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-gray-700 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-gray-300" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-900 flex items-center justify-center">
                <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
              </div>
              <div className="bg-gray-800 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Sparkles className="w-4 h-4 animate-pulse" />
                  <span>Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-800 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end gap-2 bg-gray-900 rounded-xl border border-gray-700 p-2">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything... The AI will auto-detect complexity and use the right agents."
                className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none outline-none min-h-[44px] max-h-[200px] py-2 px-3"
                rows={1}
              />
              <button
                onClick={handleSend}
                disabled={!message.trim() || isLoading}
                className="p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
              <div className="flex items-center gap-4">
                <span>Press Enter to send</span>
                <span>Shift+Enter for new line</span>
              </div>
              <div className="flex items-center gap-2">
                {healthData?.local?.status === 'healthy' && (
                  <span className="flex items-center gap-1 text-green-400">
                    <Server className="w-3 h-3" />
                    Local LLM Active
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
