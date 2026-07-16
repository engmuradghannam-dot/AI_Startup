// API Client v3.0 - Local LLM + Multi-Agent Support
import axios from 'axios'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || window?.location?.origin?.replace(/\/+$/, '') || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Stable anonymous id for this browser - lets the assistant remember
// preferences/corrections across conversations without a login system.
const USER_ID_KEY = 'ai-startup:anonymous-user-id'
export const getAnonymousUserId = (): string => {
  let id = localStorage.getItem(USER_ID_KEY)
  if (!id) {
    id = 'anon-' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36)
    localStorage.setItem(USER_ID_KEY, id)
  }
  return id
}

// Helper to ensure response data is an Array
const ensureArray = (response: any): any[] => {
  if (!response) return []
  if (Array.isArray(response)) return response
  if (typeof response === 'object') {
    return response.data || response.results || response.items ||
           response.agents || response.skills || response.datasets || []
  }
  return []
}

// Helper to ensure response data is an Object
const ensureObject = (response: any): any => {
  if (!response) return {}
  if (typeof response === 'object' && !Array.isArray(response)) return response
  return {}
}

// ============================================
// AGENTS API
// ============================================
export const agentsApi = {
  list: async () => {
    const res = await api.get('/api/agents/')
    return { ...res, data: ensureArray(res.data) }
  },
  get: (id: string) => api.get(`/api/agents/${id}`),
  create: (data: any) => api.post('/api/agents/', data),
  update: (id: string, data: any) => api.put(`/api/agents/${id}`, data),
  delete: (id: string) => api.delete(`/api/agents/${id}`),
  clone: (id: string, newName: string) => api.post(`/api/agents/${id}/clone`, null, { params: { new_name: newName } }),
  execute: (id: string, data: any) => api.post(`/api/agents/${id}/execute`, data),
  scaleUp: (count: number, role: string) => api.post('/api/agents/scale-up', null, { params: { count, role } }),
  getMetrics: () => api.get('/api/agents/metrics'),
}

// ============================================
// AI CHAT API - Unified (Local LLM + Groq)
// ============================================
export const aiChatApi = {
  // Main chat endpoint - auto-detects complexity
  chat: async (messages: any[], options: any = {}) => {
    const res = await api.post('/api/ai-chat/chat', {
      messages,
      model: options.model || null,
      temperature: options.temperature || 0.7,
      max_tokens: options.max_tokens || 2048,
      stream: options.stream || false,
      agent_mode: options.agent_mode || 'auto',
      attachment: options.attachment || null,
      user_id: options.user_id === undefined ? getAnonymousUserId() : options.user_id,
    })
    return res.data
  },

  // Streaming chat - calls onDelta(text) as each token chunk arrives, resolves with final metadata
  chatStream: async (
    messages: any[],
    options: any = {},
    onDelta: (text: string) => void,
    onToolCall?: (call: { name: string; arguments: string }) => void
  ): Promise<{ content: string; model?: string; provider?: string; source?: string; usage?: any; agent_trace?: any[] }> => {
    const response = await fetch(`${API_BASE_URL}/api/ai-chat/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages,
        model: options.model || null,
        temperature: options.temperature || 0.7,
        max_tokens: options.max_tokens || 2048,
        agent_mode: options.agent_mode || 'auto',
        attachment: options.attachment || null,
        user_id: options.user_id === undefined ? getAnonymousUserId() : options.user_id,
      }),
    })

    if (!response.ok || !response.body) {
      throw new Error(`Stream request failed: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let content = ''
    let final: any = {}

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = JSON.parse(line.slice(6))
        if (payload.error) throw new Error(payload.error)
        if (payload.delta) {
          content += payload.delta
          onDelta(payload.delta)
        }
        if (payload.tool_call && onToolCall) onToolCall(payload.tool_call)
        if (payload.done) final = payload
      }
    }

    return { content, ...final }
  },

  // Multi-agent chat
  agentChat: async (task: string, agents?: string[], mode: string = 'hierarchical') => {
    const res = await api.post('/api/ai-chat/agent-chat', {
      task,
      agents,
      mode,
    })
    return res.data
  },

  // Skill-based chat
  skillChat: async (task: string, skills: string[]) => {
    const res = await api.post('/api/ai-chat/skill-chat', {
      task,
      skills,
    })
    return res.data
  },

  // Get all available models
  getModels: async () => {
    const res = await api.get('/api/ai-chat/models')
    return ensureArray(res.data)
  },

  // Get all agents
  getAgents: async () => {
    const res = await api.get('/api/ai-chat/agents')
    return res.data?.agents || []
  },

  // Get specific agent
  getAgent: async (name: string) => {
    const res = await api.get(`/api/ai-chat/agents/${name}`)
    return res.data
  },

  // Execute single agent
  executeAgent: async (name: string, task: string, context?: any) => {
    const res = await api.post(`/api/ai-chat/agents/${name}/execute`, { task, context })
    return res.data
  },

  // Clear agent memories
  clearAllMemory: () => api.post('/api/ai-chat/agents/clear-memory'),
  clearAgentMemory: (name: string) => api.post(`/api/ai-chat/agents/${name}/clear-memory`),

  // Health check
  getHealth: async () => {
    const res = await api.get('/api/ai-chat/health')
    return res.data
  },

  // Metrics
  getMetrics: async () => {
    const res = await api.get('/api/ai-chat/metrics')
    return res.data
  },
}

