import { useState, useEffect } from 'react'
import { learningApi, agentsApi } from '../services/api'
import { GraduationCap, TrendingUp, Star, MessageSquare, Brain, Download, Upload } from 'lucide-react'

interface LearningStats {
  total_patterns_learned: number
  pattern_types: { preferences: number; corrections: number; enhancements: number }
  total_interactions: number
  successful_interactions: number
  user_satisfaction: number
  improvement_rate: number
  feedback_count: number
  avg_confidence: number
}

export default function LearningPage() {
  const [agents, setAgents] = useState<any[]>([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [stats, setStats] = useState<LearningStats | null>(null)
  const [patterns, setPatterns] = useState<any[]>([])
  const [feedback, setFeedback] = useState({
    query: '',
    response: '',
    rating: 3,
    correction: '',
    comments: '',
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadAgents()
  }, [])

  useEffect(() => {
    if (selectedAgent) {
      loadStats()
      loadPatterns()
    }
  }, [selectedAgent])

  const loadAgents = async () => {
    try {
      const res = await agentsApi.list()
      setAgents(res.data || [])
      if (res.data?.length > 0) setSelectedAgent(res.data[0].id)
    } catch (e) {
      console.error(e)
    }
  }

  const loadStats = async () => {
    if (!selectedAgent) return
    try {
      const res = await learningApi.getStats(selectedAgent)
      setStats(res)
    } catch (e) {
      console.error(e)
    }
  }

  const loadPatterns = async () => {
    if (!selectedAgent) return
    try {
      const res = await learningApi.getPatterns(selectedAgent)
      setPatterns(res.patterns || [])
    } catch (e) {
      console.error(e)
    }
  }

  const handleSubmitFeedback = async () => {
    if (!feedback.query.trim() || !selectedAgent) return
    setLoading(true)
    try {
      await learningApi.submitFeedback({
        agent_id: selectedAgent,
        query: feedback.query,
        response: feedback.response,
        rating: feedback.rating,
        correction: feedback.correction,
        comments: feedback.comments,
      })
      setFeedback({ query: '', response: '', rating: 3, correction: '', comments: '' })
      setMessage('Feedback submitted successfully!')
      loadStats()
      loadPatterns()
    } catch (e) {
      setMessage('Error submitting feedback')
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
  }

  const handleTriggerLearning = async () => {
    if (!selectedAgent) return
    setLoading(true)
    try {
      await learningApi.triggerLearning(selectedAgent)
      setMessage('Learning triggered!')
      loadStats()
      loadPatterns()
    } catch (e) {
      setMessage('Error triggering learning')
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <GraduationCap className="w-8 h-8 text-indigo-600" />
        <h1 className="text-3xl font-bold text-gray-900">Self-Learning System</h1>
      </div>

      {message && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700">
          {message}
        </div>
      )}

      {/* Agent Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Select Agent</label>
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
        >
          {agents.map((agent) => (
            <option key={agent.id} value={agent.id}>{agent.name}</option>
          ))}
        </select>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-5 h-5 text-indigo-500" />
              <span className="text-sm text-gray-600">Patterns Learned</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.total_patterns_learned}</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Star className="w-5 h-5 text-yellow-500" />
              <span className="text-sm text-gray-600">Satisfaction</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.user_satisfaction}%</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-600">Improvement</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.improvement_rate}%</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-600">Interactions</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.total_interactions}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Submit Feedback */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Submit Feedback
          </h2>
          <div className="space-y-4">
            <textarea
              value={feedback.query}
              onChange={(e) => setFeedback({ ...feedback, query: e.target.value })}
              placeholder="User query..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 h-20 resize-none"
            />
            <textarea
              value={feedback.response}
              onChange={(e) => setFeedback({ ...feedback, response: e.target.value })}
              placeholder="Agent response..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 h-20 resize-none"
            />
            <div>
              <label className="text-sm text-gray-600">Rating: {feedback.rating}/5</label>
              <input
                type="range"
                min="1"
                max="5"
                step="1"
                value={feedback.rating}
                onChange={(e) => setFeedback({ ...feedback, rating: parseInt(e.target.value) })}
                className="w-full"
              />
            </div>
            <textarea
              value={feedback.correction}
              onChange={(e) => setFeedback({ ...feedback, correction: e.target.value })}
              placeholder="Suggested correction (optional)..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 h-20 resize-none"
            />
            <button
              onClick={handleSubmitFeedback}
              disabled={loading}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </div>

        {/* Patterns & Actions */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Learned Patterns
            </h2>
            <button
              onClick={handleTriggerLearning}
              disabled={loading}
              className="px-3 py-1.5 text-sm bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100"
            >
              Trigger Learning
            </button>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {patterns.length === 0 && (
              <p className="text-gray-500 text-center py-8">No patterns learned yet</p>
            )}
            {patterns.map((pattern, idx) => (
              <div key={idx} className="p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    pattern.pattern_type === 'preference' ? 'bg-green-100 text-green-700' :
                    pattern.pattern_type === 'correction' ? 'bg-red-100 text-red-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {pattern.pattern_type}
                  </span>
                  <span className="text-xs text-gray-500">Confidence: {pattern.confidence}</span>
                </div>
                <p className="text-sm text-gray-700 truncate">{pattern.trigger}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
