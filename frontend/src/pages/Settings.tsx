import { useState, useEffect } from 'react'
import { settingsApi, aiChatApi } from '../services/api'
import { 
  Brain, Check, AlertTriangle, RefreshCw, Key, Zap, Globe, Server,
  Sparkles, Cpu, Cloud, Bot, MessageSquare, Flame, Star, Eye, EyeOff,
  Users, Play, ChevronDown, ChevronUp, Copy, CheckCircle2
} from 'lucide-react'

interface AIProvider {
  id: string
  name: string
  api_key: string
  base_url: string
  default_model: string
  is_active: boolean
  temperature: number
  max_tokens: number
}

interface EnsembleResult {
  mode: string
  results: any[]
  errors: any[]
  providers_used: string[]
  providers_count: number
  final_answer?: string
  all_answers?: string[]
  consensus?: boolean
}

const PROVIDER_INFO: Record<string, { icon: string; color: string; desc: string; free: boolean }> = {
  groq: { icon: 'zap', color: 'text-yellow-500', desc: 'Ultra-fast inference', free: false },
  openai: { icon: 'brain', color: 'text-green-500', desc: 'GPT-4o & GPT-3.5', free: false },
  google: { icon: 'globe', color: 'text-blue-500', desc: 'Gemini 1.5 Pro', free: false },
  anthropic: { icon: 'sparkles', color: 'text-orange-500', desc: 'Claude 3.5 Sonnet', free: false },
  mistral: { icon: 'cpu', color: 'text-cyan-500', desc: 'Mistral Large', free: false },
  cohere: { icon: 'cloud', color: 'text-indigo-500', desc: 'Command R Plus', free: false },
  ollama: { icon: 'server', color: 'text-purple-500', desc: 'Local LLMs', free: true },
  huggingface: { icon: 'bot', color: 'text-yellow-600', desc: 'FREE open models', free: true },
  openrouter: { icon: 'message-square', color: 'text-teal-500', desc: 'FREE + 100+ providers', free: true },
  xai: { icon: 'flame', color: 'text-red-500', desc: 'Grok Beta', free: false },
  kimi: { icon: 'star', color: 'text-pink-500', desc: 'Moonshot v1', free: false },
}

const LLM_MODES = [
  { id: 'auto', label: 'Auto', desc: 'Automatically selects best available provider' },
  { id: 'ensemble', label: 'Ensemble', desc: 'All active providers work together' },
  { id: 'groq', label: 'Groq', desc: 'Fastest inference' },
  { id: 'openai', label: 'OpenAI', desc: 'GPT-4o & GPT-3.5' },
  { id: 'google', label: 'Google', desc: 'Gemini models' },
  { id: 'anthropic', label: 'Claude', desc: 'Anthropic Claude' },
  { id: 'mistral', label: 'Mistral', desc: 'Mistral AI' },
  { id: 'cohere', label: 'Cohere', desc: 'Command models' },
  { id: 'ollama', label: 'Ollama', desc: 'Local models' },
  { id: 'huggingface', label: 'Hugging Face', desc: 'FREE open models' },
  { id: 'openrouter', label: 'OpenRouter', desc: 'FREE + 100+ providers' },
  { id: 'xai', label: 'xAI', desc: 'Grok models' },
  { id: 'kimi', label: 'KIMI', desc: 'Moonshot' },
]

