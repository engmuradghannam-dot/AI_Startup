import { useState } from 'react'
import { Zap, Play, Settings, Info } from 'lucide-react'
import { skillsApi } from '../services/api'
import toast from 'react-hot-toast'

interface Skill {
  id: string
  name: string
  display_name: string
  category: string
  enabled: boolean
  trigger: string
  execution_mode: string
  metrics: {
    total_executions: number
    success_rate: number
  }
}

export default function SkillPanel({ skill, onUpdate }: { skill: Skill; onUpdate: () => void }) {
  const [isExecuting, setIsExecuting] = useState(false)

  const categoryColors: Record<string, string> = {
    fable5: 'bg-purple-100 text-purple-800',
    orchestration: 'bg-blue-100 text-blue-800',
    scaling: 'bg-green-100 text-green-800',
    optimization: 'bg-yellow-100 text-yellow-800',
    security: 'bg-red-100 text-red-800',
    monitoring: 'bg-indigo-100 text-indigo-800',
    learning: 'bg-pink-100 text-pink-800',
    deployment: 'bg-orange-100 text-orange-800',
    multimodal: 'bg-cyan-100 text-cyan-800',
    collaboration: 'bg-teal-100 text-teal-800',
  }

  const handleToggle = async () => {
    try {
      await skillsApi.update(skill.id, { enabled: !skill.enabled })
      toast.success(`Skill ${skill.enabled ? 'disabled' : 'enabled'}`)
      onUpdate()
    } catch {
      toast.error('Failed to update skill')
    }
  }

  const handleExecute = async () => {
    setIsExecuting(true)
    try {
      await skillsApi.execute(skill.id, {
        skill_id: skill.id,
        agent_id: 'system',
        parameters: {},
        context: {},
      })
      toast.success('Skill executed')
    } catch {
      toast.error('Execution failed')
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-50 rounded-lg">
            <Zap className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">{skill.display_name}</h4>
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${categoryColors[skill.category] || 'bg-gray-100 text-gray-800'}`}>
              {skill.category}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleExecute}
            disabled={isExecuting || !skill.enabled}
            className="p-1.5 rounded hover:bg-gray-100 text-green-600 disabled:opacity-50"
            title="Execute"
          >
            <Play className="w-4 h-4" />
          </button>
          <button
            onClick={handleToggle}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
              skill.enabled ? 'bg-primary-600' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                skill.enabled ? 'translate-x-5' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-gray-500 mt-3 pt-3 border-t border-gray-100">
        <span>Executions: {skill.metrics?.total_executions || 0}</span>
        <span>Success: {((skill.metrics?.success_rate || 0) * 100).toFixed(1)}%</span>
        <span className="capitalize">{skill.execution_mode}</span>
      </div>
    </div>
  )
}
