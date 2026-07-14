import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { Send, Bot, User } from 'lucide-react'
import { agentsApi } from '../services/api'

// Local storage helper
const getStoredAgents = () => {
  try {
    const stored = localStorage.getItem('ai_startup_agents')
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

export default function AgentChat() {
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<any[]>([])
  const [selectedAgent, setSelectedAgent] = useState<any>(null)
  const [localAgents, setLocalAgents] = useState<any[]>([])

  // Load agents from local storage + API
  const { data: apiAgents, isLoading } = useQuery(
    'agents',
    () => agentsApi.list().then((r: any) => r.data),
  )

  useEffect(() => {
    const stored = getStoredAgents()
    const apiAgentsArray = Array.isArray(apiAgents) ? apiAgents : []
    // Merge and remove duplicates
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
    if (!message.trim()) return

    const newMessage = { role: 'user', content: message, agentId: selectedAgent?.id }
    setChatHistory([...chatHistory, newMessage])
    setMessage('')

    // Mock response
    setTimeout(() => {
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: selectedAgent
            ? `${selectedAgent.name}: This is a mock response. AI integration coming soon!`
            : 'This is a mock response. AI integration coming soon!',
        },
      ])
    }, 1000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Agent Chat</h1>
        <p className="text-gray-600 mt-1">Chat with your AI agents</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Agents List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h2 className="font-medium text-gray-900 mb-4">Available Agents</h2>
            {isLoading && localAgents.length === 0 ? (
              <p className="text-gray-500">Loading...</p>
            ) : (
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
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg border border-gray-200 flex flex-col h-[600px]">
            {/* Chat Header */}
            {selectedAgent && (
              <div className="border-b border-gray-200 p-4 flex items-center space-x-3">
                <Bot className="w-6 h-6 text-primary-600" />
                <div>
                  <div className="font-medium text-gray-900">{selectedAgent.name}</div>
                  <div className="text-xs text-gray-500">{selectedAgent.role} • {selectedAgent.status || 'active'}</div>
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
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
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
                  disabled={!selectedAgent}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:text-gray-400"
                />
                <button
                  onClick={handleSend}
                  disabled={!selectedAgent}
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
