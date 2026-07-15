import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery } from 'react-query'
import { 
  Send, Bot, User, Settings, Mic, MicOff, Paperclip, 
  Image, Video, FileText, Monitor, X, Volume2, VolumeX,
  Brain, Sparkles, Trash2, Download
} from 'lucide-react'
import { agentsApi } from '../services/api'
import axios from 'axios'
import toast from 'react-hot-toast'

// Local storage helpers
const getStoredAgents = () => {
  try {
    const stored = localStorage.getItem('ai_startup_agents')
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

const getStoredProviders = () => {
  try {
    const stored = localStorage.getItem('ai_startup_providers')
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

const getActiveProvider = () => {
  const providers = getStoredProviders()
  const active = providers.find((p: any) => p.isActive)
  return active || providers[0] || { id: 'groq', name: 'Groq', models: ['llama-3.1-70b-versatile'], keyValue: '' }
}

interface ChatMessage {
  id: string
  role: 'user' | 'agent' | 'system'
  content: string
  agentName?: string
  agentId?: string
  timestamp: string
  attachments?: Attachment[]
  voiceUrl?: string
  isVoice?: boolean
}

interface Attachment {
  id: string
  type: 'image' | 'video' | 'document' | 'audio'
  name: string
  url: string
  size: number
}

export default function AgentChat() {
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [selectedAgent, setSelectedAgent] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [attachments, setAttachments] = useState<Attachment[]>([])
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false)
  const [showScreenCapture, setShowScreenCapture] = useState(false)
  const [agentKnowledge, setAgentKnowledge] = useState<any[]>([])
  const [showKnowledge, setShowKnowledge] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const agents = getStoredAgents()

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  // Select first agent by default
  useEffect(() => {
    if (agents.length > 0 && !selectedAgent) {
      setSelectedAgent(agents[0])
    }
  }, [agents, selectedAgent])

  // Load agent knowledge
  const loadAgentKnowledge = useCallback(async (agentId: string) => {
    try {
      const res = await axios.get(`/api/training/learn/${agentId}`)
      if (res.data && res.data.knowledge) {
        setAgentKnowledge(res.data.knowledge)
      }
    } catch (e) {
      console.log('Knowledge load skipped:', e)
    }
  }, [])

  useEffect(() => {
    if (selectedAgent?.id) {
      loadAgentKnowledge(selectedAgent.id)
    }
  }, [selectedAgent, loadAgentKnowledge])

  const handleSend = async () => {
    if (!message.trim() && attachments.length === 0) return
    if (!selectedAgent) {
      toast.error('Please select an agent first')
      return
    }

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      attachments: attachments.length > 0 ? [...attachments] : undefined,
    }

    setChatHistory(prev => [...prev, userMsg])
    setMessage('')
    setAttachments([])
    setIsLoading(true)

    try {
      const provider = getActiveProvider()
      const messages = [
        { role: 'system', content: `You are ${selectedAgent.name}, an AI agent. ${selectedAgent.description || ''}` },
        ...chatHistory.map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content })),
        { role: 'user', content: message },
      ]

      const response = await axios.post('/ai-chat/chat', {
        provider: provider.id,
        model: provider.models[0],
        messages: messages,
        agent_name: selectedAgent.name,
        api_key: provider.keyValue,
      })

      const agentMsg: ChatMessage = {
        id: `agent_${Date.now()}`,
        role: 'agent',
        content: response.data.response || 'I apologize, I could not process that.',
        agentName: selectedAgent.name,
        agentId: selectedAgent.id,
        timestamp: new Date().toISOString(),
      }

      setChatHistory(prev => [...prev, agentMsg])

      // Learn from this conversation
      try {
        await axios.post('/api/training/learn/from-chat', {
          agent_id: selectedAgent.id,
          conversation: JSON.stringify({ user: message, agent: response.data.response }),
          user_feedback: null,
        })
      } catch (e) {
        // Silent fail for learning
      }

    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
      setChatHistory(prev => [...prev, {
        id: `error_${Date.now()}`,
        role: 'system',
        content: `Error: ${errorMsg}`,
        timestamp: new Date().toISOString(),
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // Voice Recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        await processVoiceAudio(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (e) {
      toast.error('Microphone access denied or not available')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const processVoiceAudio = async (audioBlob: Blob) => {
    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'voice_message.wav')
      formData.append('language', 'en')
      if (selectedAgent?.id) {
        formData.append('agent_id', selectedAgent.id)
      }

      // Speech-to-Text
      const sttRes = await axios.post('/api/voice/speech-to-text', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      const transcribedText = sttRes.data.text || '[Voice message]'

      // Add voice message to chat
      const voiceMsg: ChatMessage = {
        id: `voice_${Date.now()}`,
        role: 'user',
        content: transcribedText,
        timestamp: new Date().toISOString(),
        isVoice: true,
      }

      setChatHistory(prev => [...prev, voiceMsg])
      setMessage(transcribedText)

      // Auto-send after voice transcription
      await handleSend()

    } catch (e) {
      toast.error('Voice processing failed')
    } finally {
      setIsLoading(false)
    }
  }

  // Text-to-Speech
  const speakText = async (text: string) => {
    try {
      setIsSpeaking(true)

      // Use browser's built-in TTS
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = 'en-US'
        utterance.onend = () => setIsSpeaking(false)
        utterance.onerror = () => setIsSpeaking(false)
        window.speechSynthesis.speak(utterance)
      } else {
        // Fallback to API
        const res = await axios.post('/api/voice/text-to-speech', {
          text,
          voice: 'default',
          language: 'en',
        })

        if (res.data.audio_url) {
          const audio = new Audio(res.data.audio_url)
          audio.onended = () => setIsSpeaking(false)
          audio.play()
        }
      }
    } catch (e) {
      setIsSpeaking(false)
    }
  }

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
    setIsSpeaking(false)
  }

  // File Upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>, type: 'image' | 'video' | 'document') => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('agent_id', selectedAgent?.id || 'default')
    formData.append('description', `Uploaded ${type}: ${file.name}`)

    try {
      const res = await axios.post('/api/training/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      if (res.data.status === 'uploaded') {
        const newAttachment: Attachment = {
          id: res.data.entry_id,
          type,
          name: file.name,
          url: URL.createObjectURL(file),
          size: file.size,
        }
        setAttachments(prev => [...prev, newAttachment])
        toast.success(`${type} uploaded successfully`)
      }
    } catch (e) {
      toast.error('Upload failed')
    }
  }

  // Screen Capture
  const captureScreen = async () => {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { cursor: 'always' },
        audio: false,
      })

      const video = document.createElement('video')
      video.srcObject = stream
      await video.play()

      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx?.drawImage(video, 0, 0)

      const screenshot = canvas.toDataURL('image/png')

      // Stop stream
      stream.getTracks().forEach(track => track.stop())

      // Send to backend for learning
      await axios.post('/api/training/learn/screen', {
        agent_id: selectedAgent?.id || 'default',
        description: 'Screen capture from Agent Chat',
        screen_data: screenshot,
      })

      toast.success('Screen captured and saved for learning')
      setShowScreenCapture(false)
    } catch (e) {
      toast.error('Screen capture failed or cancelled')
    }
  }

  // Clear chat
  const clearChat = () => {
    setChatHistory([])
    toast.success('Chat cleared')
  }

  // Delete knowledge entry
  const deleteKnowledge = async (entryId: string) => {
    try {
      await axios.delete(`/api/training/learn/${selectedAgent.id}/${entryId}`)
      setAgentKnowledge(prev => prev.filter(k => k.id !== entryId))
      toast.success('Knowledge deleted')
    } catch (e) {
      toast.error('Failed to delete')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent Chat</h1>
          <p className="text-gray-600 mt-1">Chat with your AI agents - Voice, Files & Screen Capture</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowKnowledge(!showKnowledge)}
            className={`p-2 rounded-lg transition-colors ${showKnowledge ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
            title="Agent Knowledge"
          >
            <Brain className="w-5 h-5" />
          </button>
          <button
            onClick={clearChat}
            className="p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-red-100 hover:text-red-600 transition-colors"
            title="Clear Chat"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="flex gap-6">
        {/* Left Sidebar - Agents */}
        <div className="w-80 space-y-4">
          {/* Agent Selector */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="font-medium text-gray-900 mb-3 flex items-center">
              <Bot className="w-5 h-5 mr-2" />
              Available Agents ({agents.length})
            </h3>
            <div className="space-y-2">
              {agents.map((agent: any) => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent)}
                  className={`w-full flex items-center p-3 rounded-lg text-left transition-colors ${
                    selectedAgent?.id === agent.id
                      ? 'bg-primary-50 border-2 border-primary-500'
                      : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                  }`}
                >
                  <Bot className="w-8 h-8 mr-3 text-primary-600" />
                  <div>
                    <div className="font-medium text-gray-900">{agent.name}</div>
                    <div className="text-xs text-gray-500">{agent.role || 'general'}</div>
                  </div>
                  {selectedAgent?.id === agent.id && (
                    <Sparkles className="w-4 h-4 ml-auto text-primary-500" />
                  )}
                </button>
              ))}
              {agents.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-4">No agents available. Create agents first.</p>
              )}
            </div>
          </div>

          {/* Agent Knowledge Panel */}
          {showKnowledge && selectedAgent && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                Agent Knowledge ({agentKnowledge.length})
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {agentKnowledge.map((k: any) => (
                  <div key={k.id} className="p-2 bg-gray-50 rounded text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">{k.content_type || 'text'}</span>
                      <button onClick={() => deleteKnowledge(k.id)} className="text-red-400 hover:text-red-600">
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                    <p className="text-gray-700 mt-1 line-clamp-2">{k.content}</p>
                  </div>
                ))}
                {agentKnowledge.length === 0 && (
                  <p className="text-gray-400 text-sm text-center">No knowledge yet</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right - Chat Area */}
        <div className="flex-1 flex flex-col h-[600px]">
          <div className="bg-white rounded-lg border border-gray-200 flex flex-col h-full">
            {/* Chat Header */}
            <div className="border-b border-gray-200 p-4 flex items-center justify-between">
              <div className="flex items-center">
                {selectedAgent ? (
                  <>
                    <Bot className="w-6 h-6 mr-2 text-primary-600" />
                    <div>
                      <div className="font-medium text-gray-900">{selectedAgent.name}</div>
                      <div className="text-xs text-gray-500">{selectedAgent.role || 'general'} • active</div>
                    </div>
                  </>
                ) : (
                  <span className="text-gray-500">Select an agent</span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {isSpeaking && (
                  <button onClick={stopSpeaking} className="p-2 text-red-500 hover:bg-red-50 rounded-lg">
                    <VolumeX className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatHistory.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex items-start space-x-3 ${
                    msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    msg.role === 'user' ? 'bg-primary-600' : 
                    msg.role === 'system' ? 'bg-red-100' : 'bg-gray-200'
                  }`}>
                    {msg.role === 'user' ? (
                      <User className="w-5 h-5 text-white" />
                    ) : msg.role === 'system' ? (
                      <span className="text-red-500 text-lg">⚠️</span>
                    ) : (
                      <Bot className="w-5 h-5 text-gray-700" />
                    )}
                  </div>
                  <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    msg.role === 'user' 
                      ? 'bg-primary-600 text-white' 
                      : msg.role === 'system'
                      ? 'bg-red-50 text-red-900 border border-red-200'
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium opacity-75">
                        {msg.role === 'user' ? 'You' : msg.agentName || 'System'}
                      </span>
                      {msg.isVoice && <Mic className="w-3 h-3 opacity-50" />}
                    </div>
                    <div className="text-sm whitespace-pre-wrap">{msg.content}</div>

                    {/* Attachments */}
                    {msg.attachments && msg.attachments.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {msg.attachments.map(att => (
                          <div key={att.id} className="flex items-center space-x-2 bg-white/20 rounded p-2">
                            {att.type === 'image' && <Image className="w-4 h-4" />}
                            {att.type === 'video' && <Video className="w-4 h-4" />}
                            {att.type === 'document' && <FileText className="w-4 h-4" />}
                            <span className="text-xs">{att.name}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Agent actions */}
                    {msg.role === 'agent' && (
                      <div className="mt-2 flex items-center space-x-2">
                        <button
                          onClick={() => speakText(msg.content)}
                          className="p-1 rounded hover:bg-white/20 transition-colors"
                          title="Read aloud"
                        >
                          <Volume2 className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex items-center justify-center space-x-2 py-4">
                  <div className="w-3 h-3 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-3 h-3 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-3 h-3 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  <span className="ml-2 text-sm text-gray-500">Thinking...</span>
                </div>
              )}

              {chatHistory.length === 0 && (
                <div className="text-center text-gray-500 mt-20">
                  <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Start a conversation</p>
                  <p className="text-sm mt-1">Type, speak, or attach files</p>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Attachments Preview */}
            {attachments.length > 0 && (
              <div className="border-t border-gray-200 px-4 py-2 flex flex-wrap gap-2">
                {attachments.map(att => (
                  <div key={att.id} className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-1 text-sm">
                    {att.type === 'image' && <Image className="w-4 h-4 text-blue-500" />}
                    {att.type === 'video' && <Video className="w-4 h-4 text-red-500" />}
                    {att.type === 'document' && <FileText className="w-4 h-4 text-green-500" />}
                    <span className="text-gray-700">{att.name}</span>
                    <button onClick={() => setAttachments(prev => prev.filter(a => a.id !== att.id))}>
                      <X className="w-3 h-3 text-gray-400 hover:text-red-500" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Input Area */}
            <div className="border-t border-gray-200 p-4">
              <div className="flex items-end space-x-3">
                {/* Attachment Button */}
                <div className="relative">
                  <button
                    onClick={() => setShowAttachmentMenu(!showAttachmentMenu)}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  >
                    <Paperclip className="w-5 h-5" />
                  </button>

                  {showAttachmentMenu && (
                    <div className="absolute bottom-full left-0 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 p-2 space-y-1 z-10">
                      <button
                        onClick={() => { fileInputRef.current?.click(); setShowAttachmentMenu(false) }}
                        className="flex items-center space-x-2 w-full p-2 rounded hover:bg-gray-100 text-sm"
                      >
                        <Image className="w-4 h-4 text-blue-500" />
                        <span>Image</span>
                      </button>
                      <button
                        onClick={() => { fileInputRef.current?.click(); setShowAttachmentMenu(false) }}
                        className="flex items-center space-x-2 w-full p-2 rounded hover:bg-gray-100 text-sm"
                      >
                        <Video className="w-4 h-4 text-red-500" />
                        <span>Video</span>
                      </button>
                      <button
                        onClick={() => { fileInputRef.current?.click(); setShowAttachmentMenu(false) }}
                        className="flex items-center space-x-2 w-full p-2 rounded hover:bg-gray-100 text-sm"
                      >
                        <FileText className="w-4 h-4 text-green-500" />
                        <span>Document</span>
                      </button>
                      <button
                        onClick={() => { setShowAttachmentMenu(false); captureScreen() }}
                        className="flex items-center space-x-2 w-full p-2 rounded hover:bg-gray-100 text-sm"
                      >
                        <Monitor className="w-4 h-4 text-purple-500" />
                        <span>Screen Capture</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Voice Button */}
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`p-2 rounded-lg transition-colors ${
                    isRecording 
                      ? 'bg-red-100 text-red-600 animate-pulse' 
                      : 'text-gray-500 hover:text-primary-600 hover:bg-primary-50'
                  }`}
                >
                  {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>

                {/* Text Input */}
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSend()
                    }
                  }}
                  placeholder={isRecording ? 'Recording...' : `Message ${selectedAgent?.name || 'agent'}...`}
                  disabled={isLoading || isRecording}
                  rows={1}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 resize-none"
                  style={{ minHeight: '40px', maxHeight: '120px' }}
                />

                {/* Send Button */}
                <button
                  onClick={handleSend}
                  disabled={isLoading || isRecording || (!message.trim() && attachments.length === 0)}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-300 flex items-center"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={(e) => handleFileUpload(e, 'image')}
        accept="image/*,video/*,.pdf,.doc,.docx,.txt"
      />
    </div>
  )
}
