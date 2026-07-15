import { useState, useEffect } from 'react'
import { notificationsApi } from '../services/api'
import { Bell, Check, X, AlertTriangle, Info, Activity, Trash2, RefreshCw } from 'lucide-react'

interface Notification {
  id: string
  title: string
  message: string
  type: string
  priority: string
  agent_id: string | null
  created_at: string
  read: boolean
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [metrics, setMetrics] = useState<any>({})
  const [systemHealth, setSystemHealth] = useState<any>(null)
  const [unreadCount, setUnreadCount] = useState(0)
  const [filter, setFilter] = useState({ unread_only: false, type: '', priority: '' })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadNotifications()
    loadMetrics()
    loadSystemHealth()
    loadUnreadCount()

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadNotifications()
      loadMetrics()
      loadUnreadCount()
    }, 30000)

    return () => clearInterval(interval)
  }, [filter])

  const loadNotifications = async () => {
    setLoading(true)
    try {
      const res = await notificationsApi.list(filter)
      setNotifications(res || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const loadMetrics = async () => {
    try {
      const res = await notificationsApi.getMetrics()
      setMetrics(res || {})
    } catch (e) {
      console.error(e)
    }
  }

  const loadSystemHealth = async () => {
    try {
      const res = await notificationsApi.getSystemHealth()
      setSystemHealth(res)
    } catch (e) {
      console.error(e)
    }
  }

  const loadUnreadCount = async () => {
    try {
      const res = await notificationsApi.getUnreadCount()
      setUnreadCount(res?.unread_count || 0)
    } catch (e) {
      console.error(e)
    }
  }

  const handleMarkAsRead = async (id: string) => {
    try {
      await notificationsApi.markAsRead(id)
      loadNotifications()
      loadUnreadCount()
    } catch (e) {
      console.error(e)
    }
  }

  const handleDismiss = async (id: string) => {
    try {
      await notificationsApi.dismiss(id)
      loadNotifications()
      loadUnreadCount()
    } catch (e) {
      console.error(e)
    }
  }

  const handleClearAll = async () => {
    try {
      await notificationsApi.clearAll()
      loadNotifications()
      loadUnreadCount()
    } catch (e) {
      console.error(e)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-700 border-red-200'
      case 'high': return 'bg-orange-100 text-orange-700 border-orange-200'
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'low': return 'bg-gray-100 text-gray-700 border-gray-200'
      default: return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'alert': return <AlertTriangle className="w-4 h-4" />
      case 'performance': return <Activity className="w-4 h-4" />
      case 'system': return <Info className="w-4 h-4" />
      default: return <Bell className="w-4 h-4" />
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Bell className="w-8 h-8 text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900">Notifications & Monitoring</h1>
          {unreadCount > 0 && (
            <span className="px-2 py-1 bg-red-500 text-white text-sm rounded-full">
              {unreadCount}
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { loadNotifications(); loadMetrics(); }}
            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={handleClearAll}
            className="px-3 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Clear All
          </button>
        </div>
      </div>

      {/* System Health */}
      {systemHealth && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-600">CPU Usage</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{systemHealth.cpu?.usage?.toFixed(1) || 0}%</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-600">Memory</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{systemHealth.memory?.percent?.toFixed(1) || 0}%</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-purple-500" />
              <span className="text-sm text-gray-600">Disk</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{systemHealth.disk?.percent?.toFixed(1) || 0}%</p>
          </div>
        </div>
      )}

      {/* Metrics */}
      {Object.keys(metrics).length > 0 && (
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Monitoring Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(metrics).map(([name, data]: [string, any]) => (
              <div key={name} className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600 capitalize">{name.replace('_', ' ')}</p>
                <p className="text-lg font-bold text-gray-900">{data.value?.toFixed(1) || 0}{data.unit}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          value={filter.priority}
          onChange={(e) => setFilter({ ...filter, priority: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value="">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          value={filter.type}
          onChange={(e) => setFilter({ ...filter, type: e.target.value })}
          className="px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value="">All Types</option>
          <option value="system">System</option>
          <option value="agent">Agent</option>
          <option value="task">Task</option>
          <option value="alert">Alert</option>
          <option value="performance">Performance</option>
        </select>
        <label className="flex items-center gap-2 px-3 py-2">
          <input
            type="checkbox"
            checked={filter.unread_only}
            onChange={(e) => setFilter({ ...filter, unread_only: e.target.checked })}
          />
          <span className="text-sm text-gray-700">Unread only</span>
        </label>
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {notifications.length === 0 && !loading && (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <Bell className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No notifications</p>
          </div>
        )}
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`p-4 rounded-xl border ${getPriorityColor(notification.priority)} ${
              notification.read ? 'opacity-60' : ''
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="mt-0.5">{getTypeIcon(notification.type)}</div>
                <div>
                  <h3 className="font-semibold text-sm">{notification.title}</h3>
                  <p className="text-sm mt-1">{notification.message}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs opacity-70">
                    <span className="capitalize">{notification.type}</span>
                    <span>{new Date(notification.created_at).toLocaleString()}</span>
                    {notification.agent_id && <span>Agent: {notification.agent_id}</span>}
                  </div>
                </div>
              </div>
              <div className="flex gap-1">
                {!notification.read && (
                  <button
                    onClick={() => handleMarkAsRead(notification.id)}
                    className="p-1.5 hover:bg-white/50 rounded"
                    title="Mark as read"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleDismiss(notification.id)}
                  className="p-1.5 hover:bg-white/50 rounded"
                  title="Dismiss"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
