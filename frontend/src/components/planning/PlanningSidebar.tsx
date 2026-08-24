import type { Village, LayerVisibility } from '../../types/village';
import type { Candidate } from '../../types/optimization';

export type PlanningObjective =
  | 'water'
  | 'healthcare'
  | 'education'
  | 'sanitation'
  | 'waste'
  | 'connectivity';

interface PlanningSidebarProps {
  village: Village;
  activeObjective: PlanningObjective;
  onChangeObjective: (obj: PlanningObjective) => void;
  selectedInfrastructure: string;
  onChangeInfrastructure: (infra: string) => void;
  threshold: number;
  onChangeThreshold: (val: number) => void;
  layerVisibility: LayerVisibility;
  onToggleLayer: (layer: keyof LayerVisibility) => void;
  onFindBestLocations: () => void;
  isGeneratingCandidates: boolean;
  candidates: Candidate[];
  onSelectCandidate: (candidate: Candidate) => void;
  proposedLocation: [number, number] | null;
  onClearProposed: () => void;
  isPlacingProposed: boolean;
  onTogglePlacementMode: () => void;
}

const OBJECTIVES: Array<{
  id: PlanningObjective;
  label: string;
  icon: string;
  available: boolean;
  statusText?: string;
}> = [
  { id: 'water', label: 'Water Access', icon: '💧', available: true },
  { id: 'healthcare', label: 'Healthcare', icon: '🏥', available: false, statusText: 'Phase 2' },
  { id: 'education', label: 'Education', icon: '🎓', available: false, statusText: 'Phase 2' },
  { id: 'sanitation', label: 'Sanitation', icon: '🚽', available: false, statusText: 'Phase 2' },
  { id: 'waste', label: 'Waste Management', icon: '♻️', available: false, statusText: 'Phase 2' },
  { id: 'connectivity', label: 'Connectivity', icon: '🛣️', available: false, statusText: 'Phase 2' },
];

const LAYER_ITEMS: Array<{
  key: keyof LayerVisibility;
  label: string;
  color: string;
  icon: string;
  defaultOn?: boolean;
}> = [
  { key: 'boundary', label: 'Village Boundary', color: 'bg-blue-500', icon: '🗺️' },
  { key: 'buildings', label: 'Buildings', color: 'bg-slate-500', icon: '🏠' },
  { key: 'facilities', label: 'Existing Facilities', color: 'bg-emerald-500', icon: '🏢' },
  { key: 'coverage', label: 'Service Coverage Buffer', color: 'bg-emerald-400', icon: '🎯' },
  { key: 'underserved', label: 'Underserved Clusters', color: 'bg-amber-500', icon: '⚠️' },
  { key: 'candidates', label: 'Candidate Sites', color: 'bg-indigo-500', icon: '⭐' },
  { key: 'proposed', label: 'Proposed Facility', color: 'bg-blue-600', icon: '📍' },
  { key: 'parcels', label: 'Land Parcels', color: 'bg-gray-400', icon: '📐' },
  { key: 'water_bodies', label: 'Water Bodies', color: 'bg-cyan-500', icon: '💧' },
];

