import { useQuery } from 'react-query'
import { 
  Users, 
  Zap, 
  Activity, 
  DollarSign,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react'
import MetricsCard from '../components/MetricsCard'
import { healthApi, agentsApi } from '../services/api'

export default function Dashboard() {
  const { data: health } = useQuery('health', () => healthApi.check().then((r: any) => r.data))
  const { data: metrics } = useQuery('metrics', () => healthApi.getMetrics().then((r: any) => r.data), {
    refetchInterval: 30000,
  })
  const { data: costs } = useQuery('costs', () => healthApi.getCosts().then((r: any) => r.data), {
    refetchInterval: 60000,
  })
  const { data: alerts } = useQuery('alerts', () => healthApi.getAlerts().then((r: any) => r.data), {
    refetchInterval: 30000,
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          AI Startup Multi-Agent System v{health?.version || '2.0.0'}
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricsCard
          title="Total Agents"
          value={metrics?.agents?.total || 0}
          subtitle={`${metrics?.agents?.idle || 0} idle, ${metrics?.agents?.busy || 0} busy`}
          icon={<Users className="w-5 h-5 text-primary-600" />}
        />
        <MetricsCard
          title="Active Skills"
          value={25}
          subtitle="10 Fable 5 + 15 Advanced"
          icon={<Zap className="w-5 h-5 text-primary-600" />}
        />
        <MetricsCard
          title="Success Rate"
          value={`${((metrics?.performance?.success_rate || 0) * 100).toFixed(1)}%`}
          change={2.5}
          subtitle="Last 24 hours"
          icon={<Activity className="w-5 h-5 text-primary-600" />}
        />
        <MetricsCard
          title="Daily Cost"
          value={`$${(costs?.daily_cost || 0).toFixed(2)}`}
          subtitle={`Budget: $${costs?.budget || 1000}`}
          icon={<DollarSign className="w-5 h-5 text-primary-600" />}
        />
      </div>

      {/* Alerts */}
      {alerts && alerts.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2" />
            Active Alerts ({alerts.length})
          </h2>
          <div className="space-y-3">
            {alerts.map((alert: any, i: number) => (
              <div key={i} className={`p-4 rounded-lg ${
                alert.severity === 'critical' ? 'bg-red-50 border border-red-200' :
                alert.severity === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
                'bg-blue-50 border border-blue-200'
              }`}>
                <p className="text-sm font-medium">{alert.message}</p>
                <p className="text-xs text-gray-500 mt-1">{alert.type}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Task Overview</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                <span className="text-gray-600">Completed</span>
              </div>
              <span className="font-semibold">{metrics?.tasks?.completed || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <XCircle className="w-5 h-5 text-red-500 mr-3" />
                <span className="text-gray-600">Failed</span>
              </div>
              <span className="font-semibold">{metrics?.tasks?.failed || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Activity className="w-5 h-5 text-blue-500 mr-3" />
                <span className="text-gray-600">Running</span>
              </div>
              <span className="font-semibold">{metrics?.tasks?.running || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-500 mr-3" />
                <span className="text-gray-600">Pending</span>
              </div>
              <span className="font-semibold">{metrics?.tasks?.pending || 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Agent Utilization</span>
                <span className="font-medium">{((metrics?.agents?.utilization || 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all"
                  style={{ width: `${(metrics?.agents?.utilization || 0) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Budget Usage</span>
                <span className="font-medium">{costs?.budget_percentage || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all ${
                    (costs?.budget_percentage || 0) > 80 ? 'bg-red-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${costs?.budget_percentage || 0}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Avg Response Time</span>
                <span className="font-medium">{(metrics?.performance?.avg_response_time_ms || 0).toFixed(0)}ms</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min((metrics?.performance?.avg_response_time_ms || 0) / 50, 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
