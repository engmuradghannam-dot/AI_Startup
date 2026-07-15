// API Client v3.0 - Local LLM + Multi-Agent Support
import axios from 'axios'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || window?.location?.origin?.replace(/\/+$/, '') || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
    })
    return res.data
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

// Export all APIs
export default {
  agents: agentsApi,
  aiChat: aiChatApi,
  localLlm: localLlmApi,
  skills: skillsApi,
  health: healthApi,
  training: trainingApi,
  voice: voiceApi,
}