export default function PlanningSidebar({
  village,
  activeObjective,
  onChangeObjective,
  selectedInfrastructure,
  onChangeInfrastructure,
  threshold,
  onChangeThreshold,
  layerVisibility,
  onToggleLayer,
  onFindBestLocations,
  isGeneratingCandidates,
  candidates,
  onSelectCandidate,
  proposedLocation,
  onClearProposed,
  isPlacingProposed,
  onTogglePlacementMode,
}: PlanningSidebarProps) {
  return (
    <aside className="w-80 bg-slate-900 border-r border-slate-800 flex flex-col h-full overflow-y-auto text-slate-100 divide-y divide-slate-800">
      {/* 1. Current Village Card */}
      <div className="p-4 bg-slate-950/40">
        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center justify-between">
          <span>Planning Scope</span>
          <span className="text-emerald-400 font-semibold">● Active</span>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/70 rounded-xl p-3">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">{village.name}</h2>
              <p className="text-xs text-slate-400">
                {village.taluk}, {village.district}
              </p>
            </div>
            <span className="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
              {village.area_sq_km} km²
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-3 pt-2.5 border-t border-slate-700/60 text-center">
            <div className="bg-slate-900/60 p-1.5 rounded-lg">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Households</div>
              <div className="text-xs font-bold text-slate-200">
                {village.estimated_households?.toLocaleString() || '-'}
              </div>
            </div>
            <div className="bg-slate-900/60 p-1.5 rounded-lg">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Population</div>
              <div className="text-xs font-bold text-slate-200">
                ~{village.estimated_population?.toLocaleString() || '-'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Planning Objective Selector */}
      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Planning Objective
          </label>
          <span className="text-[10px] text-slate-400">Extensible</span>
        </div>

        <div className="grid grid-cols-1 gap-1.5">
          {OBJECTIVES.map((obj) => {
            const isSelected = activeObjective === obj.id;
            return (
              <button
                key={obj.id}
                onClick={() => obj.available && onChangeObjective(obj.id)}
                disabled={!obj.available}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                  isSelected
                    ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/25'
                    : obj.available
                    ? 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 border border-slate-700/50'
                    : 'bg-slate-900/40 text-slate-500 border border-slate-800/40 opacity-60 cursor-not-allowed'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>{obj.icon}</span>
                  <span>{obj.label}</span>
                </div>
                {obj.statusText && (
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {obj.statusText}
                  </span>
                )}
                {isSelected && (
                  <span className="text-xs">✓</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Infrastructure Type */}
        <div className="pt-2">
          <label className="text-[11px] font-semibold text-slate-400 mb-1.5 block">
            Target Infrastructure
          </label>
          <select
            value={selectedInfrastructure}
            onChange={(e) => onChangeInfrastructure(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="water_facility">Water Purification & Distribution Facility</option>
            <option value="borewell">Community Borewell & Storage Tank</option>
            <option value="water_kiosk">Smart Water ATM / Kiosk</option>
          </select>
        </div>
      </div>

      {/* 3. Interactive Simulation Controls */}
      <div className="p-4 space-y-3 bg-slate-950/20">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <span>⚡</span>
            <span>Simulation Engine</span>
          </label>
          <span className="text-[10px] text-blue-400 font-medium">What-If Mode</span>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2">
          <button
            onClick={onFindBestLocations}
            disabled={isGeneratingCandidates}
            className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center justify-center gap-2"
          >
            {isGeneratingCandidates ? (
              <>
                <span className="inline-block animate-spin">⟳</span>
                <span>Optimizing Gap Locations...</span>
              </>
            ) : (
              <>
                <span>⚡</span>
                <span>Find Best Locations</span>
              </>
            )}
          </button>

          <button
            onClick={onTogglePlacementMode}
            className={`w-full py-2 px-3 rounded-xl text-xs font-medium border transition-all flex items-center justify-center gap-2 ${
              isPlacingProposed
                ? 'bg-amber-500 text-slate-950 border-amber-400 font-bold animate-pulse'
                : 'bg-slate-800/80 hover:bg-slate-800 text-slate-200 border-slate-700'
            }`}
          >
            <span>📍</span>
            <span>{isPlacingProposed ? 'Click on Map to Place Facility' : 'Place Facility on Map'}</span>
          </button>

          {proposedLocation && (
            <button
              onClick={onClearProposed}
              className="w-full py-1.5 px-3 rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-300 text-[11px] font-medium transition-colors flex items-center justify-center gap-1.5"
            >
              <span>↺</span>
              <span>Reset Proposed Facility</span>
            </button>
          )}
        </div>

        {/* Candidate Locations List */}
        {candidates.length > 0 && (
          <div className="pt-2 border-t border-slate-800">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 mb-2">
              <span>Top Recommended Sites ({candidates.length})</span>
              <span className="text-[10px] text-indigo-400">Click to place</span>
            </div>
            <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
              {candidates.slice(0, 5).map((cand, idx) => (
                <button
                  key={idx}
                  onClick={() => onSelectCandidate(cand)}
                  className="w-full bg-slate-800/70 hover:bg-indigo-600/30 hover:border-indigo-500/60 border border-slate-700/60 rounded-lg p-2 text-left transition-all flex items-center justify-between group"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-indigo-500 text-white font-bold text-[10px] flex items-center justify-center">
                      #{cand.rank || idx + 1}
                    </span>
                    <div>
                      <div className="text-[11px] font-bold text-white group-hover:text-indigo-300">
                        Site #{cand.rank || idx + 1}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        +{cand.households_gained || Math.round((cand.coverage_improvement || 0.25) * 200)} households served
                      </div>
                    </div>
                  </div>
                  <span className="text-[10px] font-semibold text-emerald-400">
                    {cand.combined_score ? `${Math.round(cand.combined_score)}% fit` : '+26% cov'}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Threshold Slider */}
        <div className="pt-2 border-t border-slate-800">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-slate-400">Service Threshold:</span>
            <span className="font-bold text-blue-400 font-mono">{threshold}m</span>
          </div>
          <input
            type="range"
            min="100"
            max="1000"
            step="50"
            value={threshold}
            onChange={(e) => onChangeThreshold(Number(e.target.value))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>100m (Walking)</span>
            <span>500m (Standard)</span>
            <span>1000m (Max)</span>
          </div>
        </div>
      </div>

      {/* 4. Map Layers Toggles */}
      <div className="p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Map GIS Layers
          </label>
          <span className="text-[10px] text-slate-400">Toggle display</span>
        </div>

        <div className="space-y-1">
          {LAYER_ITEMS.map((item) => {
            const isVisible = !!layerVisibility[item.key];
            return (
              <button
                key={item.key}
                onClick={() => onToggleLayer(item.key)}
                className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-all ${
                  isVisible
                    ? 'bg-slate-800/80 text-white font-medium border border-slate-700/60'
                    : 'bg-slate-900/30 text-slate-400 opacity-60 hover:opacity-100'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${item.color}`} />
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </div>
                <div
                  className={`w-7 h-4 rounded-full transition-colors relative flex items-center px-0.5 ${
                    isVisible ? 'bg-blue-600' : 'bg-slate-700'
                  }`}
                >
                  <div
                    className={`w-3 h-3 rounded-full bg-white transition-transform ${
                      isVisible ? 'translate-x-3' : 'translate-x-0'
                    }`}
                  />
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