// ============================================
// LOCAL LLM API
// ============================================
export const localLlmApi = {
  // Health check
  getHealth: async () => {
    const res = await api.get('/api/local-llm/health')
    return res.data
  },

  // List all models
  getModels: async () => {
    const res = await api.get('/api/local-llm/models')
    return res.data
  },

  // Pull a model
  pullModel: async (modelName: string) => {
    const res = await api.post('/api/local-llm/models/pull', { model_name: modelName })
    return res.data
  },

  // Generate text
  generate: async (prompt: string, model?: string, temperature?: number, maxTokens?: number) => {
    const res = await api.post('/api/local-llm/generate', {
      prompt,
      model,
      temperature,
      max_tokens: maxTokens,
    })
    return res.data
  },

  // Get recommended models
  getRecommended: async () => {
    const res = await api.get('/api/local-llm/models/recommended')
    return res.data
  },
}

// ============================================
// SKILLS API
// ============================================
export const skillsApi = {
  list: async () => {
    const res = await api.get('/api/skills/')
    return { ...res, data: ensureArray(res.data) }
  },
  get: (id: string) => api.get(`/api/skills/${id}`),
  create: (data: any) => api.post('/api/skills/', data),
  update: (id: string, data: any) => api.put(`/api/skills/${id}`, data),
  delete: (id: string) => api.delete(`/api/skills/${id}`),
  execute: (id: string, data: any) => api.post(`/api/skills/${id}/execute`, data),
  getByCategory: (category: string) => api.get(`/api/skills/?category=${category}`),
  getCategories: () => api.get('/api/skills/categories'),
}

// ============================================
// HEALTH API
// ============================================
export const healthApi = {
  check: () => api.get('/api/health/'),
  detailed: () => api.get('/api/health/detailed'),
  getMetrics: async () => {
    const res = await api.get('/api/notifications/metrics')
    return res
  },
  getCosts: async () => {
    const res = await api.get('/api/ai-chat/metrics')
    return res
  },
  getAlerts: async () => {
    const res = await api.get('/api/notifications/?unread_only=true&limit=5')
    return res
  },
}

// ============================================
// TRAINING API
// ============================================
export const trainingApi = {
  getDatasets: async () => {
    const res = await api.get('/api/training/datasets')
    return { ...res, data: ensureArray(res.data) }
  },
  getJobs: async () => {
    const res = await api.get('/api/training/jobs')
    return { ...res, data: ensureArray(res.data) }
  },
  createJob: (data: any) => api.post('/api/training/jobs', data),
  getJobStatus: (id: string) => api.get(`/api/training/jobs/${id}/status`),
  getStats: async () => {
    const res = await api.get('/api/training/stats')
    return res
  },
}

