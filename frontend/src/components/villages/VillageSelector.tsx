import { useEffect, useState } from 'react';
import { villageApi } from '../../services/api';
import type { Village } from '../../types/village';

interface VillageSelectorProps {
  onVillageSelect: (village: Village) => void;
  selectedVillageId?: string;
}

export default function VillageSelector({ onVillageSelect, selectedVillageId }: VillageSelectorProps) {
  const [villages, setVillages] = useState<Village[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVillages();
  }, []);

  const loadVillages = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await villageApi.getVillages();
      setVillages(data.villages);
    } catch (err) {
      setError('Failed to load villages');
      console.error('Error loading villages:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded mb-2"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600 flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
        <button
          onClick={loadVillages}
          className="mt-4 text-sm text-blue-600 hover:text-blue-700"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">Select Village</h2>
        <p className="text-sm text-gray-600 mt-1">
          Choose a village to view and plan infrastructure
        </p>
      </div>
      
      <div className="p-4 space-y-3">
        {villages.map((village) => (
          <button
            key={village.id}
            onClick={() => onVillageSelect(village)}
            className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
              selectedVillageId === village.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{village.name}</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {village.taluk}, {village.district}
                </p>
                
                <div className="mt-3 flex flex-wrap gap-2 text-xs">
                  <span className="px-2 py-1 bg-gray-100 rounded">
                    {village.estimated_households} households
                  </span>
                  <span className="px-2 py-1 bg-gray-100 rounded">
                    ~{village.estimated_population} population
                  </span>
                  <span className="px-2 py-1 bg-gray-100 rounded">
                    {village.area_sq_km} km²
                  </span>
                </div>


              </div>

              {selectedVillageId === village.id && (
                <div className="text-blue-500">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
