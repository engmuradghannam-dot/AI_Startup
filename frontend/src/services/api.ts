import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Agents API
export const agentsApi = {
  list: () => api.get('/agents/'),
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
  list: () => api.get('/skills/'),
  get: (id: string) => api.get(`/skills/${id}`),
  create: (data: any) => api.post('/skills/', data),
  update: (id: string, data: any) => api.put(`/skills/${id}`, data),
  delete: (id: string) => api.delete(`/skills/${id}`),
  execute: (id: string, data: any) => api.post(`/skills/${id}/execute`, data),
  getCategories: () => api.get('/skills/categories/summary'),
}

// Training API
export const trainingApi = {
  getDatasets: () => api.get('/training/datasets'),
  createDataset: (name: string, description: string, type: string) => 
    api.post('/training/datasets', null, { params: { name, description, dataset_type: type } }),
  getFeedbackStats: (agentId?: string) => api.get('/training/feedback/stats', { params: { agent_id: agentId } }),
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
