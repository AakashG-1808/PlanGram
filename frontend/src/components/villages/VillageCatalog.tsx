import { useEffect, useState } from 'react';
import { villageApi } from '../../services/api';
import type { Village } from '../../types/village';

interface VillageCatalogProps {
  onSelectVillage: (village: Village) => void;
  onOpenUpload: () => void;
  onBackToLanding: () => void;
}

export default function VillageCatalog({
  onSelectVillage,
  onOpenUpload,
  onBackToLanding,
}: VillageCatalogProps) {
  const [villages, setVillages] = useState<Village[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

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
      console.error('Error loading villages:', err);
      setError('Unable to load village registry from server.');
    } finally {
      setLoading(false);
    }
  };

  const filteredVillages = villages.filter((v) => {
    const q = searchQuery.toLowerCase();
    return (
      v.name.toLowerCase().includes(q) ||
      v.taluk?.toLowerCase().includes(q) ||
      v.district?.toLowerCase().includes(q) ||
      v.state?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="min-h-full flex flex-col bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/60 backdrop-blur-md px-8 py-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onBackToLanding}
              className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
              title="Back to Landing"
            >
              ←
            </button>
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center font-bold text-white text-lg">
              P
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-white">PlanGram</span>
                <span className="text-slate-500">/</span>
                <span className="text-sm text-slate-300 font-medium">Village & Project Catalog</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onOpenUpload}
              className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-sm font-medium transition-all flex items-center gap-2"
            >
              <span>📤</span>
              <span>Upload Village Data</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto px-8 py-10 w-full">
        {/* Title Bar & Search */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
              Select Dataset
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Select a Village to Plan
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Choose a representative village dataset to explore spatial layers and run infrastructure simulations.
            </p>
          </div>

          {/* Search Input */}
          <div className="w-full md:w-72">
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 text-sm">
                🔍
              </span>
              <input
                type="text"
                placeholder="Search villages, taluk..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 animate-pulse space-y-4"
              >
                <div className="h-6 bg-slate-700 rounded w-1/2"></div>
                <div className="h-4 bg-slate-700/60 rounded w-3/4"></div>
                <div className="h-20 bg-slate-700/30 rounded-xl"></div>
                <div className="h-10 bg-slate-700 rounded-xl"></div>
              </div>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 text-center max-w-md mx-auto my-12">
            <span className="text-3xl mb-2 block">⚠️</span>
            <h3 className="text-lg font-semibold text-red-400 mb-1">Failed to Load Villages</h3>
            <p className="text-sm text-slate-400 mb-4">{error}</p>
            <button
              onClick={loadVillages}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Villages Grid */}
        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVillages.map((village) => {
              return (
                <div
                  key={village.id}
                  className="bg-slate-800/50 hover:bg-slate-800/80 border border-slate-700/70 hover:border-blue-500/50 rounded-2xl p-6 transition-all duration-200 flex flex-col justify-between shadow-lg hover:shadow-xl hover:shadow-blue-500/5 group"
                >
                  <div>
                    {/* Header: Name & Status */}
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div>
                        <h2 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">
                          {village.name}
                        </h2>
                        <p className="text-xs text-slate-400 mt-0.5">
                          {village.taluk ? `${village.taluk}, ` : ''}
                          {village.district ? `${village.district}, ` : ''}
                          {village.state || ''}
                        </p>
                      </div>

                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
                          village.data_mode === 'prototype'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                            : village.data_mode === 'official'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
                            village.data_mode === 'prototype'
                              ? 'bg-amber-400'
                              : village.data_mode === 'official'
                              ? 'bg-emerald-400'
                              : 'bg-blue-400'
                          }`}
                        ></span>
                        {village.data_mode === 'prototype'
                          ? 'Prototype Data'
                          : village.data_mode === 'official'
                          ? 'Official Data'
                          : 'Imported Data'}
                      </span>
                    </div>

                    {/* Description */}
                    {village.description && (
                      <p className="text-xs text-slate-300 line-clamp-2 mt-3 mb-4 leading-relaxed">
                        {village.description}
                      </p>
                    )}

                    {/* Key Metrics Grid */}
                    <div className="grid grid-cols-3 gap-2 bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 mb-4 text-center">
                      <div>
                        <div className="text-slate-400 text-[10px] uppercase font-semibold">Population</div>
                        <div className="text-sm font-bold text-white mt-0.5">
                          ~{village.estimated_population?.toLocaleString() || 'N/A'}
                        </div>
                      </div>
                      <div className="border-x border-slate-800">
                        <div className="text-slate-400 text-[10px] uppercase font-semibold">Households</div>
                        <div className="text-sm font-bold text-white mt-0.5">
                          {village.estimated_households?.toLocaleString() || 'N/A'}
                        </div>
                      </div>
                      <div>
                        <div className="text-slate-400 text-[10px] uppercase font-semibold">Area</div>
                        <div className="text-sm font-bold text-white mt-0.5">
                          {village.area_sq_km} km²
                        </div>
                      </div>
                    </div>

                    {/* Priority Infrastructure Tags */}
                    {village.priority_infrastructure && village.priority_infrastructure.length > 0 && (
                      <div className="mb-4">
                        <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                          Planning Priorities
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {village.priority_infrastructure.map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-0.5 rounded-md bg-slate-700/60 text-slate-300 text-xs font-medium"
                            >
                              {tag === 'water' ? '💧 Water Access' :
                               tag === 'healthcare' ? '🏥 Healthcare' :
                               tag === 'waste' ? '♻️ Waste Mgmt' :
                               tag === 'education' ? '🎓 Education' : tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Open Planner Button */}
                  <button
                    onClick={() => onSelectVillage(village)}
                    className="w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm shadow-md shadow-blue-600/20 hover:shadow-blue-500/30 transition-all flex items-center justify-center gap-2 group/btn"
                  >
                    <span>Open Planner</span>
                    <span className="transform group-hover/btn:translate-x-1 transition-transform">→</span>
                  </button>
                </div>
              );
            })}

            {/* Empty Upload Prompt Card */}
            <div
              onClick={onOpenUpload}
              className="border-2 border-dashed border-slate-700 hover:border-blue-500/60 rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all hover:bg-slate-800/30 min-h-[300px] group"
            >
              <div className="w-14 h-14 rounded-2xl bg-slate-800 border border-slate-700 group-hover:border-blue-500/40 text-2xl flex items-center justify-center mb-3 group-hover:scale-105 transition-transform text-slate-300 group-hover:text-blue-400">
                +
              </div>
              <h3 className="text-base font-bold text-white mb-1">Import Another Village</h3>
              <p className="text-xs text-slate-400 max-w-xs mb-4">
                Support for GeoJSON, Shapefile, GeoPackage, KML, and tabular survey datasets.
              </p>
              <span className="text-xs font-semibold text-blue-400 group-hover:underline">
                Open Data Manager →
              </span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
