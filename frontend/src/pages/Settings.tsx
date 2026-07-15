import { useState, useEffect } from 'react'
import { settingsApi } from '../services/api'
import { 
  Brain, Check, AlertTriangle, RefreshCw, Key, Zap, Globe, Server,
  Sparkles, Cpu, Cloud, Bot, MessageSquare, Flame, Star, Eye, EyeOff
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

const PROVIDER_INFO: Record<string, { icon: string; color: string; desc: string }> = {
  groq: { icon: 'zap', color: 'text-yellow-500', desc: 'Ultra-fast inference with Llama & Mixtral models' },
  openai: { icon: 'brain', color: 'text-green-500', desc: 'GPT-4o, GPT-4 Turbo, GPT-3.5' },
  google: { icon: 'globe', color: 'text-blue-500', desc: 'Gemini 1.5 Pro & Flash' },
  anthropic: { icon: 'sparkles', color: 'text-orange-500', desc: 'Claude 3.5 Sonnet & Opus' },
  mistral: { icon: 'cpu', color: 'text-cyan-500', desc: 'Mistral Large & Medium' },
  cohere: { icon: 'cloud', color: 'text-indigo-500', desc: 'Command R Plus & Command R' },
  ollama: { icon: 'server', color: 'text-purple-500', desc: 'Local LLMs - Llama3, Phi4, Qwen' },
  huggingface: { icon: 'bot', color: 'text-yellow-600', desc: 'FREE inference API for open models' },
  openrouter: { icon: 'message-square', color: 'text-teal-500', desc: 'FREE models + 100+ providers' },
  xai: { icon: 'flame', color: 'text-red-500', desc: 'Grok Beta & Grok Vision' },
  kimi: { icon: 'star', color: 'text-pink-500', desc: 'Moonshot v1 (8K, 32K, 128K)' },
}

const LLM_MODES = [
  { id: 'auto', label: 'Auto', desc: 'Automatically selects best available provider' },
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
  const [activeProvider, setActiveProvider] = useState<string | null>(null)
  const [llmMode, setLlmMode] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [testing, setTesting] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [showKey, setShowKey] = useState<Record<string, boolean>>({})
  const [editingKey, setEditingKey] = useState<Record<string, string>>({})

  useEffect(() => {
    loadProviders()
    loadLlmMode()
  }, [])

  const loadProviders = async () => {
    try {
      const res = await settingsApi.getProviders()
      setProviders(res || [])
      const active = res?.find((p: AIProvider) => p.is_active)
      if (active) setActiveProvider(active.id)
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

  const handleSetActive = async (providerId: string) => {
    setLoading(true)
    try {
      await settingsApi.setActiveProvider(providerId)
      setActiveProvider(providerId)
      setMessage(`${PROVIDER_INFO[providerId]?.label || providerId} is now active!`)
      loadProviders()
    } catch (e) {
      setMessage(`Error setting ${providerId} as active`)
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
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

  const toggleShowKey = (providerId: string) => {
    setShowKey(prev => ({ ...prev, [providerId]: !prev[providerId] }))
  }

  const getProviderIcon = (providerId: string) => {
    const info = PROVIDER_INFO[providerId] || { color: 'text-gray-500' }
    const className = `w-6 h-6 ${info.color}`
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

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-8 h-8 text-indigo-600" />
        <h1 className="text-3xl font-bold text-gray-900">AI Provider Settings</h1>
        <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded-full">
          11 Providers
        </span>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.includes('Error') || message.includes('failed')
            ? 'bg-red-50 text-red-700 border border-red-200'
            : message.includes('active') || message.includes('updated')
            ? 'bg-green-50 text-green-700 border border-green-200'
            : 'bg-blue-50 text-blue-700 border border-blue-200'
        }`}>
          {message}
        </div>
      )}

      {/* LLM Mode Selector */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">LLM Mode</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
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
        </p>
      </div>

      {/* Active Provider Banner */}
      {activeProvider && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-xl mb-6">
          <div className="flex items-center gap-2">
            <Check className="w-5 h-5 text-green-600" />
            <span className="font-medium text-green-800">
              Active: {providers.find(p => p.id === activeProvider)?.name}
            </span>
            <span className="text-sm text-green-600 ml-2">
              ({providers.find(p => p.id === activeProvider)?.default_model})
            </span>
          </div>
        </div>
      )}

      {/* Providers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {providers.map((provider) => {
          const info = PROVIDER_INFO[provider.id] || { desc: '' }
          const isEditing = editingKey[provider.id] !== undefined
          const displayKey = isEditing 
            ? editingKey[provider.id] 
            : (showKey[provider.id] ? provider.api_key : provider.api_key ? '••••••••••••••••' : '')

          return (
            <div
              key={provider.id}
              className={`bg-white p-5 rounded-xl shadow-sm border transition-all ${
                provider.is_active 
                  ? 'border-indigo-500 ring-2 ring-indigo-100' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gray-50 rounded-lg">
                    {getProviderIcon(provider.id)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{provider.name}</h3>
                    <p className="text-xs text-gray-500">{info.desc}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  {provider.id !== 'ollama' && (
                    <button
                      onClick={() => handleTestProvider(provider.id)}
                      disabled={testing === provider.id || !hasKey(provider)}
                      className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 flex items-center gap-1"
                    >
                      <RefreshCw className={`w-3 h-3 ${testing === provider.id ? 'animate-spin' : ''}`} />
                      {testing === provider.id ? 'Testing...' : 'Test'}
                    </button>
                  )}
                  <button
                    onClick={() => handleSetActive(provider.id)}
                    disabled={provider.id !== 'ollama' && !hasKey(provider)}
                    className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 ${
                      provider.is_active
                        ? 'bg-green-100 text-green-700 cursor-default'
                        : 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 disabled:opacity-50'
                    }`}
                  >
                    {provider.is_active ? (
                      <><Check className="w-3 h-3" /> Active</>
                    ) : (
                      'Set Active'
                    )}
                  </button>
                </div>
              </div>

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
              <div className="grid grid-cols-2 gap-3">
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
              <div className="mt-3">
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

              {/* Status */}
              {!hasKey(provider) && provider.id !== 'ollama' && (
                <div className="mt-3 flex items-center gap-2 text-xs text-amber-600 bg-amber-50 p-2 rounded-lg">
                  <AlertTriangle className="w-3 h-3" />
                  <span>No API key. Add key to enable.</span>
                </div>
              )}
              {hasKey(provider) && (
                <div className="mt-3 flex items-center gap-2 text-xs text-green-600 bg-green-50 p-2 rounded-lg">
                  <Check className="w-3 h-3" />
                  <span>API key configured</span>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
