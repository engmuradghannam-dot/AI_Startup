import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { Send, Bot, User, Users, MessageSquare, Brain, CheckCircle, XCircle } from 'lucide-react'
import { agentsApi } from '../services/api'
import axios from 'axios'
import toast from 'react-hot-toast'

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

// Assign AI provider to each agent
const AGENT_PROVIDERS = [
  { provider: 'groq', model: 'llama-3.1-70b-versatile', icon: '🚀' },
  { provider: 'openai', model: 'gpt-4o', icon: '🧠' },
  { provider: 'chatgpt', model: 'gpt-4-turbo', icon: '💬' },
  { provider: 'grok', model: 'grok-beta', icon: '⚡' },
  { provider: 'anthropic', model: 'claude-3-5-sonnet-20241022', icon: '🎯' },
  { provider: 'google', model: 'gemini-1.5-pro', icon: '🔮' },
  { provider: 'cohere', model: 'command-r-plus', icon: '📊' },
  { provider: 'mistral', model: 'mistral-large-latest', icon: '🌊' },
  { provider: 'kimi', model: 'kimi-k2', icon: '🌙' },
]

interface BoardMessage {
  id: string
  agentId: string
  agentName: string
  agentRole: string
  provider: string
  model: string
  icon: string
  content: string
  role: 'user' | 'agent' | 'consensus'
  timestamp: string
  agreed: boolean
}

