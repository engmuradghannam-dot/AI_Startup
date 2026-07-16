import { useCallback, useEffect, useRef, useState } from 'react'

// Minimal typing for the Web Speech API (not in default TS lib)
interface SpeechRecognitionResultLike {
  isFinal: boolean
  0: { transcript: string }
}
interface SpeechRecognitionEventLike extends Event {
  resultIndex: number
  results: ArrayLike<SpeechRecognitionResultLike>
}
interface SpeechRecognitionLike extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start: () => void
  stop: () => void
  abort: () => void
  onresult: ((event: SpeechRecognitionEventLike) => void) | null
  onerror: ((event: any) => void) | null
  onend: (() => void) | null
}

const getSpeechRecognition = (): (new () => SpeechRecognitionLike) | null => {
  const w = window as any
  return w.SpeechRecognition || w.webkitSpeechRecognition || null
}

export const ASSISTANT_NAME = 'Nova'
const WAKE_PHRASES = ['hey nova', 'hi nova', 'ok nova', 'okay nova']

export type VoiceAssistantStatus =
  | 'unsupported'
  | 'off'
  | 'listening-for-wake'
  | 'listening-for-command'
  | 'speaking'

const FATAL_ERRORS = new Set(['not-allowed', 'audio-capture', 'service-not-allowed'])

interface UseVoiceAssistantOptions {
  onCommand: (transcript: string) => void
  onError?: (message: string) => void
}

export function useVoiceAssistant({ onCommand, onError }: UseVoiceAssistantOptions) {
  const SpeechRecognitionCtor = getSpeechRecognition()
  const [status, setStatus] = useState<VoiceAssistantStatus>(SpeechRecognitionCtor ? 'off' : 'unsupported')
  const [liveTranscript, setLiveTranscript] = useState('')

  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
  const enabledRef = useRef(false)
  const modeRef = useRef<'wake' | 'command'>('wake')
  const onCommandRef = useRef(onCommand)
  onCommandRef.current = onCommand
  const onErrorRef = useRef(onError)
  onErrorRef.current = onError

  const speak = useCallback((text: string) => {
    if (!('speechSynthesis' in window) || !text) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.onstart = () => setStatus('speaking')
    utterance.onend = () => setStatus(enabledRef.current ? 'listening-for-wake' : 'off')
    window.speechSynthesis.speak(utterance)
  }, [])

  const startRecognition = useCallback((mode: 'wake' | 'command') => {
    if (!SpeechRecognitionCtor) return
    modeRef.current = mode
    setLiveTranscript('')

    const recognition = new SpeechRecognitionCtor()
    recognition.continuous = mode === 'wake'
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      let finalTranscript = ''
      let interimTranscript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) finalTranscript += result[0].transcript
        else interimTranscript += result[0].transcript
      }

      if (modeRef.current === 'wake') {
        const heard = (finalTranscript + ' ' + interimTranscript).toLowerCase()
        if (WAKE_PHRASES.some((phrase) => heard.includes(phrase))) {
          recognition.abort()
          setStatus('listening-for-command')
          startRecognition('command')
        }
        return
      }

      // command mode
      setLiveTranscript(finalTranscript || interimTranscript)
      if (finalTranscript.trim()) {
        recognition.abort()
        modeRef.current = 'wake'
        onCommandRef.current(finalTranscript.trim())
        setStatus(enabledRef.current ? 'listening-for-wake' : 'off')
      }
    }

    recognition.onerror = (event) => {
      if (event.error === 'aborted') return // we called .abort() ourselves - part of normal flow

      if (FATAL_ERRORS.has(event.error)) {
        enabledRef.current = false
        setStatus(SpeechRecognitionCtor ? 'off' : 'unsupported')
        onErrorRef.current?.(
          event.error === 'audio-capture'
            ? 'No microphone detected. Voice control has been turned off.'
            : 'Microphone access was denied. Please allow microphone permissions and try again.'
        )
        return
      }

      // recoverable error (e.g. no-speech, network) - fall back to wake listening
      modeRef.current = 'wake'
      setStatus(enabledRef.current ? 'listening-for-wake' : 'off')
    }

    recognition.onend = () => {
      // browsers auto-stop continuous recognition after a while - restart while enabled
      if (enabledRef.current && modeRef.current === 'wake') {
        startRecognition('wake')
      }
    }

    recognitionRef.current = recognition
    recognition.start()
    if (mode === 'wake') setStatus('listening-for-wake')
  }, [SpeechRecognitionCtor])

  const enable = useCallback(() => {
    if (!SpeechRecognitionCtor || enabledRef.current) return
    enabledRef.current = true
    startRecognition('wake')
  }, [SpeechRecognitionCtor, startRecognition])

  const disable = useCallback(() => {
    enabledRef.current = false
    recognitionRef.current?.abort()
    window.speechSynthesis?.cancel()
    setStatus(SpeechRecognitionCtor ? 'off' : 'unsupported')
  }, [SpeechRecognitionCtor])

  const toggle = useCallback(() => {
    if (enabledRef.current) disable()
    else enable()
  }, [enable, disable])

  useEffect(() => () => disable(), [disable])

  return { status, liveTranscript, toggle, speak, isSupported: !!SpeechRecognitionCtor }
}
