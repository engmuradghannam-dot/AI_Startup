import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { Send, Bot, User, Settings } from 'lucide-react'
import { agentsApi } from '../services/api'
import axios from 'axios'

// Local storage helper
const getStoredAgents = () => {
  try {
    const stored = localStorage.getItem('ai_startup_agents')
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

const getStoredProviders = () => {
  try {
    const stored = localStorage.getItem('ai_startup_providers')
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

const getActiveProvider = () => {
  const providers = getStoredProviders()
  const active = providers.find((p: any) => p.isActive)
  return active || providers[0] || { id: 'groq', name: 'Groq', models: ['llama-3.1-70b-versatile'] }
}

export default function AgentChat() {
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<any[]>([])
  const [selectedAgent, setSelectedAgent] = useState<any>(null)
  const [localAgents, setLocalAgents] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  // Load agents from local storage + API
  const { data: apiAgents } = useQuery(
    'agents',
    () => agentsApi.list().then((r: any) => r.data),
  )

  useEffect(() => {
    const stored = getStoredAgents()
    const apiAgentsArray = Array.isArray(apiAgents) ? apiAgents : []
    const allAgents = [...stored, ...apiAgentsArray]
    const unique = allAgents.filter((agent, index, self) =>
      index === self.findIndex((a) => a.id === agent.id)
    )
    setLocalAgents(unique)
    if (unique.length > 0 && !selectedAgent) {
      setSelectedAgent(unique[0])
    }
  }, [apiAgents])

  const handleSend = async () => {
    if (!message.trim() || !selectedAgent) return

    const userMessage = { role: 'user', content: message, agentId: selectedAgent.id }
    setChatHistory((prev) => [...prev, userMessage])
    setMessage('')
    setIsLoading(true)

    try {
      const provider = getActiveProvider()
      const messages = [
        { role: 'system', content: `You are ${selectedAgent.name}, an AI agent with role: ${selectedAgent.role}. ${selectedAgent.description || ''}` },
        ...chatHistory.filter((m: any) => m.role === 'user' || m.role === 'assistant').slice(-10),
        { role: 'user', content: message },
      ]

      // Call backend AI API
      const response = await axios.post('/ai-chat/chat', {
        provider: provider.id,
        model: provider.models[0],
        messages: messages,
        agent_name: selectedAgent.name,
      })

      const aiResponse = response.data.response || 'No response'

      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: aiResponse,
          agentId: selectedAgent.id,
          provider: response.data.provider,
          model: response.data.model,
          mock: response.data.mock,
        },
      ])
    } catch (error) {
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `${selectedAgent.name}: Sorry, I encountered an error. Please check your AI provider settings.`,
          agentId: selectedAgent.id,
          error: true,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const activeProvider = getActiveProvider()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent Chat</h1>
          <p className="text-gray-600 mt-1">Chat with your AI agents</p>
        </div>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center text-sm"
        >
          <Settings className="w-4 h-4 mr-2" />
          AI: {activeProvider.name}
        </button>
      </div>

      {/* AI Provider Selector */}
      {showSettings && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium text-gray-900 mb-3">Select AI Provider</h3>
          <div className="flex flex-wrap gap-2">
            {getStoredProviders().map((provider: any) => (
              <button
                key={provider.id}
                onClick={() => {
                  // Update active provider
                  const providers = getStoredProviders()
                  const updated = providers.map((p: any) => ({
                    ...p,
                    isActive: p.id === provider.id,
                  }))
                  localStorage.setItem('ai_startup_providers', JSON.stringify(updated))
                  setShowSettings(false)
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  provider.isActive
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {provider.name}
                {provider.keyValue ? ' ✅' : ' ❌'}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            ✅ = API key configured | ❌ = No API key
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Agents List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h2 className="font-medium text-gray-900 mb-4">Available Agents</h2>
            <div className="space-y-2">
              {localAgents.map((agent: any) => (
                <div
                  key={agent.id || agent._id || Math.random()}
                  onClick={() => setSelectedAgent(agent)}
                  className={`flex items-center p-2 rounded-lg cursor-pointer transition-colors ${
                    selectedAgent?.id === agent.id
                      ? 'bg-primary-50 border border-primary-200'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <Bot className="w-5 h-5 text-primary-600 mr-3" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{agent.name || 'Unnamed'}</div>
                    <div className="text-xs text-gray-500">{agent.role || 'general'}</div>
                  </div>
                </div>
              ))}
              {localAgents.length === 0 && (
                <div className="text-center py-4">
                  <p className="text-gray-500 text-sm">No agents available</p>
                  <p className="text-xs text-gray-400 mt-1">Create agents in the Agents page</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg border border-gray-200 flex flex-col h-[600px]">
            {/* Chat Header */}
            {selectedAgent && (
              <div className="border-b border-gray-200 p-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Bot className="w-6 h-6 text-primary-600" />
                  <div>
                    <div className="font-medium text-gray-900">{selectedAgent.name}</div>
                    <div className="text-xs text-gray-500">{selectedAgent.role} • {selectedAgent.status || 'active'}</div>
                  </div>
                </div>
                <div className="text-xs text-gray-400">
                  Using: {activeProvider.name}
                </div>
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatHistory.map((msg: any, index: number) => (
                <div
                  key={index}
                  className={`flex items-start space-x-3 ${
                    msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    msg.role === 'user' ? 'bg-primary-600' : 'bg-gray-200'
                  }`}>
                    {msg.role === 'user' ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-gray-600" />
                    )}
                  </div>
                  <div className={`max-w-[70%] rounded-lg px-4 py-2 ${
                    msg.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : msg.error
                      ? 'bg-red-50 text-red-700 border border-red-200'
                      : msg.mock
                      ? 'bg-yellow-50 text-yellow-800 border border-yellow-200'
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    <div className="text-sm">{msg.content}</div>
                    {msg.mock && (
                      <div className="text-xs text-yellow-600 mt-1">
                        ⚠️ Mock mode - Configure API key in Settings
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-gray-600 animate-pulse" />
                  </div>
                  <div className="bg-gray-100 rounded-lg px-4 py-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
              {chatHistory.length === 0 && (
                <div className="text-center text-gray-500 mt-20">
                  <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Start a conversation with {selectedAgent?.name || 'an agent'}</p>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 p-4">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder={selectedAgent ? `Message ${selectedAgent.name}...` : 'Select an agent first...'}
                  disabled={!selectedAgent || isLoading}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:text-gray-400"
                />
                <button
                  onClick={handleSend}
                  disabled={!selectedAgent || isLoading}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-300"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
