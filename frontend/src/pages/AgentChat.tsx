import { useState, useEffect, useRef } from 'react'
import { useQuery } from 'react-query'
import {
  Send, Bot, User, Trash2, Download,
  Brain, Sparkles, Loader2, Cloud, CheckCircle, AlertCircle,
  Server, Zap, Mic, MicOff, Plus, Pencil, MessageSquare, Paperclip, X, FileText,
  Volume2, VolumeX
} from 'lucide-react'
import { aiChatApi } from '../services/api'
import toast from 'react-hot-toast'
import { useVoiceAssistant, ASSISTANT_NAME } from '../hooks/useVoiceAssistant'
import { useChatProjects } from '../hooks/useChatProjects'

interface ChatMessage {
  id: string
  role: 'user' | 'agent' | 'system'
  content: string
  agentName?: string
  timestamp: string
  source?: string
  provider?: string
  agentTrace?: any[]
  attachmentName?: string
}

interface PendingAttachment {
  name: string
  contentType: string
  data: string // UTF-8 text, or base64 for images
  isBase64: boolean
}

const TEXT_EXTENSIONS = /\.(txt|md|markdown|json|csv|log|py|js|jsx|ts|tsx|html|css|yml|yaml|xml|sh|java|c|cpp|go|rs|rb|php|sql)$/i
const MAX_ATTACHMENT_CHARS = 15000

interface AIModel {
  id: string
  name: string
  provider: string
  speed: string
  capabilities: string[]
  best_for: string[]
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
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [agentMode, setAgentMode] = useState<string>('auto')
  const [isLoading, setIsLoading] = useState(false)
  const [showAgentTrace, setShowAgentTrace] = useState(false)
  const [lastTrace, setLastTrace] = useState<any[]>([])
  const [pendingAttachment, setPendingAttachment] = useState<PendingAttachment | null>(null)
  const [renamingProjectId, setRenamingProjectId] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const [autoSpeak, setAutoSpeak] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const prevProjectIdRef = useRef<string | null>(null)

  const {
    projects,
    activeProjectId,
    activeProject,
    switchProject,
    createProject,
    renameProject,
    deleteProject,
    updateActiveMessages,
  } = useChatProjects()

  const { data: healthData } = useQuery('ai-health', () => aiChatApi.getHealth(), { refetchInterval: 30000 })
  const { data: modelsData } = useQuery('ai-models', () => aiChatApi.getModels(), { refetchInterval: 60000 })
  const { data: agentsData } = useQuery('ai-agents', () => aiChatApi.getAgents(), { refetchInterval: 60000 })

  const models: AIModel[] = modelsData || []
  const agents: AIAgent[] = agentsData || []

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  // Load this project's saved conversation whenever we switch to it
  useEffect(() => {
    if (!activeProjectId || prevProjectIdRef.current === activeProjectId) return
    prevProjectIdRef.current = activeProjectId
    setChatHistory((activeProject?.messages as ChatMessage[]) || [])
    setLastTrace([])
  }, [activeProjectId, activeProject])

  // Persist every change back to the active project so it survives closing/reopening the app
  useEffect(() => {
    if (!activeProjectId || prevProjectIdRef.current !== activeProjectId) return
    updateActiveMessages(chatHistory)
  }, [chatHistory, activeProjectId, updateActiveMessages])

  const generateId = () => Math.random().toString(36).substring(2, 10)

  const handleSend = async (overrideText?: string): Promise<string | null> => {
    const attachment = overrideText === undefined ? pendingAttachment : null
    const textToSend = overrideText ?? message ?? ''
    if ((!textToSend.trim() && !attachment) || isLoading) return null
    const effectiveText = textToSend.trim() || `Please look at the attached file: ${attachment?.name}`

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: effectiveText,
      timestamp: new Date().toISOString(),
      attachmentName: attachment?.name,
    }

    setChatHistory(prev => [...prev, userMessage])
    if (overrideText === undefined) {
      setMessage('')
      setPendingAttachment(null)
    }
    setIsLoading(true)

    try {
      const messages = chatHistory
        .filter(m => m.role !== 'system')
        .map(m => ({ role: m.role === 'agent' ? 'assistant' : m.role, content: m.content }))
        .concat([{ role: 'user', content: effectiveText }])

      const response = await aiChatApi.chat(messages, {
        model: selectedModel || undefined,
        agent_mode: agentMode,
        attachment: attachment
          ? { name: attachment.name, content_type: attachment.contentType, data: attachment.data, is_base64: attachment.isBase64 }
          : undefined,
      })

      const replyContent = response.choices?.[0]?.message?.content || 'No response'

      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'agent',
        content: replyContent,
        timestamp: new Date().toISOString(),
        source: response.source,
        provider: response.provider,
        agentTrace: response.agent_trace,
      }

