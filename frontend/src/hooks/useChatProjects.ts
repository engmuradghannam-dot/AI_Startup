import { useCallback, useEffect, useRef, useState } from 'react'

export interface StoredMessage {
  id: string
  role: 'user' | 'agent' | 'system'
  content: string
  agentName?: string
  timestamp: string
  source?: string
  provider?: string
  agentTrace?: any[]
}

export interface ChatProject {
  id: string
  name: string
  createdAt: string
  updatedAt: string
  messages: StoredMessage[]
}

const PROJECTS_KEY = 'ai-startup:chat-projects'
const ACTIVE_PROJECT_KEY = 'ai-startup:active-project-id'

const generateId = () => Math.random().toString(36).substring(2, 10)

const loadProjects = (): ChatProject[] => {
  try {
    const raw = localStorage.getItem(PROJECTS_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

const saveProjects = (projects: ChatProject[]) => {
  try {
    localStorage.setItem(PROJECTS_KEY, JSON.stringify(projects))
  } catch {
    // storage full or unavailable - conversation just won't persist
  }
}

const makeProject = (name: string): ChatProject => ({
  id: generateId(),
  name,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  messages: [],
})

export function useChatProjects() {
  const initialized = useRef(false)
  const [projects, setProjects] = useState<ChatProject[]>([])
  const [activeProjectId, setActiveProjectId] = useState<string>('')

  useEffect(() => {
    if (initialized.current) return
    initialized.current = true

    let loaded = loadProjects()
    if (loaded.length === 0) {
      loaded = [makeProject('New Chat')]
      saveProjects(loaded)
    }

    const storedActive = localStorage.getItem(ACTIVE_PROJECT_KEY)
    const active = loaded.find((p) => p.id === storedActive) || loaded[0]

    setProjects(loaded)
    setActiveProjectId(active.id)
  }, [])

  const persist = useCallback((next: ChatProject[]) => {
    setProjects(next)
    saveProjects(next)
  }, [])

  const activeProject = projects.find((p) => p.id === activeProjectId) || null

  const switchProject = useCallback((id: string) => {
    setActiveProjectId(id)
    localStorage.setItem(ACTIVE_PROJECT_KEY, id)
  }, [])

  const createProject = useCallback((name: string = 'New Chat') => {
    const project = makeProject(name)
    setProjects((prev) => {
      const next = [project, ...prev]
      saveProjects(next)
      return next
    })
    switchProject(project.id)
    return project.id
  }, [switchProject])

  const renameProject = useCallback((id: string, name: string) => {
    setProjects((prev) => {
      const next = prev.map((p) => (p.id === id ? { ...p, name, updatedAt: new Date().toISOString() } : p))
      saveProjects(next)
      return next
    })
  }, [])

  const deleteProject = useCallback((id: string) => {
    setProjects((prev) => {
      const next = prev.filter((p) => p.id !== id)
      const withFallback = next.length > 0 ? next : [makeProject('New Chat')]
      saveProjects(withFallback)
      if (id === activeProjectId) switchProject(withFallback[0].id)
      return withFallback
    })
  }, [activeProjectId, switchProject])

  const updateActiveMessages = useCallback((messages: StoredMessage[]) => {
    if (!activeProjectId) return
    setProjects((prev) => {
      const next = prev.map((p) =>
        p.id === activeProjectId ? { ...p, messages, updatedAt: new Date().toISOString() } : p
      )
      saveProjects(next)
      return next
    })
  }, [activeProjectId])

  return {
    projects,
    activeProjectId,
    activeProject,
    switchProject,
    createProject,
    renameProject,
    deleteProject,
    updateActiveMessages,
  }
}
