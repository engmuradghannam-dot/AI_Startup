import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Key, Database, Globe, Save, TestTube, Trash2, Plus } from 'lucide-react'
import toast from 'react-hot-toast'

// AI Providers configuration
interface AIProvider {
  id: string
  name: string
  keyName: string
  keyValue: string
  baseUrl: string
  models: string[]
  isActive: boolean
}

const DEFAULT_PROVIDERS: AIProvider[] = [
  {
    id: 'groq',
    name: 'Groq',
    keyName: 'GROQ_API_KEY',
    keyValue: '',
    baseUrl: 'https://api.groq.com/openai/v1',
    models: ['llama-3.1-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'gemma-7b-it'],
    isActive: true,
  },
  {
    id: 'openai',
    name: 'OpenAI',
    keyName: 'OPENAI_API_KEY',
    keyValue: '',
    baseUrl: 'https://api.openai.com/v1',
    models: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    isActive: false,
  },
  {
    id: 'anthropic',
    name: 'Anthropic Claude',
    keyName: 'ANTHROPIC_API_KEY',
    keyValue: '',
    baseUrl: 'https://api.anthropic.com/v1',
    models: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
    isActive: false,
  },
  {
    id: 'google',
    name: 'Google Gemini',
    keyName: 'GOOGLE_API_KEY',
    keyValue: '',
    baseUrl: 'https://generativelanguage.googleapis.com/v1',
    models: ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'],
    isActive: false,
  },
  {
    id: 'cohere',
    name: 'Cohere',
    keyName: 'COHERE_API_KEY',
    keyValue: '',
    baseUrl: 'https://api.cohere.com/v1',
    models: ['command-r-plus', 'command-r', 'command'],
    isActive: false,
  },
  {
    id: 'mistral',
    name: 'Mistral AI',
    keyName: 'MISTRAL_API_KEY',
    keyValue: '',
    baseUrl: 'https://api.mistral.ai/v1',
    models: ['mistral-large-latest', 'mistral-medium-latest', 'mistral-small-latest'],
    isActive: false,
  },
]

// Storage helpers
const getStoredProviders = (): AIProvider[] => {
  try {
    const stored = localStorage.getItem('ai_startup_providers')
    if (stored) return JSON.parse(stored)
  } catch { }
  return DEFAULT_PROVIDERS
}

const storeProviders = (providers: AIProvider[]) => {
  localStorage.setItem('ai_startup_providers', JSON.stringify(providers))
}

const getStoredMongoUri = (): string => {
  try {
    return localStorage.getItem('ai_startup_mongodb_uri') || ''
  } catch { }
  return ''
}

const storeMongoUri = (uri: string) => {
  localStorage.setItem('ai_startup_mongodb_uri', uri)
}

export default function Settings() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('ai')
  const [providers, setProviders] = useState<AIProvider[]>(getStoredProviders())
  const [mongoUri, setMongoUri] = useState(getStoredMongoUri())
  const [selectedProvider, setSelectedProvider] = useState<string>('')
  const [testResult, setTestResult] = useState<string>('')

  const tabs = [
    { id: 'ai', label: 'AI Providers', icon: Key },
    { id: 'database', label: 'Database', icon: Database },
    { id: 'general', label: 'General', icon: Globe },
  ]

  const handleSaveProviders = () => {
    storeProviders(providers)
    toast.success('AI providers saved successfully')
  }

  const handleSaveMongo = () => {
    storeMongoUri(mongoUri)
    toast.success('MongoDB connection saved')
  }

  const updateProviderKey = (providerId: string, keyValue: string) => {
    setProviders(prev => prev.map(p =>
      p.id === providerId ? { ...p, keyValue } : p
    ))
  }

  const toggleProvider = (providerId: string) => {
    setProviders(prev => prev.map(p =>
      p.id === providerId ? { ...p, isActive: !p.isActive } : p
    ))
  }

  const handleTestConnection = async (provider: AIProvider) => {
    setTestResult(`Testing ${provider.name}...`)

    // Mock test - in real app, this would call the API
    setTimeout(() => {
      if (provider.keyValue) {
        setTestResult(`✅ ${provider.name} connection successful!`)
        toast.success(`${provider.name} is working`)
      } else {
        setTestResult(`❌ ${provider.name} failed: No API key provided`)
        toast.error(`Please enter ${provider.name} API key`)
      }
    }, 1500)
  }

  const handleTestMongo = async () => {
    setTestResult('Testing MongoDB connection...')

    setTimeout(() => {
      if (mongoUri) {
        setTestResult('✅ MongoDB connection string saved!')
        toast.success('MongoDB configuration saved')
      } else {
        setTestResult('❌ Please enter MongoDB URI')
        toast.error('MongoDB URI is required')
      }
    }, 1000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Configure AI providers and system settings</p>
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

      {/* AI Providers Tab */}
      {activeTab === 'ai' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-medium text-gray-900">AI Providers</h2>
                <p className="text-sm text-gray-500">Configure API keys for AI models</p>
              </div>
              <button
                onClick={handleSaveProviders}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center text-sm"
              >
                <Save className="w-4 h-4 mr-2" />
                Save All
              </button>
            </div>

            <div className="space-y-4">
              {providers.map((provider) => (
                <div
                  key={provider.id}
                  className={`border rounded-lg p-4 transition-colors ${
                    provider.isActive ? 'border-primary-200 bg-primary-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        provider.isActive ? 'bg-green-500' : 'bg-gray-300'
                      }`} />
                      <h3 className="font-medium text-gray-900">{provider.name}</h3>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleTestConnection(provider)}
                        className="px-3 py-1 text-sm text-primary-600 hover:bg-primary-50 rounded-lg flex items-center"
                      >
                        <TestTube className="w-4 h-4 mr-1" />
                        Test
                      </button>
                      <label className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={provider.isActive}
                          onChange={() => toggleProvider(provider.id)}
                          className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">Active</span>
                      </label>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        API Key
                      </label>
                      <input
                        type="password"
                        value={provider.keyValue}
                        onChange={(e) => updateProviderKey(provider.id, e.target.value)}
                        placeholder={`Enter ${provider.name} API key`}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Base URL
                        </label>
                        <input
                          type="text"
                          value={provider.baseUrl}
                          readOnly
                          className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Default Model
                        </label>
                        <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-sm">
                          {provider.models.map((model) => (
                            <option key={model} value={model}>{model}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`p-4 rounded-lg ${
              testResult.includes('✅') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {testResult}
            </div>
          )}
        </div>
      )}

      {/* Database Tab */}
      {activeTab === 'database' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-medium text-gray-900">MongoDB Connection</h2>
                <p className="text-sm text-gray-500">Configure database connection</p>
              </div>
              <button
                onClick={handleSaveMongo}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center text-sm"
              >
                <Save className="w-4 h-4 mr-2" />
                Save
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  MongoDB URI
                </label>
                <input
                  type="password"
                  value={mongoUri}
                  onChange={(e) => setMongoUri(e.target.value)}
                  placeholder="mongodb+srv://username:password@cluster.mongodb.net/database"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Format: mongodb+srv://username:password@cluster.mongodb.net/database
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Database Name
                </label>
                <input
                  type="text"
                  value="ai_startup"
                  readOnly
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-gray-500"
                />
              </div>

              <button
                onClick={handleTestMongo}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center text-sm"
              >
                <TestTube className="w-4 h-4 mr-2" />
                Test Connection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* General Tab */}
      {activeTab === 'general' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">General Settings</h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h3 className="font-medium text-gray-900">Auto-deploy</h3>
                  <p className="text-sm text-gray-500">Automatically deploy on push</p>
                </div>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enabled</span>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h3 className="font-medium text-gray-900">Debug Mode</h3>
                  <p className="text-sm text-gray-500">Show detailed error messages</p>
                </div>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enabled</span>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h3 className="font-medium text-gray-900">Clear Local Data</h3>
                  <p className="text-sm text-gray-500">Remove all local storage data</p>
                </div>
                <button
                  onClick={() => {
                    localStorage.clear()
                    toast.success('Local data cleared')
                  }}
                  className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg text-sm flex items-center"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Clear
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
