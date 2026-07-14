import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="bg-white rounded-xl shadow-lg p-8 max-w-lg w-full">
            <div className="text-red-500 text-5xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h1>
            <p className="text-gray-600 mb-4">The application encountered an error. Please try refreshing the page.</p>
            <div className="bg-gray-100 rounded-lg p-4 mb-4 overflow-auto">
              <code className="text-sm text-red-600">{this.state.error?.message || 'Unknown error'}</code>
            </div>
            <button 
              onClick={() => window.location.reload()} 
              className="w-full py-2 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
