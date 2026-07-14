import { useState } from 'react'
import { useQuery, useQueryClient } from 'react-query'
import { Plus, Search, Filter } from 'lucide-react'
import AgentCard from '../components/AgentCard'
import { agentsApi } from '../services/api'
import toast from 'react-hot-toast'

export default function Agents() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newAgent, setNewAgent] = useState({
    name: '',
    role: 'general',
    description: '',
    priority: 5,
  })

  const { data: agents, isLoading } = useQuery(
    'agents',
    () => agentsApi.list().then(r => r.data),
    { refetchInterval: 10000 }
  )

  // ✅ Ensure agents is always an Array before filter
  const agentsArray = Array.isArray(agents) ? agents : []

  const filteredAgents = agentsArray.filter((agent: any) =>
    agent.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.role?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleCreate = async () => {
    try {
      await agentsApi.create(newAgent)
      toast.success('Agent created successfully')
      setShowCreateModal(false)
      setNewAgent({ name: '', role: 'general', description: '', priority: 5 })
      queryClient.invalidateQueries('agents')
    } catch {
      toast.error('Failed to create agent')
    }
  }

  const handleScaleUp = async () => {
    try {
      await agentsApi.scaleUp(5, 'general')
      toast.success('Scaled up 5 agents')
      queryClient.invalidateQueries('agents')
    } catch {
      toast.error('Failed to scale up')
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

      {/* Agents Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
          <p className="text-gray-500 mt-4">Loading agents...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent: any) => (
            <AgentCard
              key={agent.id || agent._id || Math.random()}
              agent={agent}
              onUpdate={() => queryClient.invalidateQueries('agents')}
            />
          ))}
          {filteredAgents.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500">
              No agents found
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
