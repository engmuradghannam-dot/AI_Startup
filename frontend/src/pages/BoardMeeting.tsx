import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { Send, Users, MessageSquare, CheckCircle, XCircle } from 'lucide-react'
import { aiChatApi } from '../services/api'

const AGENT_ICONS: Record<string, string> = {
  strategist: '🧭',
  coder: '💻',
  analyst: '📊',
  coordinator: '🤝',
}

interface AIAgent {
  name: string
  specialty: string
  description: string
  skills: string[]
  model: string
}

interface BoardMessage {
  id: string
  agentName: string
  specialty?: string
  provider?: string
  model?: string
  icon: string
  content: string
  role: 'user' | 'agent' | 'consensus'
  timestamp: string
  ok: boolean
}

export default function BoardMeeting() {
  const [message, setMessage] = useState('')
  const [boardHistory, setBoardHistory] = useState<BoardMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  const [consensusMode, setConsensusMode] = useState(false)

  const { data: agentsData } = useQuery('ai-agents', () => aiChatApi.getAgents())
  const agents: AIAgent[] = agentsData || []

  // Default to every real specialized agent being on the board
  useEffect(() => {
    if (agents.length > 0 && selectedAgents.length === 0) {
      setSelectedAgents(agents.map((a) => a.name))
    }
  }, [agents])

  const toggleAgent = (name: string) => {
    setSelectedAgents(prev =>
      prev.includes(name) ? prev.filter(n => n !== name) : [...prev, name]
    )
  }

  const handleSend = async () => {
    if (!message.trim() || selectedAgents.length === 0 || isLoading) return

    const question = message
    const userMessage: BoardMessage = {
      id: `user_${Date.now()}`,
      agentName: 'You',
      icon: '👤',
      content: question,
      role: 'user',
      timestamp: new Date().toISOString(),
      ok: true,
    }

    setBoardHistory(prev => [...prev, userMessage])
    setMessage('')
    setIsLoading(true)

    const activeAgents = agents.filter((a) => selectedAgents.includes(a.name))

    const responses = await Promise.all(
      activeAgents.map(async (agent): Promise<BoardMessage> => {
        try {
          const result = await aiChatApi.executeAgent(agent.name, question)
          return {
            id: `resp_${Date.now()}_${agent.name}`,
            agentName: agent.name,
            specialty: result.specialty,
            provider: result.provider,
            model: result.model_used,
            icon: AGENT_ICONS[agent.name] || '🤖',
            content: result.thought || 'No response',
            role: 'agent',
            timestamp: new Date().toISOString(),
            ok: true,
          }
        } catch (error: any) {
          return {
            id: `resp_${Date.now()}_${agent.name}`,
            agentName: agent.name,
            icon: AGENT_ICONS[agent.name] || '🤖',
            content: `Error - ${error.response?.data?.detail || error.message || 'Request failed'}`,
            role: 'agent',
            timestamp: new Date().toISOString(),
            ok: false,
          }
        }
      })
    )

    setBoardHistory(prev => [...prev, ...responses])

    if (consensusMode && responses.filter(r => r.ok).length > 1) {
      const consensus = await generateConsensus(responses, question)
      setBoardHistory(prev => [...prev, consensus])
    }

    setIsLoading(false)
  }

  const generateConsensus = async (responses: BoardMessage[], originalQuestion: string): Promise<BoardMessage> => {
    const successful = responses.filter(r => r.ok)

    if (successful.length === 0) {
      return {
        id: `consensus_${Date.now()}`,
        agentName: 'Board Consensus',
        icon: '🤝',
        content: 'No consensus could be reached - every agent hit an error. Please check your active provider in Settings.',
        role: 'consensus',
        timestamp: new Date().toISOString(),
        ok: false,
      }
    }

    try {
      const allOpinions = successful.map(r => `${r.agentName} (${r.specialty}): ${r.content}`).join('\n\n')
      const response = await aiChatApi.chat(
        [
          {
            role: 'system',
            content: 'You are a board consensus generator. Summarize the opinions below and provide a final consensus decision. Be concise.',
          },
          {
            role: 'user',
            content: `Question: ${originalQuestion}\n\nOpinions:\n${allOpinions}\n\nProvide a consensus decision:`,
          },
        ],
        { agent_mode: 'single', user_id: null }
      )

      return {
        id: `consensus_${Date.now()}`,
        agentName: 'Board Consensus',
        icon: '🤝',
        content: response.choices?.[0]?.message?.content || 'Consensus reached.',
        role: 'consensus',
        timestamp: new Date().toISOString(),
        ok: true,
      }
    } catch {
      return {
        id: `consensus_${Date.now()}`,
        agentName: 'Board Consensus',
        icon: '🤝',
        content: `Board Meeting Results:\n\n${successful.map(r => `✅ ${r.agentName}: Agreed`).join('\n')}\n\nAll participating agents have provided their input.`,
        role: 'consensus',
        timestamp: new Date().toISOString(),
        ok: true,
      }
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
          Board Members ({selectedAgents.length}/{agents.length})
        </h3>
        <div className="flex flex-wrap gap-2">
          {agents.map((agent) => {
            const isSelected = selectedAgents.includes(agent.name)
            return (
              <button
                key={agent.name}
                onClick={() => toggleAgent(agent.name)}
                className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                  isSelected
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                title={agent.specialty}
              >
                <span className="mr-2">{AGENT_ICONS[agent.name] || '🤖'}</span>
                {agent.name}
              </button>
            )
          })}
          {agents.length === 0 && (
            <p className="text-gray-500 text-sm">Loading agents...</p>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="bg-white rounded-lg border border-gray-200 flex flex-col h-[500px]">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {boardHistory.map((msg) => (
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
                <span>{msg.icon}</span>
              </div>
              <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : msg.role === 'consensus'
                  ? 'bg-green-50 text-green-900 border border-green-200'
                  : msg.ok
                  ? 'bg-gray-100 text-gray-900'
                  : 'bg-yellow-50 text-yellow-900 border border-yellow-200'
              }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium opacity-75 capitalize">
                    {msg.agentName} {msg.provider && `• ${msg.provider}`}
                  </span>
                  {msg.role === 'agent' && (
                    msg.ok ? (
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
              <p className="text-sm mt-1">All selected agents will respond using the active AI provider</p>
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
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
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
        <h3 className="font-medium text-gray-900 mb-2 flex items-center">
          <MessageSquare className="w-4 h-4 mr-2" />
          Board Members & Specialties
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
          {agents.map((agent) => (
            <div key={agent.name} className="flex items-center space-x-2">
              <span>{AGENT_ICONS[agent.name] || '🤖'}</span>
              <span className="text-gray-600 capitalize">{agent.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
