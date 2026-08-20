import { useState } from 'react';
import VillageSelector from './components/villages/VillageSelector';
import VillageInfo from './components/villages/VillageInfo';
import VillageMap from './components/map/VillageMap';
import LayerControls from './components/map/LayerControls';
import VillageMetricsPanel from './components/insights/VillageMetricsPanel';
import type { Village, LayerVisibility } from './types/village';

function App() {
  const [selectedVillage, setSelectedVillage] = useState<Village | null>(null);
  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility>({
    boundary: true,
    buildings: true,
    parcels: false,
    roads: true,
    water_bodies: true,
    facilities: true,
  });
  const [threshold, setThreshold] = useState(500); // Distance threshold in meters

  const handleToggleLayer = (layer: keyof LayerVisibility) => {
    setLayerVisibility((prev) => ({
      ...prev,
      [layer]: !prev[layer],
    }));
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">PlanGram</h1>
              <p className="text-sm text-gray-600 mt-1">
                Explore. Simulate. Plan.
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                Phase 3: Spatial Analysis
              </span>
              {selectedVillage && (
                <span className="text-sm text-gray-600">
                  📍 {selectedVillage.name}
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-80 bg-white border-r overflow-y-auto">
          <div className="p-4 space-y-4">
            {/* Village Selector */}
            <VillageSelector
              onVillageSelect={setSelectedVillage}
              selectedVillageId={selectedVillage?.id}
            />

            {/* Village Info */}
            {selectedVillage && (
              <VillageInfo village={selectedVillage} />
            )}

            {/* Threshold Control */}
            {selectedVillage && (
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="font-semibold text-gray-900 mb-3">
                  Analysis Settings
                </h3>
                <div>
                  <label className="block text-sm text-gray-700 mb-2">
                    Service Threshold: {threshold}m
                  </label>
                  <input
                    type="range"
                    min="100"
                    max="1000"
                    step="50"
                    value={threshold}
                    onChange={(e) => setThreshold(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-600 mt-1">
                    <span>100m</span>
                    <span>1000m</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-2">
                    Households within this distance are considered "served"
                  </p>
                </div>
              </div>
            )}

            {/* Village Metrics */}
            {selectedVillage && (
              <VillageMetricsPanel
                village={selectedVillage}
                threshold={threshold}
              />
            )}

            {/* Layer Controls */}
            {selectedVillage && (
              <LayerControls
                layerVisibility={layerVisibility}
                onToggleLayer={handleToggleLayer}
              />
            )}
          </div>
        </aside>

        {/* Map Area */}
        <main className="flex-1 relative">
          {selectedVillage ? (
            <VillageMap
              village={selectedVillage}
              layerVisibility={layerVisibility}
            />
          ) : (
            <div className="h-full flex items-center justify-center bg-gray-100">
              <div className="text-center max-w-md">
                <div className="text-6xl mb-4">📊</div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Select a Village
                </h2>
                <p className="text-gray-600">
                  Choose a village from the sidebar to view spatial analysis,
                  coverage metrics, and infrastructure insights.
                </p>
                <div className="mt-6 space-y-2 text-sm text-gray-600">
                  <div className="flex items-center justify-center gap-2">
                    <span>📈</span>
                    <span>Coverage analysis • Distance metrics</span>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <span>🎯</span>
                    <span>Underserved area identification</span>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <span>💡</span>
                    <span>Priority recommendations</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t px-6 py-3">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <div className="flex items-center gap-4">
            <span>© 2026 PlanGram</span>
            <span className="text-gray-400">|</span>
            <span>Anekal Taluk, Karnataka</span>
            {selectedVillage && threshold && (
              <>
                <span className="text-gray-400">|</span>
                <span>Threshold: {threshold}m</span>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-amber-600">⚠️</span>
            <span>Decision-support prototype with synthetic data</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
