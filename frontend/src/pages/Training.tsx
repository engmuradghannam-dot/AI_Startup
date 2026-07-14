import { useQuery, useQueryClient } from 'react-query'
import { useState } from 'react'
import {
  BookOpen,
  Brain,
  MessageSquare,
  GitBranch,
  Database,
  Play
} from 'lucide-react'
import { trainingApi } from '../services/api'
import toast from 'react-hot-toast'

export default function Training() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('datasets')
  const [selectedAgent, setSelectedAgent] = useState('')

  const { data: datasets, isLoading: datasetsLoading } = useQuery(
    'datasets',
    () => trainingApi.getDatasets().then(r => r.data),
    { refetchInterval: 30000 }
  )

  const { data: feedbackStats } = useQuery(
    ['feedbackStats', selectedAgent],
    () => trainingApi.getFeedbackStats(selectedAgent || undefined).then(r => r.data),
    { enabled: activeTab === 'feedback' }
  )

  // ✅ Ensure datasets is always an Array
  const datasetsArray = Array.isArray(datasets) ? datasets : []

  // ✅ Ensure feedbackStats is always an Object
  const feedbackStatsObj = (feedbackStats && typeof feedbackStats === 'object' && !Array.isArray(feedbackStats))
    ? feedbackStats
    : {}

  const tabs = [
    { id: 'datasets', label: 'Datasets', icon: Database },
    { id: 'feedback', label: 'Feedback', icon: MessageSquare },
    { id: 'memory', label: 'Memory', icon: Brain },
    { id: 'knowledge', label: 'Knowledge Graph', icon: GitBranch },
  ]

  const handleProcessFeedback = async () => {
    try {
      await trainingApi.processFeedback(100)
      toast.success('Feedback processed')
      queryClient.invalidateQueries('feedbackStats')
    } catch {
      toast.error('Failed to process feedback')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Training & Learning</h1>
        <p className="text-gray-600 mt-1">Manage training data, feedback, and knowledge</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {tabs.map((tab) => {
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
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Training Datasets</h3>
            <button className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700">
              + New Dataset
            </button>
          </div>

          {datasetsLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
              <p className="text-gray-500 mt-4">Loading datasets...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {datasetsArray.map((dataset: any) => (
                <div key={dataset.id || dataset._id || Math.random()} className="bg-white rounded-xl border border-gray-200 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <BookOpen className="w-5 h-5 text-primary-600" />
                    <span className="text-xs text-gray-500">{dataset.type || 'unknown'}</span>
                  </div>
                  <h4 className="font-semibold text-gray-900">{dataset.name || 'Unnamed'}</h4>
                  <p className="text-sm text-gray-500 mt-1">{dataset.entries || 0} entries</p>
                  <div className="mt-3 flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${(dataset.quality || 0) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 ml-2">
                      Quality: {((dataset.quality || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
              {datasetsArray.length === 0 && (
                <div className="col-span-full text-center py-12 text-gray-500">
                  No datasets found
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'feedback' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Feedback Loop</h3>
            <button
              onClick={handleProcessFeedback}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700 flex items-center"
            >
              <Play className="w-4 h-4 mr-2" />
              Process Feedback
            </button>
          </div>

          {feedbackStatsObj && Object.keys(feedbackStatsObj).length > 0 ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
                  <p className="text-3xl font-bold text-primary-600">{feedbackStatsObj.total_feedback || 0}</p>
                  <p className="text-sm text-gray-500 mt-1">Total Feedback</p>
                </div>
                <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
                  <p className="text-3xl font-bold text-green-600">{feedbackStatsObj.processed || 0}</p>
                  <p className="text-sm text-gray-500 mt-1">Processed</p>
                </div>
                <div className="bg-white rounded-xl border border-gray-200 p-5 text-center">
                  <p className="text-3xl font-bold text-blue-600">
                    {feedbackStatsObj.average_rating?.toFixed(1) || 'N/A'}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">Avg Rating</p>
                </div>
              </div>

              {/* Rating Distribution */}
              {feedbackStatsObj.rating_distribution && (
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">Rating Distribution</h4>
                  <div className="space-y-3">
                    {[5, 4, 3, 2, 1].map((rating) => {
                      const distribution = feedbackStatsObj.rating_distribution || {}
                      const count = distribution[rating] || 0
                      const total = feedbackStatsObj.total_feedback || 1
                      const percentage = (count / total) * 100
                      return (
                        <div key={rating} className="flex items-center">
                          <span className="w-8 text-sm font-medium">{rating}★</span>
                          <div className="flex-1 mx-3 bg-gray-200 rounded-full h-4">
                            <div
                              className={`h-4 rounded-full ${
                                rating >= 4 ? 'bg-green-500' : rating >= 3 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-500 w-12 text-right">{count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
              <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No feedback data available</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'memory' && (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
          <Brain className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">Agent Memory</h3>
          <p className="text-gray-500 mt-2">Select an agent to view its memory and learning history</p>
          <input
            type="text"
            placeholder="Enter agent ID..."
            className="mt-4 px-4 py-2 border border-gray-300 rounded-lg max-w-sm"
            onChange={(e) => setSelectedAgent(e.target.value)}
          />
        </div>
      )}

      {activeTab === 'knowledge' && (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
          <GitBranch className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">Knowledge Graph</h3>
          <p className="text-gray-500 mt-2">Visualize interconnected agent knowledge</p>
          <p className="text-sm text-gray-400 mt-4">Coming soon: Interactive graph visualization</p>
        </div>
      )}
    </div>
  )
}
