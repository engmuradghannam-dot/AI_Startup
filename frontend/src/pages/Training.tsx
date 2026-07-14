import { useQuery, useQueryClient } from 'react-query'
import { useState } from 'react'
import { BookOpen, Database, MessageSquare, TrendingUp } from 'lucide-react'
import { trainingApi } from '../services/api'

export default function Training() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('datasets')

  const { data: datasetsResponse, isLoading: datasetsLoading } = useQuery(
    'datasets',
    () => trainingApi.getDatasets().then((r: any) => r.data),
    { refetchInterval: 30000 }
  )

  const { data: statsResponse } = useQuery(
    'trainingStats',
    () => trainingApi.getStats().then((r: any) => r.data)
  )

  // ✅ Ensure datasets is always an Array
  const datasets = Array.isArray(datasetsResponse) ? datasetsResponse : []

  // ✅ Ensure stats is always an Object
  const stats = (statsResponse && typeof statsResponse === 'object')
    ? statsResponse
    : { datasets: 0, memories: 0, feedback: 0 }

  const tabs = [
    { id: 'datasets', label: 'Datasets', icon: Database },
    { id: 'feedback', label: 'Feedback', icon: MessageSquare },
    { id: 'memory', label: 'Memory', icon: BookOpen },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Training</h1>
        <p className="text-gray-600 mt-1">Manage training data and feedback</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-500">Datasets</div>
          <div className="text-2xl font-bold text-gray-900">{stats.datasets || 0}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-500">Memories</div>
          <div className="text-2xl font-bold text-gray-900">{stats.memories || 0}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-500">Feedback</div>
          <div className="text-2xl font-bold text-gray-900">{stats.feedback || 0}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {tabs.map((tab: any) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Content */}
      {activeTab === 'datasets' && (
        <div>
          {datasetsLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
              <p className="text-gray-500 mt-4">Loading datasets...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {datasets.map((dataset: any) => (
                <div
                  key={dataset.id || dataset._id || Math.random()}
                  className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{dataset.name || 'Unnamed'}</h3>
                      <p className="text-sm text-gray-500">{dataset.type || 'conversations'}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">{dataset.entries || 0} entries</div>
                      <div className="text-sm text-gray-500">Quality: {dataset.quality || 0}%</div>
                    </div>
                  </div>
                </div>
              ))}
              {datasets.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  No datasets found
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'feedback' && (
        <div className="text-center py-12 text-gray-500">
          Feedback management coming soon
        </div>
      )}

      {activeTab === 'memory' && (
        <div className="text-center py-12 text-gray-500">
          Memory management coming soon
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="text-center py-12 text-gray-500">
          Analytics coming soon
        </div>
      )}
    </div>
  )
}
