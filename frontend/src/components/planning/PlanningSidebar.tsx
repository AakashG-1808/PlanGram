import type { Village, LayerVisibility, ProposedFacility } from '../../types/village';
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
  onClearCandidates?: () => void;
  onDismissCandidate?: (candidate: Candidate) => void;
  proposedFacilities: ProposedFacility[];
  onDeleteProposedFacility: (id: string) => void;
  onClearAllProposed: () => void;
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
  { id: 'healthcare', label: 'Healthcare', icon: '🏥', available: true },
  { id: 'education', label: 'Education', icon: '🎓', available: true },
  { id: 'sanitation', label: 'Sanitation', icon: '🚽', available: true },
  { id: 'waste', label: 'Waste Management', icon: '♻️', available: true },
  { id: 'connectivity', label: 'Connectivity', icon: '🛣️', available: true },
];

/** Infrastructure type options mapped to each planning objective */
const INFRASTRUCTURE_OPTIONS: Record<PlanningObjective, Array<{ value: string; label: string }>> = {
  water: [
    { value: 'water_facility', label: 'Water Purification & Distribution Facility' },
    { value: 'borewell', label: 'Community Borewell & Storage Tank' },
    { value: 'water_kiosk', label: 'Smart Water ATM / Kiosk' },
  ],
  healthcare: [
    { value: 'health_facility', label: 'Primary Health Centre (PHC)' },
    { value: 'health_subcenter', label: 'Health Sub-Centre' },
    { value: 'health_wellness', label: 'Ayushman Health & Wellness Centre' },
  ],
  education: [
    { value: 'education_facility', label: 'Primary School' },
    { value: 'education_secondary', label: 'Secondary School' },
    { value: 'education_anganwadi', label: 'Anganwadi Centre' },
  ],
  sanitation: [
    { value: 'public_toilet', label: 'Community / Public Toilet Complex' },
    { value: 'sanitation_stp', label: 'Sewage Treatment Plant' },
    { value: 'sanitation_solid_waste', label: 'Solid Waste Collection Point' },
  ],
  waste: [
    { value: 'waste_facility', label: 'Waste Processing Facility' },
    { value: 'waste_collection', label: 'Waste Collection Centre' },
    { value: 'waste_recycling', label: 'Recycling & Segregation Unit' },
  ],
  connectivity: [
    { value: 'bus_stop', label: 'Bus Stop / Transit Shelter' },
    { value: 'connectivity_road', label: 'Road Connectivity Point' },
    { value: 'connectivity_digital', label: 'Digital Connectivity Hub (CSC)' },
  ],
};

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
  onClearCandidates,
  onDismissCandidate,
  proposedFacilities,
  onDeleteProposedFacility,
  onClearAllProposed,
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
            {INFRASTRUCTURE_OPTIONS[activeObjective].map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
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
          <div className="flex items-center gap-1.5">
            <button
              onClick={onFindBestLocations}
              disabled={isGeneratingCandidates}
              className="flex-1 py-2.5 px-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center justify-center gap-2"
            >
              {isGeneratingCandidates ? (
                <>
                  <span className="inline-block animate-spin">⟳</span>
                  <span>Optimizing Gap Locations...</span>
                </>
              ) : (
                <>
                  <span>⚡</span>
                  <span>{candidates.length > 0 ? 'Find Best Locations' : 'Find Best Locations'}</span>
                </>
              )}
            </button>
            {candidates.length > 0 && onClearCandidates && (
              <button
                onClick={onClearCandidates}
                className="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-red-500/20 text-slate-300 hover:text-red-400 border border-slate-700 hover:border-red-500/40 text-xs font-semibold transition-all flex items-center justify-center gap-1 shrink-0"
                title="Remove best recommended locations"
              >
                <span>✕</span>
                <span className="text-[11px]">Clear</span>
              </button>
            )}
          </div>

          <button
            onClick={onTogglePlacementMode}
            className={`w-full py-2 px-3 rounded-xl text-xs font-medium border transition-all flex items-center justify-center gap-2 ${
              isPlacingProposed
                ? 'bg-amber-500 text-slate-950 border-amber-400 font-bold animate-pulse'
                : 'bg-slate-800/80 hover:bg-slate-800 text-slate-200 border-slate-700'
            }`}
          >
            <span>📍</span>
            <span>
              {isPlacingProposed
                ? `Click Map to Pin ${OBJECTIVES.find(o => o.id === activeObjective)?.label || 'Facility'}`
                : `+ Pin ${OBJECTIVES.find(o => o.id === activeObjective)?.label || 'Facility'} on Map`}
            </span>
          </button>
        </div>

        {/* Pinned Proposed Facilities List */}
        {proposedFacilities.length > 0 && (
          <div className="pt-2 border-t border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-300">
              <span className="flex items-center gap-1.5">
                <span>📌</span>
                <span>Pinned Facilities ({proposedFacilities.length})</span>
              </span>
              <button
                onClick={onClearAllProposed}
                className="text-[10px] text-red-400 hover:text-red-300 hover:underline"
              >
                Clear All
              </button>
            </div>

            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {proposedFacilities.map((fac, idx) => {
                const objMeta = OBJECTIVES.find((o) => o.id === fac.objective);
                return (
                  <div
                    key={fac.id || idx}
                    className="w-full bg-slate-800/80 border border-slate-700/80 rounded-lg p-2 flex items-center justify-between gap-2 hover:border-blue-500/50 transition-colors"
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-sm shrink-0">{objMeta?.icon || '📍'}</span>
                      <div className="min-w-0">
                        <div className="text-xs font-bold text-white truncate">
                          {fac.name}
                        </div>
                        <div className="text-[10px] text-slate-400">
                          {fac.location[1].toFixed(4)}, {fac.location[0].toFixed(4)}
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => onDeleteProposedFacility(fac.id)}
                      className="px-2 py-1 rounded-md bg-red-500/10 hover:bg-red-500 text-red-300 hover:text-white border border-red-500/20 hover:border-red-500 text-xs font-semibold transition-all shrink-0 flex items-center gap-1"
                      title="Delete this facility"
                    >
                      <span>🗑️</span>
                      <span className="text-[10px]">Delete</span>
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Candidate Locations List */}
        {candidates.length > 0 && (
          <div className="pt-2 border-t border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-300">
              <span className="flex items-center gap-1.5 font-bold text-white">
                <span>⚡</span>
                <span>Top Recommended Sites ({candidates.length})</span>
              </span>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-indigo-400 hidden sm:inline">Click to place</span>
                {onClearCandidates && (
                  <button
                    onClick={onClearCandidates}
                    className="px-2 py-0.5 rounded-md bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 border border-red-500/20 text-[10px] font-semibold transition-all flex items-center gap-1"
                    title="Remove all recommended sites from map"
                  >
                    <span>✕</span>
                    <span>Remove All</span>
                  </button>
                )}
              </div>
            </div>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {candidates.map((cand, idx) => (
                <div
                  key={cand.rank || idx}
                  onClick={() => onSelectCandidate(cand)}
                  className="w-full bg-slate-800/70 hover:bg-indigo-600/30 hover:border-indigo-500/60 border border-slate-700/60 rounded-lg p-2 text-left transition-all flex items-center justify-between group cursor-pointer"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="w-5 h-5 rounded-full bg-indigo-500 text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                      #{cand.rank || idx + 1}
                    </span>
                    <div className="min-w-0">
                      <div className="text-[11px] font-bold text-white group-hover:text-indigo-300 truncate">
                        Site #{cand.rank || idx + 1}
                      </div>
                      <div className="text-[10px] text-slate-400 truncate">
                        +{cand.households_gained || Math.round((cand.coverage_improvement || 0.25) * 200)} households served
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0 ml-1">
                    <span className="text-[10px] font-semibold text-emerald-400">
                      {cand.combined_score ? `${Math.round(cand.combined_score)}% fit` : '+26% cov'}
                    </span>
                    {onDismissCandidate && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDismissCandidate(cand);
                        }}
                        className="p-1 rounded hover:bg-red-500/20 text-slate-400 hover:text-red-400 text-xs transition-colors"
                        title={`Remove Site #${cand.rank || idx + 1}`}
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
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
