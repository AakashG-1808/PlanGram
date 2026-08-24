import type { LayerVisibility } from '../../types/village';

interface LayerControlsProps {
  layerVisibility: LayerVisibility;
  onToggleLayer: (layer: keyof LayerVisibility) => void;
}

const LAYER_CONFIG = {
  boundary: { label: 'Village Boundary', color: 'bg-blue-500', icon: '🗺️' },
  buildings: { label: 'Buildings', color: 'bg-slate-400', icon: '🏠' },
  facilities: { label: 'Facilities', color: 'bg-emerald-500', icon: '🏢' },
  coverage: { label: 'Service Coverage', color: 'bg-emerald-400', icon: '🎯' },
  underserved: { label: 'Underserved Clusters', color: 'bg-amber-500', icon: '⚠️' },
  candidates: { label: 'Candidate Sites', color: 'bg-indigo-500', icon: '⭐' },
  proposed: { label: 'Proposed Facility', color: 'bg-blue-600', icon: '📍' },
  parcels: { label: 'Parcels', color: 'bg-gray-400', icon: '📐' },
  water_bodies: { label: 'Water Bodies', color: 'bg-cyan-400', icon: '💧' },
};

export default function LayerControls({ layerVisibility, onToggleLayer }: LayerControlsProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-lg">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold text-xs text-white uppercase tracking-wider">Map Layers</h3>
        <span className="text-[10px] text-slate-400">Toggle</span>
      </div>

      <div className="space-y-1.5">
        {Object.entries(LAYER_CONFIG).map(([key, config]) => {
          const layerKey = key as keyof LayerVisibility;
          const isVisible = !!layerVisibility[layerKey];

          return (
            <button
              key={key}
              onClick={() => onToggleLayer(layerKey)}
              className={`w-full flex items-center justify-between p-2 rounded-lg text-xs transition-all ${
                isVisible
                  ? 'bg-slate-800 text-white font-medium border border-slate-700/60'
                  : 'bg-slate-900/40 text-slate-400 opacity-60 hover:opacity-100'
              }`}
            >
              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${config.color}`}></div>
                <span>{config.icon}</span>
                <span>{config.label}</span>
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
                ></div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
