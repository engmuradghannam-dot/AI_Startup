import { useState, useEffect } from 'react'
import { useQuery, useQueryClient } from 'react-query'
import { Plus, Search, Filter, Bot, Trash2, Play, ChevronDown, ChevronUp } from 'lucide-react'
import AgentCard from '../components/AgentCard'
import { agentsApi } from '../services/api'
import toast from 'react-hot-toast'

// Local storage helpers
const getStoredAgents = () => {
  try {
    const stored = localStorage.getItem('ai_startup_agents')
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

const storeAgents = (agents: any[]) => {
  localStorage.setItem('ai_startup_agents', JSON.stringify(agents))
}

export default function Agents() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null)
  const [newAgent, setNewAgent] = useState({
    name: '',
    role: 'general',
    description: '',
    priority: 5,
  })

  const { data: apiAgents, isLoading } = useQuery(
    'agents',
    () => agentsApi.list().then((r: any) => r.data),
    { refetchInterval: 5000 }
  )

  // Merge API agents with local storage
  const storedAgents = getStoredAgents()
  const apiAgentsArray = Array.isArray(apiAgents) ? apiAgents : []

  // Use stored agents if API returns empty
  const allAgents = apiAgentsArray.length > 0 ? apiAgentsArray : storedAgents

  const filteredAgents = allAgents.filter((agent: any) =>
    (agent.name?.toLowerCase() || '').includes(searchQuery.toLowerCase()) ||
    (agent.role?.toLowerCase() || '').includes(searchQuery.toLowerCase())
  )

  const handleCreate = async () => {
    try {
      const result = await agentsApi.create(newAgent)
      const createdAgent = result.data || result

      // Add to local storage
      const current = getStoredAgents()
      current.push(createdAgent)
      storeAgents(current)

      toast.success('Agent created successfully')
      setShowCreateModal(false)
      setNewAgent({ name: '', role: 'general', description: '', priority: 5 })
      queryClient.invalidateQueries('agents')
    } catch {
      // Create locally if API fails
      const localAgent = {
        id: `local_${Date.now()}`,
        name: newAgent.name,
        role: newAgent.role,
        status: 'active',
        description: newAgent.description,
        priority: newAgent.priority,
        metrics: { cpu: 0, memory: 0, tasks_completed: 0 },
        tasks: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      const current = getStoredAgents()
      current.push(localAgent)
      storeAgents(current)

      toast.success('Agent created locally')
      setShowCreateModal(false)
      setNewAgent({ name: '', role: 'general', description: '', priority: 5 })
      queryClient.invalidateQueries('agents')
    }
  }

  const handleScaleUp = async () => {
    try {
      const result = await agentsApi.scaleUp(5, 'general')
      toast.success('Scaled up 5 agents')
      queryClient.invalidateQueries('agents')
    } catch {
      // Create locally
      for (let i = 0; i < 5; i++) {
        const localAgent = {
          id: `local_${Date.now()}_${i}`,
          name: `Auto-Scaled Agent ${i + 1}`,
          role: 'general',
          status: 'active',
          description: 'Auto-scaled agent',
          priority: 5,
          metrics: { cpu: 0, memory: 0, tasks_completed: 0 },
          tasks: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
        const current = getStoredAgents()
        current.push(localAgent)
        storeAgents(current)
      }
      toast.success('Created 5 local agents')
      queryClient.invalidateQueries('agents')
    }
  }

  const handleDelete = (agentId: string) => {
    const current = getStoredAgents()
    const updated = current.filter((a: any) => a.id !== agentId)
    storeAgents(updated)
    toast.success('Agent deleted')
    queryClient.invalidateQueries('agents')
  }

  const handleAddTask = (agentId: string, taskName: string) => {
    const current = getStoredAgents()
    const agent = current.find((a: any) => a.id === agentId)
    if (agent) {
      if (!agent.tasks) agent.tasks = []
      agent.tasks.push({
        id: `task_${Date.now()}`,
        name: taskName,
        status: 'pending',
        created_at: new Date().toISOString(),
      })
      storeAgents(current)
      toast.success('Task added')
      queryClient.invalidateQueries('agents')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agents</h1>
          <p className="text-gray-600 mt-1">Manage your AI agents</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleScaleUp}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
          >
            Auto-Scale +5
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Agent
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
          <Filter className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      {/* Agents List */}
      {isLoading && allAgents.length === 0 ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
          <p className="text-gray-500 mt-4">Loading agents...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAgents.map((agent: any) => (
            <div
              key={agent.id || agent._id || Math.random()}
              className="bg-white rounded-lg border border-gray-200 overflow-hidden"
            >
              {/* Agent Header */}
              <div
                className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50"
                onClick={() => setExpandedAgent(expandedAgent === agent.id ? null : agent.id)}
              >
                <div className="flex items-center space-x-4">
                  <Bot className="w-10 h-10 text-primary-600" />
                  <div>
                    <h3 className="font-medium text-gray-900">{agent.name || 'Unnamed'}</h3>
                    <p className="text-sm text-gray-500">{agent.role || 'general'} • {agent.status || 'active'}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">
                    {agent.tasks?.length || 0} tasks
                  </span>
                  {expandedAgent === agent.id ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </div>

              {/* Expanded Tasks */}
              {expandedAgent === agent.id && (
                <div className="border-t border-gray-200 p-4 bg-gray-50">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Tasks</h4>

                  {/* Add Task */}
                  <div className="flex space-x-2 mb-4">
                    <input
                      type="text"
                      placeholder="New task name..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleAddTask(agent.id, (e.target as HTMLInputElement).value)
                          ;(e.target as HTMLInputElement).value = ''
                        }
                      }}
                    />
                    <button
                      onClick={() => {
                        const input = document.querySelector(`input[placeholder="New task name..."]`) as HTMLInputElement
                        if (input?.value) {
                          handleAddTask(agent.id, input.value)
                          input.value = ''
                        }
                      }}
                      className="px-3 py-2 bg-primary-600 text-white rounded-lg text-sm"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Tasks List */}
                  <div className="space-y-2">
                    {agent.tasks?.map((task: any) => (
                      <div
                        key={task.id || Math.random()}
                        className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200"
                      >
                        <div className="flex items-center space-x-3">
                          <Play className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-900">{task.name}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            task.status === 'completed' ? 'bg-green-100 text-green-700' :
                            task.status === 'running' ? 'bg-blue-100 text-blue-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {task.status}
                          </span>
                        </div>
                      </div>
                    ))}
                    {(!agent.tasks || agent.tasks.length === 0) && (
                      <p className="text-gray-500 text-sm text-center py-4">No tasks yet</p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex justify-end mt-4 space-x-2">
                    <button
                      onClick={() => handleDelete(agent.id)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg text-sm flex items-center"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
          {filteredAgents.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No agents found</p>
              <p className="text-sm mt-1">Create an agent to get started</p>
            </div>
          )}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Create New Agent</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newAgent.name}
                  onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="Agent name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  value={newAgent.role}
                  onChange={(e) => setNewAgent({ ...newAgent, role: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="general">General</option>
                  <option value="marketing">Marketing</option>
                  <option value="legal">Legal</option>
                  <option value="finance">Finance</option>
                  <option value="hr">HR</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="developer">Developer</option>
                  <option value="designer">Designer</option>
                  <option value="analyst">Analyst</option>
                  <option value="security">Security</option>
                  <option value="devops">DevOps</option>
                  <option value="data_scientist">Data Scientist</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newAgent.description}
                  onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  placeholder="Agent description"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority (1-10)</label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={newAgent.priority}
                  onChange={(e) => setNewAgent({ ...newAgent, priority: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
