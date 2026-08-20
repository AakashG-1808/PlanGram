import { useEffect, useState } from 'react';
import { analysisApi } from '../../services/api';
import type { Village } from '../../types/village';
import type { VillageMetrics } from '../../types/analysis';

interface VillageMetricsPanelProps {
  village: Village;
  threshold: number;
}

export default function VillageMetricsPanel({ village, threshold }: VillageMetricsPanelProps) {
  const [metrics, setMetrics] = useState<VillageMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMetrics();
  }, [village.id, threshold]);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analysisApi.getVillageMetrics(village.id, threshold);
      setMetrics(data);
    } catch (err) {
      console.error('Error loading metrics:', err);
      setError('Failed to load village metrics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600">{error || 'No metrics available'}</div>
      </div>
    );
  }

  const waterCoverage = metrics.water_coverage;

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-gray-900">Village Insights</h3>
        <p className="text-sm text-gray-600 mt-1">
          Coverage analysis at {threshold}m threshold
        </p>
      </div>

      <div className="p-4 space-y-4">
        {/* Priority Level */}
        <div className={`p-3 rounded-lg ${
          metrics.priority_level === 'high' ? 'bg-red-50 border border-red-200' :
          metrics.priority_level === 'medium' ? 'bg-amber-50 border border-amber-200' :
          'bg-green-50 border border-green-200'
        }`}>
          <div className="flex items-center gap-2">
            <span className="text-lg">
              {metrics.priority_level === 'high' ? '🔴' :
               metrics.priority_level === 'medium' ? '🟡' : '🟢'}
            </span>
            <div className="flex-1">
              <div className={`text-sm font-semibold uppercase ${
                metrics.priority_level === 'high' ? 'text-red-900' :
                metrics.priority_level === 'medium' ? 'text-amber-900' :
                'text-green-900'
              }`}>
                {metrics.priority_level} Priority
              </div>
              {metrics.priority_factors.length > 0 && (
                <div className={`text-xs mt-1 ${
                  metrics.priority_level === 'high' ? 'text-red-700' :
                  metrics.priority_level === 'medium' ? 'text-amber-700' :
                  'text-green-700'
                }`}>
                  {metrics.priority_factors[0]}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Water Coverage */}
        {waterCoverage && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Water Access
            </h4>
            
            {/* Coverage Bar */}
            <div className="mb-3">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-700">Coverage</span>
                <span className="font-semibold text-gray-900">
                  {waterCoverage.coverage_percentage.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${
                    waterCoverage.coverage_percentage >= 70 ? 'bg-green-500' :
                    waterCoverage.coverage_percentage >= 50 ? 'bg-amber-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${waterCoverage.coverage_percentage}%` }}
                ></div>
              </div>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-2 gap-2 mb-3">
              <div className="bg-green-50 p-2 rounded">
                <div className="text-xs text-green-700">Served</div>
                <div className="text-lg font-bold text-green-900">
                  {waterCoverage.served_households}
                </div>
                <div className="text-xs text-green-600">
                  households
                </div>
              </div>
              <div className="bg-red-50 p-2 rounded">
                <div className="text-xs text-red-700">Underserved</div>
                <div className="text-lg font-bold text-red-900">
                  {waterCoverage.underserved_households}
                </div>
                <div className="text-xs text-red-600">
                  households
                </div>
              </div>
            </div>

            {/* Distance Metrics */}
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-gray-600">Avg Distance</div>
                <div className="font-semibold text-gray-900">
                  {waterCoverage.average_distance.toFixed(0)}m
                </div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-gray-600">Median</div>
                <div className="font-semibold text-gray-900">
                  {waterCoverage.median_distance.toFixed(0)}m
                </div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-gray-600">Max</div>
                <div className="font-semibold text-gray-900">
                  {waterCoverage.max_distance.toFixed(0)}m
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Underserved Clusters */}
        {metrics.underserved_clusters.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Underserved Areas
            </h4>
            <div className="space-y-2">
              {metrics.underserved_clusters.slice(0, 3).map((cluster) => (
                <div
                  key={cluster.cluster_id}
                  className="p-2 bg-amber-50 border border-amber-200 rounded text-xs"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-semibold text-amber-900">
                        {cluster.cluster_id.replace('_', ' ')}
                      </div>
                      <div className="text-amber-700 mt-1">
                        {cluster.households} households • {cluster.population} people
                      </div>
                      <div className="text-amber-600 mt-1">
                        Avg: {cluster.avg_distance_to_facility}m from facility
                      </div>
                    </div>
                    <div className="text-amber-900 font-semibold">
                      #{metrics.underserved_clusters.indexOf(cluster) + 1}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {metrics.underserved_clusters.length > 3 && (
              <div className="text-xs text-gray-600 mt-2 text-center">
                +{metrics.underserved_clusters.length - 3} more clusters
              </div>
            )}
          </div>
        )}

        {/* Infrastructure Summary */}
        <div className="pt-4 border-t">
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-gray-600">Water Facilities</span>
              <div className="font-semibold text-gray-900 text-lg">
                {metrics.water_facilities}
              </div>
            </div>
            <div>
              <span className="text-gray-600">Other Facilities</span>
              <div className="font-semibold text-gray-900 text-lg">
                {metrics.other_facilities}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
