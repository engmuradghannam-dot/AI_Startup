// API Client v2.3 - Fixed all endpoints for production
import axios from 'axios'

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
  getMetrics: (id: string) => api.get(`/api/agents/${id}/metrics`),
  getScalingMetrics: () => api.get('/api/agents/scaling/metrics'),
  getLoadMetrics: () => api.get('/api/agents/load/metrics'),
}

// Skills API
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
  getCategories: async () => {
    const res = await api.get('/api/skills/categories')
    return { ...res, data: ensureObject(res.data) }
  },
}

// Training API
export const trainingApi = {
  getDatasets: async () => {
    const res = await api.get('/api/training/datasets')
    return { ...res, data: ensureArray(res.data) }
  },
  createDataset: (name: string, description: string = '', type: string = 'conversations') =>
    api.post('/api/training/datasets', null, { params: { name, description, dataset_type: type } }),
  getFeedbackStats: async (agentId?: string) => {
    const res = await api.get('/api/training/feedback/stats', { params: { agent_id: agentId } })
    return { ...res, data: ensureObject(res.data) }
  },
  processFeedback: (limit: number) => api.post('/api/training/feedback/process', null, { params: { limit } }),
  getMemory: (agentId: string) => api.get(`/api/training/memory/${agentId}`),
  getStats: async () => {
    const res = await api.get('/api/training/stats')
    return { ...res, data: ensureObject(res.data) }
  },
}

// Health API
export const healthApi = {
  check: () => api.get('/api/health/'),
  getMetrics: () => api.get('/api/health/metrics'),
  getCosts: () => api.get('/api/health/costs'),
  getSecurity: () => api.get('/api/health/security'),
  getAlerts: () => api.get('/api/health/alerts'),
}

export default api
