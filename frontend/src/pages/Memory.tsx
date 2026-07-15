import { useState, useEffect } from 'react'
import { memoryApi, agentsApi } from '../services/api'
import { Brain, Search, Save, Database, Tag, BarChart3, Download, Upload } from 'lucide-react'

interface Memory {
  id: string
  content: string
  agent_id: string
  memory_type: string
  importance: number
  tags: string[]
  created_at: string
  access_count: number
}

interface MemoryStats {
  total_memories: number
  episodic: number
  semantic: number
  procedural: number
  avg_importance: number
  total_accesses: number
}

export default function MemoryPage() {
  const [agents, setAgents] = useState<any[]>([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [memories, setMemories] = useState<Memory[]>([])
  const [stats, setStats] = useState<MemoryStats | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [newMemory, setNewMemory] = useState({
    content: '',
    memory_type: 'episodic',
    importance: 0.5,
    tags: '',
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadAgents()
  }, [])

  useEffect(() => {
    if (selectedAgent) {
      loadMemories()
      loadStats()
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

  const loadMemories = async () => {
    if (!selectedAgent) return
    setLoading(true)
    try {
      const res = await memoryApi.getAgentMemories(selectedAgent, undefined, 50)
      setMemories(res || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const loadStats = async () => {
    if (!selectedAgent) return
    try {
      const res = await memoryApi.getStats(selectedAgent)
      setStats(res)
    } catch (e) {
      console.error(e)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim() || !selectedAgent) return
    setLoading(true)
    try {
      const res = await memoryApi.search({
        query: searchQuery,
        agent_id: selectedAgent,
        limit: 10,
      })
      setMemories(res || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const handleStore = async () => {
    if (!newMemory.content.trim() || !selectedAgent) return
    setLoading(true)
    try {
      await memoryApi.store({
        content: newMemory.content,
        agent_id: selectedAgent,
        memory_type: newMemory.memory_type,
        importance: newMemory.importance,
        tags: newMemory.tags.split(',').map(t => t.trim()).filter(Boolean),
      })
      setNewMemory({ content: '', memory_type: 'episodic', importance: 0.5, tags: '' })
      setMessage('Memory stored successfully!')
      loadMemories()
      loadStats()
    } catch (e) {
      setMessage('Error storing memory')
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
  }

  const handleConsolidate = async () => {
    if (!selectedAgent) return
    setLoading(true)
    try {
      await memoryApi.consolidate(selectedAgent)
      setMessage('Memories consolidated!')
      loadMemories()
      loadStats()
    } catch (e) {
      setMessage('Error consolidating memories')
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'episodic': return 'bg-purple-100 text-purple-700'
      case 'semantic': return 'bg-blue-100 text-blue-700'
      case 'procedural': return 'bg-green-100 text-green-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-8 h-8 text-indigo-600" />
        <h1 className="text-3xl font-bold text-gray-900">Advanced Memory System</h1>
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
              <Database className="w-5 h-5 text-indigo-500" />
              <span className="text-sm text-gray-600">Total Memories</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.total_memories}</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-600">Avg Importance</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.avg_importance?.toFixed(2) || 0}</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Tag className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-600">Episodic</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.episodic}</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-5 h-5 text-purple-500" />
              <span className="text-sm text-gray-600">Semantic</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.semantic}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Store Memory */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Save className="w-5 h-5" />
            Store New Memory
          </h2>
          <div className="space-y-4">
            <textarea
              value={newMemory.content}
              onChange={(e) => setNewMemory({ ...newMemory, content: e.target.value })}
              placeholder="Memory content..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 h-24 resize-none"
            />
            <select
              value={newMemory.memory_type}
              onChange={(e) => setNewMemory({ ...newMemory, memory_type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="episodic">Episodic (Experience)</option>
              <option value="semantic">Semantic (Knowledge)</option>
              <option value="procedural">Procedural (How-to)</option>
            </select>
            <div>
              <label className="text-sm text-gray-600">Importance: {newMemory.importance}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={newMemory.importance}
                onChange={(e) => setNewMemory({ ...newMemory, importance: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
            <input
              type="text"
              value={newMemory.tags}
              onChange={(e) => setNewMemory({ ...newMemory, tags: e.target.value })}
              placeholder="Tags (comma separated)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
            <button
              onClick={handleStore}
              disabled={loading}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Storing...' : 'Store Memory'}
            </button>
          </div>
        </div>

        {/* Search & List */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Search className="w-5 h-5" />
              Memories
            </h2>
            <div className="flex gap-2">
              <button
                onClick={handleConsolidate}
                disabled={loading}
                className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Consolidate
              </button>
              <button
                onClick={loadMemories}
                className="px-3 py-1.5 text-sm bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100"
              >
                Refresh
              </button>
            </div>
          </div>

          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search memories..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              <Search className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {memories.length === 0 && !loading && (
              <p className="text-gray-500 text-center py-8">No memories found</p>
            )}
            {memories.map((memory) => (
              <div key={memory.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${getTypeColor(memory.memory_type)}`}>
                    {memory.memory_type}
                  </span>
                  <span className="text-xs text-gray-500">
                    Accessed: {memory.access_count}x
                  </span>
                </div>
                <p className="text-gray-800 text-sm mb-2">{memory.content}</p>
                <div className="flex items-center gap-2 flex-wrap">
                  {memory.tags?.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                  <span>Importance: {memory.importance}</span>
                  <span>{new Date(memory.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
