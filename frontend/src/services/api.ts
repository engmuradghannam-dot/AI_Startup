// API Client v2.1 - Fixed array/object validation for production\nimport axios from 'axios'

// @ts-ignore - Vite env types
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || window?.location?.origin?.replace(/\/$/, '') || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ✅ Helper to ensure response data is an Array
const ensureArray = (response: any): any[] => {
  if (!response) return []
  if (Array.isArray(response)) return response
  // If Object containing data/results/items/agents/skills/datasets
  if (typeof response === 'object') {
    return response.data || response.results || response.items ||
           response.agents || response.skills || response.datasets || []
  }
  return []
}

// ✅ Helper to ensure response data is an Object
const ensureObject = (response: any): any => {
  if (!response) return {}
  if (typeof response === 'object' && !Array.isArray(response)) return response
  return {}
}

// Agents API
export const agentsApi = {
  list: async () => {
    const res = await api.get('/agents/')
    return { ...res, data: ensureArray(res.data) }
  },
  get: (id: string) => api.get(`/agents/${id}`),
  create: (data: any) => api.post('/agents/', data),
  update: (id: string, data: any) => api.put(`/agents/${id}`, data),
  delete: (id: string) => api.delete(`/agents/${id}`),
  clone: (id: string, newName: string) => api.post(`/agents/${id}/clone`, null, { params: { new_name: newName } }),
  getMetrics: (id: string) => api.get(`/agents/${id}/metrics`),
  execute: (id: string, data: any) => api.post(`/agents/${id}/execute`, data),
  getScalingMetrics: () => api.get('/agents/scaling/metrics'),
  scaleUp: (count: number, role: string) => api.post('/agents/scaling/scale-up', null, { params: { count, role } }),
  getLoadMetrics: () => api.get('/agents/load/metrics'),
}

// Skills API
export const skillsApi = {
  list: async () => {
    const res = await api.get('/skills/')
    return { ...res, data: ensureArray(res.data) }
  },
  get: (id: string) => api.get(`/skills/${id}`),
  create: (data: any) => api.post('/skills/', data),
  update: (id: string, data: any) => api.put(`/skills/${id}`, data),
  delete: (id: string) => api.delete(`/skills/${id}`),
  execute: (id: string, data: any) => api.post(`/skills/${id}/execute`, data),
  getCategories: async () => {
    const res = await api.get('/skills/categories/summary')
    return { ...res, data: ensureObject(res.data) }
  },
}

// Training API
export const trainingApi = {
  getDatasets: async () => {
    const res = await api.get('/training/datasets')
    return { ...res, data: ensureArray(res.data) }
  },
  createDataset: (name: string, description: string, type: string) =>
    api.post('/training/datasets', null, { params: { name, description, dataset_type: type } }),
  getFeedbackStats: async (agentId?: string) => {
    const res = await api.get('/training/feedback/stats', { params: { agent_id: agentId } })
    return { ...res, data: ensureObject(res.data) }
  },
  processFeedback: (limit: number) => api.post('/training/feedback/process', null, { params: { limit } }),
  getMemory: (agentId: string) => api.get(`/training/memory/${agentId}`),
  getKnowledgeGraph: (agentId: string) => api.get(`/training/knowledge-graph/${agentId}`),
}

// Health API
export const healthApi = {
  check: () => api.get('/health/'),
  getMetrics: () => api.get('/health/metrics'),
  getCosts: () => api.get('/health/costs'),
  getSecurity: () => api.get('/health/security'),
  getAlerts: () => api.get('/health/alerts'),
}

export default api