export default function BoardMeeting() {
  const [message, setMessage] = useState('')
  const [boardHistory, setBoardHistory] = useState<BoardMessage[]>([])
  const [localAgents, setLocalAgents] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  const [consensusMode, setConsensusMode] = useState(false)

  // Load agents
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
    if (unique.length > 0 && selectedAgents.length === 0) {
      setSelectedAgents(unique.map((a: any) => a.id))
    }
  }, [apiAgents])

  const toggleAgent = (agentId: string) => {
    setSelectedAgents(prev =>
      prev.includes(agentId)
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    )
  }

  const handleSend = async () => {
    if (!message.trim() || selectedAgents.length === 0) return

    const userMessage: BoardMessage = {
      id: `user_${Date.now()}`,
      agentId: 'user',
      agentName: 'You',
      agentRole: 'Chairman',
      provider: 'user',
      model: 'user',
      icon: '👤',
      content: message,
      role: 'user',
      timestamp: new Date().toISOString(),
      agreed: true,
    }

    setBoardHistory(prev => [...prev, userMessage])
    setMessage('')
    setIsLoading(true)

    const activeAgents = localAgents.filter((a: any) => selectedAgents.includes(a.id))

    // Get all responses in parallel
    const responses = await Promise.all(
      activeAgents.map(async (agent: any, index: number) => {
        const providerConfig = AGENT_PROVIDERS[index % AGENT_PROVIDERS.length]
        const providers = getStoredProviders()
        const provider = providers.find((p: any) => p.id === providerConfig.provider)

        if (!provider || !provider.keyValue) {
          return {
            id: `resp_${Date.now()}_${index}`,
            agentId: agent.id,
            agentName: agent.name,
            agentRole: agent.role,
            provider: providerConfig.provider,
            model: providerConfig.model,
            icon: providerConfig.icon,
            content: `${agent.name}: I need an API key for ${providerConfig.provider} to respond. Please configure it in Settings.`,
            role: 'agent' as const,
            timestamp: new Date().toISOString(),
            agreed: false,
          }
        }

        try {
          const messages = [
            { 
              role: 'system', 
              content: `You are ${agent.name}, a ${agent.role} in a board meeting. You are discussing with other AI agents. Give your professional opinion. Be concise (2-3 sentences). Respond in the same language as the user.` 
            },
            { role: 'user', content: message },
          ]

          const response = await axios.post('/ai-chat/chat', {
            provider: providerConfig.provider,
            model: providerConfig.model,
            messages: messages,
            agent_name: agent.name,
            api_key: provider.keyValue,
          })

          return {
            id: `resp_${Date.now()}_${index}`,
            agentId: agent.id,
            agentName: agent.name,
            agentRole: agent.role,
            provider: providerConfig.provider,
            model: providerConfig.model,
            icon: providerConfig.icon,
            content: response.data.response || 'No response',
            role: 'agent' as const,
            timestamp: new Date().toISOString(),
            agreed: !response.data.mock,
          }
        } catch (error: any) {
          return {
            id: `resp_${Date.now()}_${index}`,
            agentId: agent.id,
            agentName: agent.name,
            agentRole: agent.role,
            provider: providerConfig.provider,
            model: providerConfig.model,
            icon: providerConfig.icon,
            content: `${agent.name}: Error - ${error.message || 'Connection failed'}`,
            role: 'agent' as const,
            timestamp: new Date().toISOString(),
            agreed: false,
          }
        }
      })
    )

    setBoardHistory(prev => [...prev, ...responses])

    // If consensus mode, generate consensus
    if (consensusMode && responses.length > 1) {
      const consensus = await generateConsensus(responses, message)
      setBoardHistory(prev => [...prev, consensus])
    }

    setIsLoading(false)
  }

  const generateConsensus = async (responses: BoardMessage[], originalQuestion: string): Promise<BoardMessage> => {
    const successfulResponses = responses.filter(r => r.agreed)

    if (successfulResponses.length === 0) {
      return {
        id: `consensus_${Date.now()}`,
        agentId: 'consensus',
        agentName: 'Board Consensus',
        agentRole: 'Consensus',
        provider: 'system',
        model: 'consensus',
        icon: '🤝',
        content: 'No consensus could be reached. All agents encountered errors. Please check API keys in Settings.',
        role: 'consensus',
        timestamp: new Date().toISOString(),
        agreed: false,
      }
    }

    // Try to get consensus from one of the working providers
    const providers = getStoredProviders()
    const workingProvider = providers.find((p: any) => p.isActive && p.keyValue)

    if (workingProvider) {
      try {
        const allOpinions = successfulResponses.map(r => `${r.agentName} (${r.provider}): ${r.content}`).join('\n\n')

        const response = await axios.post('/ai-chat/chat', {
          provider: workingProvider.id,
          model: workingProvider.models[0],
          messages: [
            { 
              role: 'system', 
              content: 'You are a board consensus generator. Summarize the opinions below and provide a final consensus decision. Be concise.' 
            },
            { role: 'user', content: `Question: ${originalQuestion}

Opinions:
${allOpinions}

Provide a consensus decision:` },
          ],
          agent_name: 'Consensus',
          api_key: workingProvider.keyValue,
        })

        return {
          id: `consensus_${Date.now()}`,
          agentId: 'consensus',
          agentName: 'Board Consensus',
          agentRole: 'Consensus',
          provider: workingProvider.id,
          model: workingProvider.models[0],
          icon: '🤝',
          content: response.data.response || 'Consensus reached.',
          role: 'consensus',
          timestamp: new Date().toISOString(),
          agreed: true,
        }
      } catch (e) {
        // Fallback
      }
    }

    // Simple consensus
    return {
      id: `consensus_${Date.now()}`,
      agentId: 'consensus',
      agentName: 'Board Consensus',
      agentRole: 'Consensus',
      provider: 'system',
      model: 'consensus',
      icon: '🤝',
      content: `Board Meeting Results:

${successfulResponses.map(r => `✅ ${r.agentName} (${r.provider}): Agreed`).join('\n')}

All participating agents have provided their input.`,
      role: 'consensus',
      timestamp: new Date().toISOString(),
      agreed: true,
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Board Meeting</h1>
          <p className="text-gray-600 mt-1">All AI agents discuss and reach consensus</p>
        </div>
        <div className="flex items-center space-x-3">
          <label className="flex items-center cursor-pointer bg-white px-3 py-2 rounded-lg border border-gray-200">
            <input
              type="checkbox"
              checked={consensusMode}
              onChange={(e) => setConsensusMode(e.target.checked)}
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
            />
            <span className="ml-2 text-sm text-gray-700">Auto Consensus</span>
          </label>
        </div>
      </div>

      {/* Agent Selector */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-medium text-gray-900 mb-3 flex items-center">
          <Users className="w-5 h-5 mr-2" />
          Board Members ({selectedAgents.length}/{localAgents.length})
        </h3>
        <div className="flex flex-wrap gap-2">
          {localAgents.map((agent: any, index: number) => {
            const providerConfig = AGENT_PROVIDERS[index % AGENT_PROVIDERS.length]
            const isSelected = selectedAgents.includes(agent.id)
            return (
              <button
                key={agent.id}
                onClick={() => toggleAgent(agent.id)}
                className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isSelected
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span className="mr-2">{providerConfig.icon}</span>
                {agent.name}
                <span className="ml-2 text-xs opacity-75">
                  {providerConfig.provider}
                </span>
              </button>
            )
          })}
          {localAgents.length === 0 && (
            <p className="text-gray-500 text-sm">No agents available. Create agents first.</p>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="bg-white rounded-lg border border-gray-200 flex flex-col h-[500px]">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {boardHistory.map((msg: BoardMessage) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${
                msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                msg.role === 'user' ? 'bg-primary-600' :
                msg.role === 'consensus' ? 'bg-green-600' :
                'bg-gray-200'
              }`}>
                {msg.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : msg.role === 'consensus' ? (
                  <CheckCircle className="w-5 h-5 text-white" />
                ) : (
                  <span>{msg.icon}</span>
                )}
              </div>
              <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : msg.role === 'consensus'
                  ? 'bg-green-50 text-green-900 border border-green-200'
                  : msg.agreed
                  ? 'bg-gray-100 text-gray-900'
                  : 'bg-yellow-50 text-yellow-900 border border-yellow-200'
              }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium opacity-75">
                    {msg.agentName} {msg.role !== 'user' && `• ${msg.provider}`}
                  </span>
                  {msg.role === 'agent' && (
                    msg.agreed ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <XCircle className="w-4 h-4 text-yellow-500" />
                    )
                  )}
                </div>
                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-center justify-center space-x-2 py-4">
              <div className="w-3 h-3 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-3 h-3 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-3 h-3 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              <span className="ml-2 text-sm text-gray-500">Board is deliberating...</span>
            </div>
          )}
          {boardHistory.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Start a board meeting</p>
              <p className="text-sm mt-1">All selected agents will respond using different AI models</p>
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
              placeholder={`Ask the board (${selectedAgents.length} agents)...`}
              disabled={isLoading || selectedAgents.length === 0}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || selectedAgents.length === 0}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-300 flex items-center"
            >
              <Send className="w-5 h-5 mr-2" />
              Ask Board
            </button>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-medium text-gray-900 mb-2">AI Models Used</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
          {AGENT_PROVIDERS.map((p, i) => (
            <div key={p.provider} className="flex items-center space-x-2">
              <span>{p.icon}</span>
              <span className="text-gray-600">{p.provider}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