      if (response.agent_trace) {
        setLastTrace(response.agent_trace)
      }

      setChatHistory(prev => [...prev, assistantMessage])
      // speak the reply if auto-speak is on, or this came from a voice command (Nova always replies out loud)
      if (autoSpeak || overrideText !== undefined) speak(replyContent)
      return replyContent
    } catch (error: any) {
      console.error('Chat error:', error)
      const detail = error.response?.data?.detail || error.message
      toast.error(detail || 'Failed to get response')

      const errorMessage: ChatMessage = {
        id: generateId(),
        role: 'system',
        content: `Error: ${detail}. Please check your API configuration.`,
        timestamp: new Date().toISOString(),
      }
      setChatHistory(prev => [...prev, errorMessage])
      return null
    } finally {
      setIsLoading(false)
    }
  }

  const { status: voiceStatus, liveTranscript, toggle: toggleVoice, speak, isSupported: voiceSupported } = useVoiceAssistant({
    // handleSend itself calls speak() for voice-triggered commands, so just send here
    onCommand: (transcript) => { handleSend(transcript) },
    onError: (msg) => toast.error(msg),
  })

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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return

    const isImage = file.type.startsWith('image/')
    const isText = file.type.startsWith('text/') || TEXT_EXTENSIONS.test(file.name) || file.type === 'application/json'

    if (!isImage && !isText) {
      toast.error('Unsupported file type. Attach a text/code file or an image.')
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result as string
      if (isImage) {
        // data URL looks like "data:image/png;base64,AAAA..." - keep just the base64 part
        const base64 = result.split(',')[1] || ''
        setPendingAttachment({ name: file.name, contentType: file.type, data: base64, isBase64: true })
      } else {
        const truncated = result.length > MAX_ATTACHMENT_CHARS
          ? result.slice(0, MAX_ATTACHMENT_CHARS) + '\n...[truncated]'
          : result
        setPendingAttachment({ name: file.name, contentType: file.type || 'text/plain', data: truncated, isBase64: false })
      }
    }
    reader.onerror = () => toast.error('Could not read file')

    if (isImage) reader.readAsDataURL(file)
    else reader.readAsText(file)
  }

  const startRenaming = (id: string, currentName: string) => {
    setRenamingProjectId(id)
    setRenameValue(currentName)
  }

  const commitRename = () => {
    if (renamingProjectId && renameValue.trim()) {
      renameProject(renamingProjectId, renameValue.trim())
    }
    setRenamingProjectId(null)
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col">
        {/* Conversations Panel */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
              Conversations
            </h3>
            <button
              onClick={() => createProject()}
              className="p-1 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
              title="New conversation"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => switchProject(project.id)}
                className={`group flex items-center gap-2 px-2 py-1.5 rounded-lg cursor-pointer text-sm ${
                  project.id === activeProjectId ? 'bg-blue-900/40 text-blue-200' : 'text-gray-400 hover:bg-gray-800'
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5 flex-shrink-0" />
                {renamingProjectId === project.id ? (
                  <input
                    autoFocus
                    value={renameValue}
                    onChange={(e) => setRenameValue(e.target.value)}
                    onBlur={commitRename}
                    onKeyDown={(e) => { if (e.key === 'Enter') commitRename(); if (e.key === 'Escape') setRenamingProjectId(null) }}
                    onClick={(e) => e.stopPropagation()}
                    className="flex-1 bg-gray-950 border border-gray-700 rounded px-1 text-xs text-white outline-none"
                  />
                ) : (
                  <span className="flex-1 truncate">{project.name}</span>
                )}
                <button
                  onClick={(e) => { e.stopPropagation(); startRenaming(project.id, project.name) }}
                  className="opacity-0 group-hover:opacity-100 hover:text-white flex-shrink-0"
                  title="Rename"
                >
                  <Pencil className="w-3 h-3" />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); deleteProject(project.id) }}
                  className="opacity-0 group-hover:opacity-100 hover:text-red-400 flex-shrink-0"
                  title="Delete"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Status Panel */}
        <div className="p-4 border-b border-gray-800">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            AI Status
          </h3>

          {/* Cloud Provider Status */}
          <div className="mb-3">
            <div className="flex items-center gap-2 mb-1">
              <Cloud className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-gray-300">
                {healthData?.cloud?.provider ? `${healthData.cloud.provider} Cloud` : 'Cloud AI'}
              </span>
              {healthData?.cloud?.available ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <AlertCircle className="w-4 h-4 text-yellow-400" />
              )}
            </div>
            <div className="text-xs text-gray-500 ml-6">
              {healthData?.cloud?.available ? 'Connected' : 'Configure a provider in Settings'}
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
                {model.name} ({model.provider})
              </option>
            ))}
          </select>
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
                <span>Groq Cloud</span>
                <span>•</span>
                <span>Multi-Agent</span>
                <span>•</span>
                <span>10 Skills</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {'speechSynthesis' in window && (
              <button
                onClick={() => setAutoSpeak(!autoSpeak)}
                className={`p-2 rounded-lg transition-colors ${
                  autoSpeak ? 'text-white bg-purple-600' : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
                title={autoSpeak ? 'Stop reading replies aloud' : 'Read replies aloud'}
              >
                {autoSpeak ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>
            )}
            {voiceSupported && (
              <button
                onClick={toggleVoice}
                className={`p-2 rounded-lg transition-colors ${
                  voiceStatus === 'off'
                    ? 'text-gray-400 hover:text-white hover:bg-gray-800'
                    : voiceStatus === 'listening-for-command'
                    ? 'text-white bg-blue-600 animate-pulse'
                    : voiceStatus === 'speaking'
                    ? 'text-white bg-purple-600'
                    : 'text-green-400 bg-gray-800'
                }`}
                title={voiceStatus === 'off' ? `Enable "Hey ${ASSISTANT_NAME}" voice control` : `Disable ${ASSISTANT_NAME}`}
              >
                {voiceStatus === 'off' ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
            )}
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

        {/* Voice Assistant Status Bar */}
        {voiceStatus !== 'off' && voiceStatus !== 'unsupported' && (
          <div className="px-6 py-2 bg-blue-950/50 border-b border-blue-900 flex items-center gap-2 text-sm">
            <Mic className={`w-4 h-4 ${voiceStatus === 'speaking' ? 'text-purple-400' : 'text-blue-400 animate-pulse'}`} />
            {voiceStatus === 'listening-for-wake' && (
              <span className="text-blue-300">Say "Hey {ASSISTANT_NAME}" to start talking...</span>
            )}
            {voiceStatus === 'listening-for-command' && (
              <span className="text-blue-300">
                {ASSISTANT_NAME} is listening{liveTranscript ? `: "${liveTranscript}"` : '...'}
              </span>
            )}
            {voiceStatus === 'speaking' && (
              <span className="text-purple-300">{ASSISTANT_NAME} is speaking...</span>
            )}
          </div>
        )}

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
                Start a conversation with our multi-agent system powered by Groq Cloud API.
                The system automatically detects task complexity and routes to the right agents.
              </p>
              <div className="flex gap-2">
                <span className="text-xs px-3 py-1 bg-gray-800 rounded-full">Groq Cloud</span>
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

                {msg.attachmentName && (
                  <div className="mt-2 flex items-center gap-1.5 text-xs opacity-80">
                    <FileText className="w-3 h-3" />
                    <span>{msg.attachmentName}</span>
                  </div>
                )}

                {msg.source && (
                  <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                    <Cloud className="w-3 h-3" />
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
            {pendingAttachment && (
              <div className="flex items-center gap-2 mb-2 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-xs text-gray-300 w-fit">
                <FileText className="w-3.5 h-3.5" />
                <span>{pendingAttachment.name}</span>
                <button onClick={() => setPendingAttachment(null)} className="text-gray-500 hover:text-red-400">
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
            <div className="flex items-end gap-2 bg-gray-900 rounded-xl border border-gray-700 p-2">
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                className="hidden"
                accept="image/*,text/*,.md,.json,.csv,.log,.py,.js,.jsx,.ts,.tsx,.html,.css,.yml,.yaml,.xml,.sh,.java,.c,.cpp,.go,.rs,.rb,.php,.sql"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors flex-shrink-0"
                title="Attach a file"
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything... The AI will auto-detect complexity and use the right agents."
                className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none outline-none min-h-[44px] max-h-[200px] py-2 px-3"
                rows={1}
              />
              <button
                onClick={() => handleSend()}
                disabled={(!message.trim() && !pendingAttachment) || isLoading}
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
                {healthData?.cloud?.available && (
                  <span className="flex items-center gap-1 text-green-400">
                    <Server className="w-3 h-3" />
                    {healthData.cloud.provider} Connected
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
