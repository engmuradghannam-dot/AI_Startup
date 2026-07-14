import { useState } from 'react'
import { 
  Play, 
  Pause, 
  Copy, 
  Trash2, 
  Activity,
  Cpu,
  Clock
} from 'lucide-react'
import { agentsApi } from '../services/api'
import toast from 'react-hot-toast'

interface Agent {
  id: string
  name: string
  role: string
  status: string
  description: string
  metrics: {
    tasks_completed: number
    tasks_failed: number
    total_tokens_used: number
    total_cost_usd: number
  }
}

export default function AgentCard({ agent, onUpdate }: { agent: Agent; onUpdate: () => void }) {
  const [isExecuting, setIsExecuting] = useState(false)

  const statusColors: Record<string, string> = {
    idle: 'bg-green-100 text-green-800',
    busy: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    paused: 'bg-gray-100 text-gray-800',
    learning: 'bg-blue-100 text-blue-800',
  }

  const handleClone = async () => {
    try {
      await agentsApi.clone(agent.id, `${agent.name} (Clone)`)
      toast.success('Agent cloned successfully')
      onUpdate()
    } catch {
      toast.error('Failed to clone agent')
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this agent?')) return
    try {
      await agentsApi.delete(agent.id)
      toast.success('Agent deleted')
      onUpdate()
    } catch {
      toast.error('Failed to delete agent')
    }
  }

  const handleExecute = async () => {
    setIsExecuting(true)
    try {
      await agentsApi.execute(agent.id, {
        name: 'Quick Task',
        description: 'Execute a quick test task',
        parameters: {},
      })
      toast.success('Task executed')
    } catch {
      toast.error('Execution failed')
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${statusColors[agent.status] || 'bg-gray-100 text-gray-800'}`}>
            {agent.status}
          </span>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleExecute}
            disabled={isExecuting || agent.status === 'busy'}
            className="p-2 rounded-lg hover:bg-gray-100 text-green-600 disabled:opacity-50"
            title="Execute Task"
          >
            <Play className="w-4 h-4" />
          </button>
          <button
            onClick={handleClone}
            className="p-2 rounded-lg hover:bg-gray-100 text-blue-600"
            title="Clone Agent"
          >
            <Copy className="w-4 h-4" />
          </button>
          <button
            onClick={handleDelete}
            className="p-2 rounded-lg hover:bg-gray-100 text-red-600"
            title="Delete Agent"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <p className="text-sm text-gray-600 mb-4">{agent.description || 'No description'}</p>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="flex items-center text-gray-600">
          <Activity className="w-4 h-4 mr-2" />
          <span>Role: {agent.role}</span>
        </div>
        <div className="flex items-center text-gray-600">
          <Cpu className="w-4 h-4 mr-2" />
          <span>Tasks: {agent.metrics?.tasks_completed || 0}</span>
        </div>
        <div className="flex items-center text-gray-600">
          <Clock className="w-4 h-4 mr-2" />
          <span>Failed: {agent.metrics?.tasks_failed || 0}</span>
        </div>
        <div className="flex items-center text-gray-600">
          <Activity className="w-4 h-4 mr-2" />
          <span>Cost: ${(agent.metrics?.total_cost_usd || 0).toFixed(4)}</span>
        </div>
      </div>
    </div>
  )
}
