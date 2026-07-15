import { useState, useEffect } from 'react'
import { integrationsApi } from '../services/api'
import { Plug, Key, Webhook, Plus, Trash2, Copy, Check, RefreshCw } from 'lucide-react'

interface Integration {
  id: string
  name: string
  type: string
  description: string
  status: string
  created_at: string
  webhook_count: number
  api_key_count: number
}

interface Webhook {
  id: string
  url: string
  events: string[]
  status: string
  created_at: string
  success_count: number
  fail_count: number
}

interface APIKey {
  id: string
  name: string
  permissions: string[]
  status: string
  created_at: string
  expires_at: string
  use_count: number
}

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null)
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [availableEvents, setAvailableEvents] = useState<any[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showWebhookModal, setShowWebhookModal] = useState(false)
  const [showApiKeyModal, setShowApiKeyModal] = useState(false)
  const [newIntegration, setNewIntegration] = useState({ name: '', type: 'webhook', description: '' })
  const [newWebhook, setNewWebhook] = useState({ url: '', events: [] as string[], description: '' })
  const [newApiKey, setNewApiKey] = useState({ name: '', permissions: [] as string[] })
  const [copiedKey, setCopiedKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadIntegrations()
    loadAvailableEvents()
  }, [])

  useEffect(() => {
    if (selectedIntegration) {
      loadWebhooks(selectedIntegration)
      loadApiKeys(selectedIntegration)
    }
  }, [selectedIntegration])

  const loadIntegrations = async () => {
    try {
      const res = await integrationsApi.list()
      setIntegrations(res || [])
    } catch (e) {
      console.error(e)
    }
  }

  const loadWebhooks = async (integrationId: string) => {
    try {
      const res = await integrationsApi.listWebhooks(integrationId)
      setWebhooks(res || [])
    } catch (e) {
      console.error(e)
    }
  }

  const loadApiKeys = async (integrationId: string) => {
    try {
      const res = await integrationsApi.listApiKeys(integrationId)
      setApiKeys(res || [])
    } catch (e) {
      console.error(e)
    }
  }

  const loadAvailableEvents = async () => {
    try {
      const res = await integrationsApi.getAvailableEvents()
      setAvailableEvents(res || [])
    } catch (e) {
      console.error(e)
    }
  }

  const handleCreateIntegration = async () => {
    if (!newIntegration.name.trim()) return
    setLoading(true)
    try {
      await integrationsApi.create({
        name: newIntegration.name,
        integration_type: newIntegration.type,
        description: newIntegration.description,
      })
      setNewIntegration({ name: '', type: 'webhook', description: '' })
      setShowCreateModal(false)
      setMessage('Integration created!')
      loadIntegrations()
    } catch (e) {
      setMessage('Error creating integration')
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
  }

  const handleCreateWebhook = async () => {
    if (!selectedIntegration || !newWebhook.url.trim()) return
    setLoading(true)
    try {
      await integrationsApi.createWebhook(selectedIntegration, {
        url: newWebhook.url,
        events: newWebhook.events,
        description: newWebhook.description,
      })
      setNewWebhook({ url: '', events: [], description: '' })
      setShowWebhookModal(false)
      setMessage('Webhook created!')
      loadWebhooks(selectedIntegration)
    } catch (e) {
      setMessage('Error creating webhook')
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
  }

  const handleCreateApiKey = async () => {
    if (!selectedIntegration || !newApiKey.name.trim()) return
    setLoading(true)
    try {
      const res = await integrationsApi.createApiKey(selectedIntegration, {
        name: newApiKey.name,
        permissions: newApiKey.permissions,
      })
      setNewApiKey({ name: '', permissions: [] })
      setShowApiKeyModal(false)
      setMessage('API Key created!')
      loadApiKeys(selectedIntegration)
      if (res?.key) {
        setCopiedKey(res.key)
      }
    } catch (e) {
      setMessage('Error creating API key')
    }
    setLoading(false)
    setTimeout(() => setMessage(''), 3000)
  }

  const handleDeleteIntegration = async (id: string) => {
    if (!confirm('Delete this integration?')) return
    try {
      await integrationsApi.delete(id)
      setMessage('Integration deleted!')
      loadIntegrations()
      if (selectedIntegration === id) setSelectedIntegration(null)
    } catch (e) {
      setMessage('Error deleting integration')
    }
    setTimeout(() => setMessage(''), 3000)
  }

  const handleDeleteWebhook = async (webhookId: string) => {
    if (!selectedIntegration) return
    try {
      await integrationsApi.deleteWebhook(selectedIntegration, webhookId)
      setMessage('Webhook deleted!')
      loadWebhooks(selectedIntegration)
    } catch (e) {
      setMessage('Error deleting webhook')
    }
    setTimeout(() => setMessage(''), 3000)
  }

  const handleRevokeApiKey = async (keyId: string) => {
    if (!selectedIntegration) return
    try {
      await integrationsApi.revokeApiKey(selectedIntegration, keyId)
      setMessage('API Key revoked!')
      loadApiKeys(selectedIntegration)
    } catch (e) {
      setMessage('Error revoking API key')
    }
    setTimeout(() => setMessage(''), 3000)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedKey(text)
    setTimeout(() => setCopiedKey(''), 2000)
  }

  const toggleEvent = (event: string) => {
    setNewWebhook(prev => ({
      ...prev,
      events: prev.events.includes(event)
        ? prev.events.filter(e => e !== event)
        : [...prev.events, event]
    }))
  }

  const togglePermission = (perm: string) => {
    setNewApiKey(prev => ({
      ...prev,
      permissions: prev.permissions.includes(perm)
        ? prev.permissions.filter(p => p !== perm)
        : [...prev.permissions, perm]
    }))
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Plug className="w-8 h-8 text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900">External Integrations</h1>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Integration
        </button>
      </div>

      {message && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700">
          {message}
        </div>
      )}

      {copiedKey && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700">API Key copied to clipboard!</p>
          <p className="text-xs text-blue-500 mt-1 font-mono">{copiedKey}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Integrations List */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Integrations</h2>
          <div className="space-y-3">
            {integrations.length === 0 && (
              <p className="text-gray-500 text-center py-8">No integrations yet</p>
            )}
            {integrations.map((integration) => (
              <div
                key={integration.id}
                onClick={() => setSelectedIntegration(integration.id)}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  selectedIntegration === integration.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{integration.name}</h3>
                    <p className="text-sm text-gray-500">{integration.type}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      integration.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {integration.status}
                    </span>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteIntegration(integration.id) }}
                      className="p-1 text-red-500 hover:bg-red-50 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="flex gap-4 mt-2 text-xs text-gray-500">
                  <span>{integration.webhook_count} webhooks</span>
                  <span>{integration.api_key_count} API keys</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Details */}
        <div className="lg:col-span-2 space-y-6">
          {selectedIntegration ? (
            <>
              {/* Webhooks */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Webhook className="w-5 h-5" />
                    Webhooks
                  </h2>
                  <button
                    onClick={() => setShowWebhookModal(true)}
                    className="px-3 py-1.5 text-sm bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 flex items-center gap-1"
                  >
                    <Plus className="w-3 h-3" />
                    Add Webhook
                  </button>
                </div>
                <div className="space-y-3">
                  {webhooks.length === 0 && (
                    <p className="text-gray-500 text-center py-4">No webhooks configured</p>
                  )}
                  {webhooks.map((webhook) => (
                    <div key={webhook.id} className="p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">{webhook.url}</p>
                          <div className="flex gap-2 mt-1">
                            {webhook.events.map((event) => (
                              <span key={event} className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                                {event}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="flex items-center gap-3 ml-4">
                          <div className="text-xs text-gray-500">
                            <span className="text-green-600">{webhook.success_count} OK</span>
                            {' / '}
                            <span className="text-red-600">{webhook.fail_count} Fail</span>
                          </div>
                          <button
                            onClick={() => handleDeleteWebhook(webhook.id)}
                            className="p-1 text-red-500 hover:bg-red-50 rounded"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* API Keys */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Key className="w-5 h-5" />
                    API Keys
                  </h2>
                  <button
                    onClick={() => setShowApiKeyModal(true)}
                    className="px-3 py-1.5 text-sm bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 flex items-center gap-1"
                  >
                    <Plus className="w-3 h-3" />
                    Add API Key
                  </button>
                </div>
                <div className="space-y-3">
                  {apiKeys.length === 0 && (
                    <p className="text-gray-500 text-center py-4">No API keys created</p>
                  )}
                  {apiKeys.map((key) => (
                    <div key={key.id} className="p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{key.name}</p>
                          <div className="flex gap-2 mt-1">
                            {key.permissions.map((perm) => (
                              <span key={perm} className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                                {perm}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-gray-500">{key.use_count} uses</span>
                          <button
                            onClick={() => handleRevokeApiKey(key.id)}
                            className="px-2 py-1 text-xs bg-red-50 text-red-700 rounded hover:bg-red-100"
                          >
                            Revoke
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-200 text-center">
              <Plug className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Select an integration to view details</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Integration Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-900 mb-4">New Integration</h2>
            <div className="space-y-4">
              <input
                type="text"
                value={newIntegration.name}
                onChange={(e) => setNewIntegration({ ...newIntegration, name: e.target.value })}
                placeholder="Integration name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
              <select
                value={newIntegration.type}
                onChange={(e) => setNewIntegration({ ...newIntegration, type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="webhook">Webhook</option>
                <option value="api_key">API Key</option>
                <option value="oauth">OAuth</option>
                <option value="plugin">Plugin</option>
              </select>
              <textarea
                value={newIntegration.description}
                onChange={(e) => setNewIntegration({ ...newIntegration, description: e.target.value })}
                placeholder="Description (optional)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg h-20 resize-none"
              />
              <div className="flex gap-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateIntegration}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Webhook Modal */}
      {showWebhookModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-900 mb-4">New Webhook</h2>
            <div className="space-y-4">
              <input
                type="url"
                value={newWebhook.url}
                onChange={(e) => setNewWebhook({ ...newWebhook, url: e.target.value })}
                placeholder="Webhook URL"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
              <textarea
                value={newWebhook.description}
                onChange={(e) => setNewWebhook({ ...newWebhook, description: e.target.value })}
                placeholder="Description (optional)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg h-20 resize-none"
              />
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Events</p>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {availableEvents.map((event) => (
                    <label key={event.event} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={newWebhook.events.includes(event.event)}
                        onChange={() => toggleEvent(event.event)}
                      />
                      <span className="text-sm text-gray-700">{event.event}</span>
                      <span className="text-xs text-gray-500">- {event.description}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowWebhookModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateWebhook}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create API Key Modal */}
      {showApiKeyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-900 mb-4">New API Key</h2>
            <div className="space-y-4">
              <input
                type="text"
                value={newApiKey.name}
                onChange={(e) => setNewApiKey({ ...newApiKey, name: e.target.value })}
                placeholder="Key name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Permissions</p>
                <div className="space-y-2">
                  {['read:agents', 'write:agents', 'read:skills', 'write:skills', 'read:chat', 'admin'].map((perm) => (
                    <label key={perm} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={newApiKey.permissions.includes(perm)}
                        onChange={() => togglePermission(perm)}
                      />
                      <span className="text-sm text-gray-700">{perm}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowApiKeyModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateApiKey}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