// ============================================
// VOICE API
// ============================================
export const voiceApi = {
  synthesize: (text: string, voice?: string) =>
    api.post('/api/voice/synthesize', { text, voice }),
  transcribe: (audioData: FormData) =>
    api.post('/api/voice/transcribe', audioData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getVoices: () => api.get('/api/voice/voices'),
}
// ============================================
// MEMORY API
// ============================================
export const memoryApi = {
  store: async (data: any) => {
    const res = await api.post('/api/memory/store', data)
    return res.data
  },
  search: async (data: any) => {
    const res = await api.post('/api/memory/search', data)
    return ensureArray(res.data)
  },
  getAgentMemories: async (agentId: string, memoryType?: string, limit?: number) => {
    const params = new URLSearchParams()
    if (memoryType) params.append('memory_type', memoryType)
    if (limit) params.append('limit', limit.toString())
    const res = await api.get(`/api/memory/agent/${agentId}?${params.toString()}`)
    return ensureArray(res.data)
  },
  getStats: async (agentId: string) => {
    const res = await api.get(`/api/memory/stats/${agentId}`)
    return res.data
  },
  consolidate: async (agentId: string) => {
    const res = await api.post(`/api/memory/consolidate/${agentId}`)
    return res.data
  },
  export: async (agentId: string) => {
    const res = await api.post(`/api/memory/export/${agentId}`)
    return res.data
  },
  import: async (agentId: string, memories: any[]) => {
    const res = await api.post(`/api/memory/import/${agentId}`, memories)
    return res.data
  },
}

// ============================================
// LEARNING API
// ============================================
export const learningApi = {
  submitFeedback: async (data: any) => {
    const res = await api.post('/api/learning/feedback', data)
    return res.data
  },
  getStats: async (agentId: string) => {
    const res = await api.get(`/api/learning/stats/${agentId}`)
    return res.data
  },
  triggerLearning: async (agentId: string) => {
    const res = await api.post(`/api/learning/learn/${agentId}`)
    return res.data
  },
  exportKnowledge: async (agentId: string) => {
    const res = await api.get(`/api/learning/export/${agentId}`)
    return res.data
  },
  importKnowledge: async (agentId: string, knowledge: any) => {
    const res = await api.post(`/api/learning/import/${agentId}`, knowledge)
    return res.data
  },
  getPatterns: async (agentId: string, patternType?: string) => {
    const params = patternType ? `?pattern_type=${patternType}` : ''
    const res = await api.get(`/api/learning/patterns/${agentId}${params}`)
    return res.data
  },
}

// ============================================
// NOTIFICATIONS API
// ============================================
export const notificationsApi = {
  list: async (filters: any = {}) => {
    const params = new URLSearchParams()
    if (filters.unread_only) params.append('unread_only', 'true')
    if (filters.type) params.append('notification_type', filters.type)
    if (filters.priority) params.append('priority', filters.priority)
    if (filters.limit) params.append('limit', filters.limit.toString())
    const res = await api.get(`/api/notifications/?${params.toString()}`)
    return ensureArray(res.data)
  },
  create: async (data: any) => {
    const res = await api.post('/api/notifications/', data)
    return res.data
  },
  markAsRead: async (id: string) => {
    const res = await api.post(`/api/notifications/${id}/read`)
    return res.data
  },
  dismiss: async (id: string) => {
    const res = await api.post(`/api/notifications/${id}/dismiss`)
    return res.data
  },
  clearAll: async () => {
    const res = await api.delete('/api/notifications/')
    return res.data
  },
  getMetrics: async () => {
    const res = await api.get('/api/notifications/metrics')
    return res.data
  },
  getMetricHistory: async (metricName: string, hours?: number) => {
    const params = hours ? `?hours=${hours}` : ''
    const res = await api.get(`/api/notifications/metrics/${metricName}${params}`)
    return res.data
  },
  recordMetric: async (name: string, value: number, unit?: string, thresholdHigh?: number, thresholdLow?: number) => {
    const res = await api.post('/api/notifications/metrics/record', null, {
      params: { name, value, unit, threshold_high: thresholdHigh, threshold_low: thresholdLow }
    })
    return res.data
  },
  addAlertRule: async (data: any) => {
    const res = await api.post('/api/notifications/alert-rules', data)
    return res.data
  },
  getSystemHealth: async () => {
    const res = await api.get('/api/notifications/system/health')
    return res.data
  },
  getUnreadCount: async () => {
    const res = await api.get('/api/notifications/unread-count')
    return res.data
  },
}

// ============================================
// INTEGRATIONS API
// ============================================
export const integrationsApi = {
  list: async (filters: any = {}) => {
    const params = new URLSearchParams()
    if (filters.type) params.append('integration_type', filters.type)
    if (filters.status) params.append('status', filters.status)
    const res = await api.get(`/api/integrations/?${params.toString()}`)
    return ensureArray(res.data)
  },
  create: async (data: any) => {
    const res = await api.post('/api/integrations/', data)
    return res.data
  },
  get: async (id: string) => {
    const res = await api.get(`/api/integrations/${id}`)
    return res.data
  },
  update: async (id: string, data: any) => {
    const res = await api.patch(`/api/integrations/${id}`, data)
    return res.data
  },
  delete: async (id: string) => {
    const res = await api.delete(`/api/integrations/${id}`)
    return res.data
  },
  createApiKey: async (integrationId: string, data: any) => {
    const res = await api.post(`/api/integrations/${integrationId}/api-keys`, data)
    return res.data
  },
  listApiKeys: async (integrationId: string) => {
    const res = await api.get(`/api/integrations/${integrationId}/api-keys`)
    return ensureArray(res.data)
  },
  revokeApiKey: async (integrationId: string, keyId: string) => {
    const res = await api.delete(`/api/integrations/${integrationId}/api-keys/${keyId}`)
    return res.data
  },
  createWebhook: async (integrationId: string, data: any) => {
    const res = await api.post(`/api/integrations/${integrationId}/webhooks`, data)
    return res.data
  },
  listWebhooks: async (integrationId: string) => {
    const res = await api.get(`/api/integrations/${integrationId}/webhooks`)
    return ensureArray(res.data)
  },
  deleteWebhook: async (integrationId: string, webhookId: string) => {
    const res = await api.delete(`/api/integrations/${integrationId}/webhooks/${webhookId}`)
    return res.data
  },
  getAvailableEvents: async () => {
    const res = await api.get('/api/integrations/events/available')
    return ensureArray(res.data)
  },
  validateApiKey: async (apiKey: string) => {
    const res = await api.post('/api/integrations/validate-key', null, {
      headers: { 'X-API-Key': apiKey }
    })
    return res.data
  },
}


// ============================================
// SETTINGS API
// ============================================
export const settingsApi = {
  getProviders: async () => {
    const res = await api.get('/api/settings/providers')
    return ensureArray(res.data)
  },
  getProvider: async (id: string) => {
    const res = await api.get(`/api/settings/providers/${id}`)
    return res.data
  },
  updateProvider: async (id: string, data: any) => {
    const res = await api.patch(`/api/settings/providers/${id}`, data)
    return res.data
  },
  testProvider: async (id: string) => {
    const res = await api.post(`/api/settings/providers/${id}/test`)
    return res.data
  },
  getActiveProvider: async () => {
    const res = await api.get('/api/settings/active-provider')
    return res.data
  },
  setActiveProvider: async (id: string) => {
    const res = await api.post(`/api/settings/active-provider/${id}`)
    return res.data
  },
  getLlmMode: async () => {
    const res = await api.get('/api/settings/llm-mode')
    return res.data
  },
  setLlmMode: async (mode: string) => {
    const res = await api.post(`/api/settings/llm-mode/${mode}`)
    return res.data
  },
  ensembleQuery: async (data: { task: string; providers?: string[]; mode?: string; context?: any }) => {
    const res = await api.post('/api/settings/ensemble', data)
    return res.data
  },
}

// Export all APIs
export default {
  agents: agentsApi,
  aiChat: aiChatApi,
  localLlm: localLlmApi,
  skills: skillsApi,
  health: healthApi,
  training: trainingApi,
  voice: voiceApi,
  memory: memoryApi,
  learning: learningApi,
  notifications: notificationsApi,
  integrations: integrationsApi,
  settings: settingsApi,
}
