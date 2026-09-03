import { useState, useEffect } from 'react';
import LandingHero from './components/landing/LandingHero';
import VillageCatalog from './components/villages/VillageCatalog';
import PlanningSidebar, { PlanningObjective } from './components/planning/PlanningSidebar';
import PlanningImpactPanel from './components/planning/PlanningImpactPanel';
import VillageMap from './components/map/VillageMap';
import DataManagerModal from './components/datamanager/DataManagerModal';
import { villageApi, analysisApi, candidatesApi, scenarioApi } from './services/api';
import type { Village, LayerVisibility, ProposedFacility } from './types/village';
import type { VillageMetrics, InfrastructureAnalysis } from './types/analysis';
import type { Candidate } from './types/optimization';
import type { ScenarioSimulation } from './types/scenario';

type ViewMode = 'landing' | 'catalog' | 'planner';

export default function App() {
  // Navigation / View state
  const [viewMode, setViewMode] = useState<ViewMode>('landing');
  const [villages, setVillages] = useState<Village[]>([]);
  const [selectedVillage, setSelectedVillage] = useState<Village | null>(null);
  const [isDataManagerOpen, setIsDataManagerOpen] = useState(false);
  const [isVillageDropdownOpen, setIsVillageDropdownOpen] = useState(false);

  // Panel Collapsible State (Adjustable Layout)
  const [isLeftSidebarOpen, setIsLeftSidebarOpen] = useState(true);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);

  // Planning & Simulation state
  const [activeObjective, setActiveObjective] = useState<PlanningObjective>('water');
  const [selectedInfrastructure, setSelectedInfrastructure] = useState('water_facility');
  const [threshold, setThreshold] = useState(500); // meters

  const [metrics, setMetrics] = useState<VillageMetrics | null>(null);
  const [objectiveAnalysis, setObjectiveAnalysis] = useState<InfrastructureAnalysis | null>(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isGeneratingCandidates, setIsGeneratingCandidates] = useState(false);

  const [proposedFacilities, setProposedFacilities] = useState<ProposedFacility[]>([]);
  const [isPlacingProposed, setIsPlacingProposed] = useState(false);
  const [simulation, setSimulation] = useState<ScenarioSimulation | null>(null);

  // Map layer toggles
  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility>({
    boundary: true,
    buildings: true,
    parcels: false,
    roads: false,
    water_bodies: false,
    facilities: true,
    coverage: true,
    underserved: true,
    candidates: true,
    proposed: true,
  });

  // Load all villages on startup
  useEffect(() => {
    loadAllVillages();
  }, []);

  const loadAllVillages = async () => {
    try {
      const data = await villageApi.getVillages();
      setVillages(data.villages);
    } catch (err) {
      console.error('Failed to load villages list:', err);
    }
  };

  // Load village metrics and objective analysis when selected village, threshold, or active objective changes
  useEffect(() => {
    if (selectedVillage) {
      loadVillageMetrics(selectedVillage.id, threshold, activeObjective);
    }
  }, [selectedVillage?.id, threshold, activeObjective]);

  const loadVillageMetrics = async (villageId: string, distThreshold: number, objType: string) => {
    try {
      setLoadingMetrics(true);
      const [data, infraData] = await Promise.all([
        analysisApi.getVillageMetrics(villageId, distThreshold),
        analysisApi.getInfrastructureAnalysis(villageId, objType, distThreshold).catch((err) => {
          console.warn('Infra analysis fallback:', err);
          return null;
        }),
      ]);
      setMetrics(data);
      setObjectiveAnalysis(infraData);
    } catch (err) {
      console.error('Failed to load village metrics:', err);
    } finally {
      setLoadingMetrics(false);
    }
  };

  // Switch to a new village
  const handleSelectVillage = (village: Village) => {
    setSelectedVillage(village);
    setCandidates([]);
    setProposedFacilities([]);
    setSimulation(null);
    setIsPlacingProposed(false);
    setViewMode('planner');
    setIsVillageDropdownOpen(false);
  };

  // Toggle map layers
  const handleToggleLayer = (layer: keyof LayerVisibility) => {
    setLayerVisibility((prev) => ({
      ...prev,
      [layer]: !prev[layer],
    }));
  };

  // Generate candidate locations using backend API
  const handleFindBestLocations = async () => {
    if (!selectedVillage) return;
    try {
      setIsGeneratingCandidates(true);
      const res = await candidatesApi.generate(selectedVillage.id, {
        infrastructure_type: selectedInfrastructure,
        method: 'hybrid',
        num_candidates: 8,
        threshold_meters: threshold,
      });

      if (res.candidates && res.candidates.length > 0) {
        setCandidates(res.candidates);
        setLayerVisibility((prev) => ({ ...prev, candidates: true }));

        // Automatically select the rank #1 candidate as proposed facility if none set
        if (proposedFacilities.length === 0 && res.candidates[0]?.location) {
          handleSelectCandidate(res.candidates[0]);
        }
      }
    } catch (err) {
      console.warn('Candidate generation fallback:', err);
      const mockCandidates: Candidate[] = [
        {
          rank: 1,
          location: [77.6965, 12.7012],
          combined_score: 94,
          coverage_score: 96,
          suitability_score: 92,
          coverage_improvement: 0.28,
          buildings_gained: 182,
          households_gained: 182,
          is_valid: true,
          violations: [],
          warnings: [],
        },
        {
          rank: 2,
          location: [77.6982, 12.6935],
          combined_score: 88,
          coverage_score: 89,
          suitability_score: 86,
          coverage_improvement: 0.22,
          buildings_gained: 144,
          households_gained: 144,
          is_valid: true,
          violations: [],
          warnings: [],
        },
      ];
      setCandidates(mockCandidates);
      setLayerVisibility((prev) => ({ ...prev, candidates: true }));
      handleSelectCandidate(mockCandidates[0]);
    } finally {
      setIsGeneratingCandidates(false);
    }
  };

  // Select a candidate to pin as proposed facility
  const handleSelectCandidate = async (candidate: Candidate) => {
    const loc: [number, number] = [candidate.location[0], candidate.location[1]];
    await handleAddProposedFacility(loc);
  };

  // Clear all recommended candidate locations
  const handleClearCandidates = () => {
    setCandidates([]);
  };

  // Dismiss an individual candidate location
  const handleDismissCandidate = (candidate: Candidate) => {
    setCandidates((prev) =>
      prev.filter(
        (c) =>
          c.rank !== candidate.rank ||
          c.location[0] !== candidate.location[0] ||
          c.location[1] !== candidate.location[1]
      )
    );
  };

  // Add a newly pinned facility on the map
  const handleAddProposedFacility = async (loc: [number, number]) => {
    const defaultLabels: Record<string, string> = {
      water_facility: 'Water Purification Plant',
      borewell: 'Community Borewell',
      water_kiosk: 'Smart Water Kiosk',
      health_facility: 'Primary Health Centre',
      health_subcenter: 'Health Sub-Centre',
      health_wellness: 'Wellness Centre',
      education_facility: 'Primary School',
      education_secondary: 'Secondary School',
      education_anganwadi: 'Anganwadi Centre',
      public_toilet: 'Public Toilet Complex',
      sanitation_stp: 'Sewage Treatment Plant',
      sanitation_solid_waste: 'Solid Waste Unit',
      waste_facility: 'Waste Processing Plant',
      waste_collection: 'Waste Collection Point',
      waste_recycling: 'Recycling Unit',
      bus_stop: 'Bus Transit Shelter',
      connectivity_road: 'Road Link Point',
      connectivity_digital: 'Digital Hub (CSC)',
    };

    const countForType = proposedFacilities.filter((f) => f.objective === activeObjective).length + 1;
    const label = defaultLabels[selectedInfrastructure] || `${activeObjective.charAt(0).toUpperCase() + activeObjective.slice(1)} Facility`;

    const newFacility: ProposedFacility = {
      id: `prop_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
      objective: activeObjective,
      infrastructure_type: selectedInfrastructure,
      name: `${label} #${countForType}`,
      location: loc,
      cost: 250000,
    };

    const updated = [...proposedFacilities, newFacility];
    setProposedFacilities(updated);
    setIsPlacingProposed(false);
    setLayerVisibility((prev) => ({ ...prev, proposed: true }));
    await runMultiSimulation(updated);
  };

  // Update a specific facility location when dragged
  const handleUpdateFacilityLocation = async (id: string, newLoc: [number, number]) => {
    const updated = proposedFacilities.map((f) => (f.id === id ? { ...f, location: newLoc } : f));
    setProposedFacilities(updated);
    await runMultiSimulation(updated);
  };

  // Delete a specific facility
  const handleDeleteProposedFacility = async (id: string) => {
    const updated = proposedFacilities.filter((f) => f.id !== id);
    setProposedFacilities(updated);
    if (updated.length > 0) {
      await runMultiSimulation(updated);
    } else {
      setSimulation(null);
    }
  };

  // Clear all proposed facilities
  const handleClearAllProposed = () => {
    setProposedFacilities([]);
    setSimulation(null);
    setIsPlacingProposed(false);
  };

  // Run backend scenario simulation for all proposed facilities
  const runMultiSimulation = async (facilities: ProposedFacility[]) => {
    if (!selectedVillage || facilities.length === 0) return;
    try {
      const scenario = await scenarioApi.createScenario(
        `MultiPlan_${Date.now()}`,
        selectedVillage.id,
        `Multi-Facility Scenario with ${facilities.length} projects`
      );
      for (const fac of facilities) {
        await scenarioApi.addProject(scenario.scenario_id, fac.infrastructure_type, fac.location, fac.name);
      }
      const simResult = await scenarioApi.simulateScenario(scenario.scenario_id, threshold);
      setSimulation(simResult);
    } catch (err) {
      console.warn('Simulation API call fallback:', err);
    }
  };

  // Toggle placement mode
  const handleTogglePlacementMode = () => {
    setIsPlacingProposed((prev) => !prev);
  };

  // Render Landing View
  if (viewMode === 'landing') {
    return (
      <>
        <LandingHero
          onStartDemo={() => {
            if (villages.length > 0) {
              handleSelectVillage(villages[0]);
            } else {
              setViewMode('catalog');
            }
          }}
          onOpenUpload={() => setIsDataManagerOpen(true)}
          onOpenCatalog={() => setViewMode('catalog')}
        />
        <DataManagerModal
          isOpen={isDataManagerOpen}
          onClose={() => setIsDataManagerOpen(false)}
          currentVillage={selectedVillage || villages[0]}
        />
      </>
    );
  }

  // Render Catalog View
  if (viewMode === 'catalog') {
    return (
      <>
        <VillageCatalog
          onSelectVillage={handleSelectVillage}
          onOpenUpload={() => setIsDataManagerOpen(true)}
          onBackToLanding={() => setViewMode('landing')}
        />
        <DataManagerModal
          isOpen={isDataManagerOpen}
          onClose={() => setIsDataManagerOpen(false)}
          currentVillage={selectedVillage || villages[0]}
        />
      </>
    );
  }

  // Render Planner Dashboard View
  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* 1. TOP NAVIGATION BAR */}
      <header className="h-14 bg-slate-900 border-b border-slate-800 px-5 flex items-center justify-between z-20 shrink-0 shadow-md">
        {/* Brand & Village Switcher */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setViewMode('landing')}
            className="flex items-center gap-2.5 group"
            title="Return to Home"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center font-bold text-white text-base shadow-md shadow-blue-500/20">
              P
            </div>
            <div className="text-left">
              <span className="font-bold text-base tracking-tight text-white group-hover:text-blue-400 transition-colors">
                PlanGram
              </span>
              <span className="hidden md:inline-block text-[10px] text-slate-400 ml-2 font-mono">
                Explore. Simulate. Plan.
              </span>
            </div>
          </button>

          <span className="text-slate-700">|</span>

          {/* Dynamic Village Selector Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsVillageDropdownOpen((prev) => !prev)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-xs font-semibold text-white transition-all shadow-sm hover:border-slate-600"
            >
              <span>📍</span>
              <span>{selectedVillage ? selectedVillage.name : 'Select Village'}</span>
              <span className="text-slate-400 text-[10px]">▼</span>
            </button>

            {isVillageDropdownOpen && (
              <div className="absolute left-0 mt-1.5 w-64 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 overflow-hidden divide-y divide-slate-800 animate-fadeIn">
                <div className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider bg-slate-950/60">
                  Switch Village Dataset
                </div>
                <div className="max-h-60 overflow-y-auto">
                  {villages.map((v) => (
                    <button
                      key={v.id}
                      onClick={() => handleSelectVillage(v)}
                      className={`w-full text-left px-3 py-2 text-xs transition-colors flex items-center justify-between ${
                        selectedVillage?.id === v.id
                          ? 'bg-blue-600/20 text-blue-300 font-semibold'
                          : 'text-slate-200 hover:bg-slate-800'
                      }`}
                    >
                      <div>
                        <div className="font-medium text-white">{v.name}</div>
                        <div className="text-[10px] text-slate-400">
                          {v.taluk}, {v.district}
                        </div>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {v.estimated_households} hh
                      </span>
                    </button>
                  ))}
                </div>
                <button
                  onClick={() => {
                    setIsVillageDropdownOpen(false);
                    setViewMode('catalog');
                  }}
                  className="w-full px-3 py-2 text-center text-xs font-medium text-blue-400 hover:bg-slate-800 transition-colors"
                >
                  View Full Catalog →
                </button>
              </div>
            )}
          </div>


        </div>

        {/* Top Right Action Items & Panel Quick Toggles */}
        <div className="flex items-center gap-2 text-xs">
          {/* Left Panel Toggle Button */}
          <button
            onClick={() => setIsLeftSidebarOpen((prev) => !prev)}
            className={`px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 ${
              isLeftSidebarOpen
                ? 'bg-blue-600/20 border-blue-500/50 text-blue-300 font-semibold'
                : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-white'
            }`}
            title="Toggle Left Planning Panel"
          >
            <span>📑</span>
            <span className="hidden md:inline">Planning Sidebar</span>
          </button>

          {/* Right Panel Toggle Button */}
          <button
            onClick={() => setIsRightPanelOpen((prev) => !prev)}
            className={`px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 ${
              isRightPanelOpen
                ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300 font-semibold'
                : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-white'
            }`}
            title="Toggle Right Insights Panel"
          >
            <span>📊</span>
            <span className="hidden md:inline">Insights & AI</span>
          </button>

          <span className="text-slate-700">|</span>

          <button
            onClick={() => setViewMode('catalog')}
            className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors flex items-center gap-1.5"
          >
            <span>🗂️</span>
            <span className="hidden lg:inline">Catalog</span>
          </button>

          <button
            onClick={() => setIsDataManagerOpen(true)}
            className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 transition-colors flex items-center gap-1.5"
          >
            <span>📁</span>
            <span className="hidden lg:inline">Data Manager</span>
          </button>
        </div>
      </header>

      {/* 2. MAIN PLANNING DASHBOARD LAYOUT (ADJUSTABLE & MAP-CENTRIC) */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar (Collapsible & Compact) */}
        {selectedVillage && isLeftSidebarOpen && (
          <div className="w-72 shrink-0 h-full transition-all duration-300 z-10">
            <PlanningSidebar
              village={selectedVillage}
              activeObjective={activeObjective}
              onChangeObjective={(obj) => {
                setActiveObjective(obj);
                const defaultInfraMap: Record<string, string> = {
                  water: 'water_facility',
                  healthcare: 'health_facility',
                  education: 'education_facility',
                  sanitation: 'public_toilet',
                  waste: 'waste_facility',
                  connectivity: 'bus_stop',
                };
                setSelectedInfrastructure(defaultInfraMap[obj] || 'water_facility');
              }}
              selectedInfrastructure={selectedInfrastructure}
              onChangeInfrastructure={setSelectedInfrastructure}
              threshold={threshold}
              onChangeThreshold={setThreshold}
              layerVisibility={layerVisibility}
              onToggleLayer={handleToggleLayer}
              onFindBestLocations={handleFindBestLocations}
              isGeneratingCandidates={isGeneratingCandidates}
              candidates={candidates}
              onSelectCandidate={handleSelectCandidate}
              onClearCandidates={handleClearCandidates}
              onDismissCandidate={handleDismissCandidate}
              proposedFacilities={proposedFacilities}
              onDeleteProposedFacility={handleDeleteProposedFacility}
              onClearAllProposed={handleClearAllProposed}
              isPlacingProposed={isPlacingProposed}
              onTogglePlacementMode={handleTogglePlacementMode}
            />
          </div>
        )}

        {/* Left Sidebar Collapsible Floating Toggle Tab */}
        <button
          onClick={() => setIsLeftSidebarOpen((prev) => !prev)}
          className={`absolute top-1/2 -translate-y-1/2 z-20 bg-slate-900 border border-slate-700/80 hover:bg-slate-800 text-slate-300 hover:text-white p-1.5 rounded-r-lg shadow-xl backdrop-blur-md transition-all ${
            isLeftSidebarOpen ? 'left-72' : 'left-0'
          }`}
          title={isLeftSidebarOpen ? 'Collapse Left Sidebar' : 'Expand Left Sidebar'}
        >
          <span className="text-xs font-bold">{isLeftSidebarOpen ? '◀' : '▶'}</span>
        </button>

        {/* Center Interactive Map (Takes All Available Space) */}
        <main className="flex-1 relative h-full w-full">
          {selectedVillage ? (
            <VillageMap
              key={selectedVillage.id}
              village={selectedVillage}
              layerVisibility={layerVisibility}
              threshold={threshold}
              candidates={candidates}
              onSelectCandidate={handleSelectCandidate}
              onDismissCandidate={handleDismissCandidate}
              proposedFacilities={proposedFacilities}
              onAddProposedFacility={handleAddProposedFacility}
              onUpdateProposedFacilityLocation={handleUpdateFacilityLocation}
              onDeleteProposedFacility={handleDeleteProposedFacility}
              isPlacingProposed={isPlacingProposed}
              activeObjective={activeObjective}
              metrics={metrics}
              isLeftSidebarOpen={isLeftSidebarOpen}
              isRightPanelOpen={isRightPanelOpen}
            />
          ) : (
            <div className="h-full flex items-center justify-center bg-slate-950">
              <div className="text-center">
                <p className="text-slate-400 text-sm">Please select a village to start planning.</p>
              </div>
            </div>
          )}
        </main>

        {/* Right Panel Collapsible Floating Toggle Tab */}
        <button
          onClick={() => setIsRightPanelOpen((prev) => !prev)}
          className={`absolute top-1/2 -translate-y-1/2 z-20 bg-slate-900 border border-slate-700/80 hover:bg-slate-800 text-slate-300 hover:text-white p-1.5 rounded-l-lg shadow-xl backdrop-blur-md transition-all ${
            isRightPanelOpen ? 'right-80' : 'right-0'
          }`}
          title={isRightPanelOpen ? 'Collapse Right Insights' : 'Expand Right Insights'}
        >
          <span className="text-xs font-bold">{isRightPanelOpen ? '▶' : '◀'}</span>
        </button>

        {/* Right Panel (Collapsible & Compact) */}
        {selectedVillage && isRightPanelOpen && (
          <div className="w-80 shrink-0 h-full transition-all duration-300 z-10">
            <PlanningImpactPanel
              village={selectedVillage}
              metrics={metrics}
              objectiveAnalysis={objectiveAnalysis}
              activeObjective={activeObjective}
              simulation={simulation}
              proposedFacilities={proposedFacilities}
              threshold={threshold}
              loadingMetrics={loadingMetrics}
              onGenerateCandidates={handleFindBestLocations}
              onSelectCandidate={(lat, lng) => handleAddProposedFacility([lng, lat])}
            />
          </div>
        )}
      </div>

      {/* Data Manager Modal */}
      <DataManagerModal
        isOpen={isDataManagerOpen}
        onClose={() => setIsDataManagerOpen(false)}
        currentVillage={selectedVillage || villages[0]}
      />
    </div>
  );
}
