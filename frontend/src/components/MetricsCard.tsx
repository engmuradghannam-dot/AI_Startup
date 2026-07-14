import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface MetricsCardProps {
  title: string
  value: string | number
  change?: number
  subtitle?: string
  icon: React.ReactNode
}

export default function MetricsCard({ title, value, change, subtitle, icon }: MetricsCardProps) {
  const isPositive = change && change > 0
  const isNegative = change && change < 0

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <div className="p-2 bg-primary-50 rounded-lg">
          {icon}
        </div>
      </div>

      <div className="flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>

        {change !== undefined && (
          <div className={`flex items-center text-sm font-medium ${
            isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-500'
          }`}>
            {isPositive && <TrendingUp className="w-4 h-4 mr-1" />}
            {isNegative && <TrendingDown className="w-4 h-4 mr-1" />}
            {!isPositive && !isNegative && <Minus className="w-4 h-4 mr-1" />}
            {Math.abs(change)}%
          </div>
        )}
      </div>
    </div>
  )
}
