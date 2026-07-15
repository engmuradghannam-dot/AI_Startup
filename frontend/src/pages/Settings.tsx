import { useState, useEffect } from 'react'
import { settingsApi } from '../services/api'
import { Brain, Check, AlertTriangle, RefreshCw, Key, Zap, Globe, Server } from 'lucide-react'

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

export default function SettingsPage() {
  const [providers, setProviders] = useState<AIProvider[]>([])
  const [activeProvider, setActiveProvider] = useState<string | null>(null)
  const [llmMode, setLlmMode] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [testing, setTesting] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [showKey, setShowKey] = useState<Record<string, boolean>>({})

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
      setMessage(`${providerId} updated successfully!`)
      loadProviders()
    } catch (e) {
      setMessage(`Error updating ${providerId}`)
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
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
      setMessage(`${providerId} is now active!`)
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
    switch (providerId) {
      case 'groq': return <Zap className="w-5 h-5 text-yellow-500" />
      case 'openai': return <Brain className="w-5 h-5 text-green-500" />
      case 'google': return <Globe className="w-5 h-5 text-blue-500" />
      case 'ollama': return <Server className="w-5 h-5 text-purple-500" />
      default: return <Key className="w-5 h-5 text-gray-500" />
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-8 h-8 text-indigo-600" />
        <h1 className="text-3xl font-bold text-gray-900">AI Settings</h1>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.includes('Error') ? 'bg-red-50 text-red-700 border border-red-200' :
          message.includes('active') ? 'bg-green-50 text-green-700 border border-green-200' :
          'bg-blue-50 text-blue-700 border border-blue-200'
        }`}>
          {message}
        </div>
      )}

      {/* LLM Mode */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">LLM Mode</h2>
        <div className="flex gap-3">
          {['auto', 'cloud', 'local'].map((mode) => (
            <button
              key={mode}
              onClick={() => handleSetLlmMode(mode)}
              className={`px-4 py-2 rounded-lg capitalize ${
                llmMode === mode
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
        <p className="text-sm text-gray-500 mt-2">
          Auto: Automatically selects the best available provider
        </p>
      </div>

      {/* Active Provider */}
      {activeProvider && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-xl mb-6">
          <div className="flex items-center gap-2">
            <Check className="w-5 h-5 text-green-600" />
            <span className="font-medium text-green-800">
              Active Provider: {providers.find(p => p.id === activeProvider)?.name}
            </span>
          </div>
        </div>
      )}

      {/* Providers List */}
      <div className="space-y-4">
        {providers.map((provider) => (
          <div
            key={provider.id}
            className={`bg-white p-6 rounded-xl shadow-sm border ${
              provider.is_active ? 'border-indigo-500 ring-1 ring-indigo-500' : 'border-gray-200'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                {getProviderIcon(provider.id)}
                <div>
                  <h3 className="font-semibold text-gray-900">{provider.name}</h3>
                  <p className="text-sm text-gray-500">{provider.base_url}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleTestProvider(provider.id)}
                  disabled={testing === provider.id || !provider.api_key}
                  className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 flex items-center gap-1"
                >
                  <RefreshCw className={`w-3 h-3 ${testing === provider.id ? 'animate-spin' : ''}`} />
                  {testing === provider.id ? 'Testing...' : 'Test'}
                </button>
                <button
                  onClick={() => handleSetActive(provider.id)}
                  disabled={!provider.api_key || provider.is_active}
                  className={`px-3 py-1.5 text-sm rounded-lg flex items-center gap-1 ${
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

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* API Key */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                <div className="flex gap-2">
                  <input
                    type={showKey[provider.id] ? 'text' : 'password'}
                    value={provider.api_key}
                    onChange={(e) => handleUpdateProvider(provider.id, { api_key: e.target.value })}
                    placeholder="Enter API key"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  <button
                    onClick={() => toggleShowKey(provider.id)}
                    className="px-3 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200"
                  >
                    {showKey[provider.id] ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>

              {/* Model */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                <input
                  type="text"
                  value={provider.default_model}
                  onChange={(e) => handleUpdateProvider(provider.id, { default_model: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>

              {/* Temperature */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Temperature: {provider.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={provider.temperature}
                  onChange={(e) => handleUpdateProvider(provider.id, { temperature: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              {/* Max Tokens */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
                <input
                  type="number"
                  value={provider.max_tokens}
                  onChange={(e) => handleUpdateProvider(provider.id, { max_tokens: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>

            {!provider.api_key && provider.id !== 'ollama' && (
              <div className="mt-3 flex items-center gap-2 text-sm text-amber-600">
                <AlertTriangle className="w-4 h-4" />
                <span>No API key configured. Add a key to enable this provider.</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
