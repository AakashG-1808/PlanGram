import type { LayerVisibility } from '../../types/village';

interface LayerControlsProps {
  layerVisibility: LayerVisibility;
  onToggleLayer: (layer: keyof LayerVisibility) => void;
}

const LAYER_CONFIG = {
  boundary: { label: 'Village Boundary', color: 'bg-blue-500', icon: '🗺️' },
  buildings: { label: 'Buildings', color: 'bg-red-500', icon: '🏠' },
  parcels: { label: 'Parcels', color: 'bg-gray-400', icon: '📐' },
  roads: { label: 'Roads', color: 'bg-amber-500', icon: '🛣️' },
  water_bodies: { label: 'Water Bodies', color: 'bg-blue-400', icon: '💧' },
  facilities: { label: 'Facilities', color: 'bg-green-500', icon: '🏢' },
};

export default function LayerControls({ layerVisibility, onToggleLayer }: LayerControlsProps) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-gray-900">Map Layers</h3>
        <p className="text-sm text-gray-600 mt-1">Toggle visibility</p>
      </div>

      <div className="p-4 space-y-2">
        {Object.entries(LAYER_CONFIG).map(([key, config]) => {
          const layerKey = key as keyof LayerVisibility;
          const isVisible = layerVisibility[layerKey];

          return (
            <button
              key={key}
              onClick={() => onToggleLayer(layerKey)}
              className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                isVisible
                  ? 'border-gray-300 bg-white'
                  : 'border-gray-200 bg-gray-50 opacity-60'
              }`}
            >
              <div className={`w-4 h-4 rounded ${config.color}`}></div>
              
              <div className="flex-1 text-left">
                <div className="flex items-center gap-2">
                  <span>{config.icon}</span>
                  <span className="text-sm font-medium text-gray-900">
                    {config.label}
                  </span>
                </div>
              </div>

              <div className="relative inline-flex items-center">
                <div
                  className={`w-11 h-6 rounded-full transition-colors ${
                    isVisible ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <div
                    className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${
                      isVisible ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  ></div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="p-4 border-t bg-gray-50 rounded-b-lg">
        <div className="text-xs text-gray-600 space-y-1">
          <p className="flex items-center gap-1">
            <span>💡</span>
            <span>Click layers to toggle visibility</span>
          </p>
          <p className="flex items-center gap-1">
            <span>🖱️</span>
            <span>Use mouse to pan and zoom map</span>
          </p>
        </div>
      </div>
    </div>
  );
}