export default function SettingsPage() {
  const [providers, setProviders] = useState<AIProvider[]>([])
  const [activeProviders, setActiveProviders] = useState<string[]>([])
  const [llmMode, setLlmMode] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [testing, setTesting] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [showKey, setShowKey] = useState<Record<string, boolean>>({})
  const [editingKey, setEditingKey] = useState<Record<string, string>>({})
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null)

  // Ensemble test
  const [ensembleTask, setEnsembleTask] = useState('')
  const [ensembleResult, setEnsembleResult] = useState<EnsembleResult | null>(null)
  const [ensembleLoading, setEnsembleLoading] = useState(false)

  useEffect(() => {
    loadProviders()
    loadLlmMode()
  }, [])

  const loadProviders = async () => {
    try {
      const res = await settingsApi.getProviders()
      setProviders(res || [])
      const active = (res || []).filter((p: AIProvider) => p.is_active).map((p: AIProvider) => p.id)
      setActiveProviders(active)
    } catch (e) {
      console.error(e)
    }
  }

  const loadLlmMode = async () => {
    try {
      const res = await settingsApi.getLlmMode()
      setLlmMode(res?.mode || 'auto')
    } catch (e) {
      console.error(e)
    }
  }

  const handleUpdateProvider = async (providerId: string, updates: Partial<AIProvider>) => {
    setLoading(true)
    try {
      await settingsApi.updateProvider(providerId, updates)
      setMessage(`${PROVIDER_INFO[providerId]?.label || providerId} updated!`)
      loadProviders()
    } catch (e) {
      setMessage(`Error updating ${providerId}`)
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
  }

  const handleToggleActive = async (providerId: string) => {
    const provider = providers.find(p => p.id === providerId)
    if (!provider) return

    const newActive = !provider.is_active
    await handleUpdateProvider(providerId, { is_active: newActive })

    if (newActive) {
      setActiveProviders(prev => [...prev, providerId])
    } else {
      setActiveProviders(prev => prev.filter(id => id !== providerId))
    }
  }

  const handleSaveKey = async (providerId: string) => {
    const key = editingKey[providerId]
    if (key === undefined) return
    await handleUpdateProvider(providerId, { api_key: key })
    setEditingKey(prev => { const n = { ...prev }; delete n[providerId]; return n })
  }

  const handleTestProvider = async (providerId: string) => {
    setTesting(providerId)
    try {
      const res = await settingsApi.testProvider(providerId)
      setMessage(res?.message || 'Test completed')
    } catch (e) {
      setMessage(`Test failed for ${providerId}`)
    }
    setTesting(null)
    setTimeout(() => setMessage(''), 5000)
  }

  const handleSetLlmMode = async (mode: string) => {
    try {
      await settingsApi.setLlmMode(mode)
      setLlmMode(mode)
      setMessage(`LLM mode set to ${mode}`)
    } catch (e) {
      setMessage('Error setting LLM mode')
    }
    setTimeout(() => setMessage(''), 3000)
  }

  const handleEnsembleQuery = async () => {
    if (!ensembleTask.trim()) return
    setEnsembleLoading(true)
    try {
      const res = await settingsApi.ensembleQuery({
        task: ensembleTask,
        mode: 'parallel',
      })
      setEnsembleResult(res)
    } catch (e: any) {
      setMessage(`Ensemble error: ${e.response?.data?.detail || e.message}`)
      setTimeout(() => setMessage(''), 5000)
    }
    setEnsembleLoading(false)
  }

  const toggleShowKey = (providerId: string) => {
    setShowKey(prev => ({ ...prev, [providerId]: !prev[providerId] }))
  }

  const getProviderIcon = (providerId: string) => {
    const info = PROVIDER_INFO[providerId] || { color: 'text-gray-500' }
    const className = `w-5 h-5 ${info.color}`
    switch (info.icon) {
      case 'zap': return <Zap className={className} />
      case 'brain': return <Brain className={className} />
      case 'globe': return <Globe className={className} />
      case 'sparkles': return <Sparkles className={className} />
      case 'cpu': return <Cpu className={className} />
      case 'cloud': return <Cloud className={className} />
      case 'server': return <Server className={className} />
      case 'bot': return <Bot className={className} />
      case 'message-square': return <MessageSquare className={className} />
      case 'flame': return <Flame className={className} />
      case 'star': return <Star className={className} />
      default: return <Key className={className} />
    }
  }

  const hasKey = (p: AIProvider) => p.api_key && p.api_key !== 'local' && p.api_key.length > 0
  const activeCount = activeProviders.length

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-8 h-8 text-indigo-600" />
        <h1 className="text-3xl font-bold text-gray-900">AI Provider Settings</h1>
        <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded-full">
          11 Providers
        </span>
        {activeCount > 0 && (
          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            {activeCount} Active
          </span>
        )}
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.includes('Error') || message.includes('failed')
            ? 'bg-red-50 text-red-700 border border-red-200'
            : message.includes('active') || message.includes('updated') || message.includes('set to')
            ? 'bg-green-50 text-green-700 border border-green-200'
            : 'bg-blue-50 text-blue-700 border border-blue-200'
        }`}>
          {message}
        </div>
      )}

      {/* LLM Mode Selector */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">LLM Mode</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          {LLM_MODES.map((mode) => (
            <button
              key={mode.id}
              onClick={() => handleSetLlmMode(mode.id)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                llmMode === mode.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-gray-50 text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
              title={mode.desc}
            >
              {mode.label}
            </button>
          ))}
        </div>
        <p className="text-sm text-gray-500 mt-2">
          {LLM_MODES.find(m => m.id === llmMode)?.desc || 'Select a mode'}
          {llmMode === 'ensemble' && (
            <span className="text-indigo-600 font-medium ml-1">
              — All {activeCount} active providers will work together!
            </span>
          )}
        </p>
      </div>

      {/* Active Providers Banner */}
      {activeCount > 0 && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-xl mb-6">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-5 h-5 text-green-600" />
            <span className="font-medium text-green-800">
              Active Providers ({activeCount}):
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {activeProviders.map(pid => {
              const p = providers.find(pr => pr.id === pid)
              return (
                <span key={pid} className="px-2 py-1 bg-white text-green-700 text-xs rounded-lg border border-green-200 flex items-center gap-1">
                  {getProviderIcon(pid)}
                  {p?.name || pid}
                </span>
              )
            })}
          </div>
        </div>
      )}

      {/* Ensemble Test Panel */}
      {llmMode === 'ensemble' && activeCount > 1 && (
        <div className="bg-indigo-50 border border-indigo-200 p-6 rounded-xl mb-6">
          <h3 className="font-semibold text-indigo-900 mb-3 flex items-center gap-2">
            <Users className="w-5 h-5" />
            Ensemble Test — Query Multiple AI Providers Together
          </h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={ensembleTask}
              onChange={(e) => setEnsembleTask(e.target.value)}
              placeholder="Ask something to all active providers..."
              className="flex-1 px-4 py-2 border border-indigo-300 rounded-lg text-sm"
              onKeyDown={(e) => e.key === 'Enter' && handleEnsembleQuery()}
            />
            <button
              onClick={handleEnsembleQuery}
              disabled={ensembleLoading || !ensembleTask.trim()}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              {ensembleLoading ? 'Querying...' : 'Query All'}
            </button>
          </div>

          {ensembleResult && (
            <div className="mt-4 space-y-3">
              <div className="flex items-center gap-2 text-sm text-indigo-700">
                <CheckCircle2 className="w-4 h-4" />
                <span>{ensembleResult.providers_count} providers responded</span>
                {ensembleResult.consensus && <span className="text-green-600">(Consensus reached!)</span>}
              </div>

              {ensembleResult.results.map((r: any, i: number) => (
                <div key={i} className="bg-white p-4 rounded-lg border border-indigo-100">
                  <div className="flex items-center gap-2 mb-2">
                    {getProviderIcon(r.provider)}
                    <span className="font-medium text-sm">{r.provider_name}</span>
                    <span className="text-xs text-gray-500">({r.model})</span>
                  </div>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{r.content}</p>
                </div>
              ))}

              {ensembleResult.errors.length > 0 && (
                <div className="bg-red-50 p-3 rounded-lg border border-red-200">
                  <p className="text-xs text-red-600 font-medium mb-1">Errors:</p>
                  {ensembleResult.errors.map((e: any, i: number) => (
                    <p key={i} className="text-xs text-red-500">{e.provider}: {e.error}</p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Providers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {providers.map((provider) => {
          const info = PROVIDER_INFO[provider.id] || { desc: '', free: false }
          const isExpanded = expandedProvider === provider.id
          const isEditing = editingKey[provider.id] !== undefined
          const displayKey = isEditing 
            ? editingKey[provider.id] 
            : (showKey[provider.id] ? provider.api_key : provider.api_key ? '••••••••••••••••' : '')

          return (
            <div
              key={provider.id}
              className={`bg-white rounded-xl shadow-sm border transition-all ${
                provider.is_active 
                  ? 'border-indigo-500 ring-2 ring-indigo-100' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {/* Header */}
              <div 
                className="p-5 flex items-start justify-between cursor-pointer"
                onClick={() => setExpandedProvider(isExpanded ? null : provider.id)}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gray-50 rounded-lg">
                    {getProviderIcon(provider.id)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900">{provider.name}</h3>
                      {info.free && (
                        <span className="px-1.5 py-0.5 bg-green-100 text-green-700 text-[10px] rounded-full font-medium">
                          FREE
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500">{info.desc}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {/* Toggle Active */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleToggleActive(provider.id)
                    }}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      provider.is_active ? 'bg-indigo-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        provider.is_active ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                </div>
              </div>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="px-5 pb-5 border-t border-gray-100 pt-4">
                  {/* API Key Input */}
                  <div className="mb-3">
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      {provider.id === 'ollama' ? 'Base URL' : 'API Key'}
                    </label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <input
                          type={showKey[provider.id] || isEditing ? 'text' : 'password'}
                          value={isEditing ? editingKey[provider.id] : (provider.api_key || '')}
                          onChange={(e) => {
                            if (provider.id === 'ollama') {
                              handleUpdateProvider(provider.id, { base_url: e.target.value })
                            } else {
                              setEditingKey(prev => ({ ...prev, [provider.id]: e.target.value }))
                            }
                          }}
                          placeholder={provider.id === 'ollama' ? 'http://localhost:11434' : 'Enter API key'}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm pr-10"
                        />
                        {provider.id !== 'ollama' && (
                          <button
                            onClick={() => toggleShowKey(provider.id)}
                            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                          >
                            {showKey[provider.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        )}
                      </div>
                      {isEditing && provider.id !== 'ollama' && (
                        <button
                          onClick={() => handleSaveKey(provider.id)}
                          className="px-3 py-2 text-xs bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                        >
                          Save
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Model & Settings */}
                  <div className="grid grid-cols-2 gap-3 mb-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Model</label>
                      <input
                        type="text"
                        value={provider.default_model}
                        onChange={(e) => handleUpdateProvider(provider.id, { default_model: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Max Tokens</label>
                      <input
                        type="number"
                        value={provider.max_tokens}
                        onChange={(e) => handleUpdateProvider(provider.id, { max_tokens: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>

                  {/* Temperature */}
                  <div className="mb-3">
                    <div className="flex justify-between">
                      <label className="text-xs font-medium text-gray-700">Temperature</label>
                      <span className="text-xs text-gray-500">{provider.temperature}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={provider.temperature}
                      onChange={(e) => handleUpdateProvider(provider.id, { temperature: parseFloat(e.target.value) })}
                      className="w-full mt-1"
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    {provider.id !== 'ollama' && (
                      <button
                        onClick={() => handleTestProvider(provider.id)}
                        disabled={testing === provider.id || !hasKey(provider)}
                        className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 flex items-center gap-1"
                      >
                        <RefreshCw className={`w-3 h-3 ${testing === provider.id ? 'animate-spin' : ''}`} />
                        {testing === provider.id ? 'Testing...' : 'Test Connection'}
                      </button>
                    )}
                  </div>

                  {/* Status */}
                  {!hasKey(provider) && provider.id !== 'ollama' && (
                    <div className="mt-3 flex items-center gap-2 text-xs text-amber-600 bg-amber-50 p-2 rounded-lg">
                      <AlertTriangle className="w-3 h-3" />
                      <span>No API key. Add key to enable this provider.</span>
                    </div>
                  )}
                  {hasKey(provider) && (
                    <div className="mt-3 flex items-center gap-2 text-xs text-green-600 bg-green-50 p-2 rounded-lg">
                      <Check className="w-3 h-3" />
                      <span>API key configured — Ready to use</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
