import type { CoverageMetrics } from '../../types/analysis';

interface CoverageChartProps {
  coverage: CoverageMetrics;
  title?: string;
}

export default function CoverageChart({ coverage, title = 'Coverage Analysis' }: CoverageChartProps) {
  const servedPercentage = coverage.coverage_percentage;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="font-semibold text-gray-900 mb-4">{title}</h3>

      {/* Donut Chart Representation */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative w-48 h-48">
          {/* Simple visual representation */}
          <svg viewBox="0 0 100 100" className="w-full h-full">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="20"
            />
            {/* Served arc */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke={servedPercentage >= 70 ? '#10b981' : servedPercentage >= 50 ? '#f59e0b' : '#ef4444'}
              strokeWidth="20"
              strokeDasharray={`${servedPercentage * 2.51} ${(100 - servedPercentage) * 2.51}`}
              strokeDashoffset="0"
              transform="rotate(-90 50 50)"
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-3xl font-bold text-gray-900">
              {servedPercentage.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-600">Coverage</div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="space-y-3">
        <div className="flex items-center justify-between p-3 bg-green-50 rounded">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm font-medium text-green-900">Served</span>
          </div>
          <div className="text-right">
            <div className="text-sm font-semibold text-green-900">
              {coverage.served_households} households
            </div>
            <div className="text-xs text-green-700">
              {coverage.served_population} people
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between p-3 bg-red-50 rounded">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-sm font-medium text-red-900">Underserved</span>
          </div>
          <div className="text-right">
            <div className="text-sm font-semibold text-red-900">
              {coverage.underserved_households} households
            </div>
            <div className="text-xs text-red-700">
              {coverage.underserved_population} people
            </div>
          </div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-gray-600">Total Buildings</div>
          <div className="font-semibold text-gray-900">{coverage.total_buildings}</div>
        </div>
        <div>
          <div className="text-gray-600">Avg Distance</div>
          <div className="font-semibold text-gray-900">
            {coverage.average_distance.toFixed(0)}m
          </div>
        </div>
      </div>
    </div>
  );
}
