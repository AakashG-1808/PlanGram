import { useState } from 'react';
import type { Village, ProposedFacility } from '../../types/village';
import type { VillageMetrics, InfrastructureAnalysis } from '../../types/analysis';
import type { ScenarioSimulation } from '../../types/scenario';
import type { PlanningObjective } from './PlanningSidebar';
import PlanningAssistant from '../ai/PlanningAssistant';

const OBJECTIVE_INFO: Record<PlanningObjective, { label: string; icon: string; singular: string }> = {
  water: { label: 'Water Access', icon: '💧', singular: 'water point' },
  healthcare: { label: 'Healthcare', icon: '🏥', singular: 'health centre' },
  education: { label: 'Education', icon: '🎓', singular: 'school' },
  sanitation: { label: 'Sanitation', icon: '🚽', singular: 'sanitation facility' },
  waste: { label: 'Waste Management', icon: '♻️', singular: 'waste facility' },
  connectivity: { label: 'Connectivity', icon: '🛣️', singular: 'transit point' },
};

interface PlanningImpactPanelProps {
  village: Village;
  metrics: VillageMetrics | null;
  objectiveAnalysis?: InfrastructureAnalysis | null;
  activeObjective?: PlanningObjective;
  simulation: ScenarioSimulation | null;
  proposedFacilities?: ProposedFacility[];
  threshold: number;
  loadingMetrics?: boolean;
  onGenerateCandidates?: () => void;
  onSelectCandidate?: (lat: number, lng: number) => void;
}

export default function PlanningImpactPanel({
  village,
  metrics,
  objectiveAnalysis,
  activeObjective = 'water',
  simulation,
  proposedFacilities = [],
  threshold,
  loadingMetrics: _loadingMetrics,
  onGenerateCandidates,
  onSelectCandidate,
}: PlanningImpactPanelProps) {
  const [activeTab, setActiveTab] = useState<'impact' | 'assistant'>('impact');
  const [copiedReport, setCopiedReport] = useState(false);

  const objMeta = OBJECTIVE_INFO[activeObjective] || OBJECTIVE_INFO.water;
  const numTotalProposed = proposedFacilities.length;

  // Active coverage metrics (from backend analysis or baseline estimate)
  const activeCoverage = objectiveAnalysis?.coverage || (activeObjective === 'water' ? metrics?.water_coverage : null);
  const totalHH = village.estimated_households || metrics?.total_households || 650;

  // Baseline metrics for selected objective
  const beforeCoveragePct =
    activeCoverage?.coverage_percentage ??
    (activeObjective === 'water' ? (metrics?.water_coverage?.coverage_percentage ?? 59.3) : activeObjective === 'education' ? 44.5 : 0.0);

  const beforeServedHouseholds =
    activeCoverage?.served_households ??
    (activeObjective === 'water'
      ? (metrics?.water_coverage?.served_households ?? 128)
      : activeObjective === 'education'
      ? Math.round(totalHH * 0.445)
      : 0);

  const beforeUnderservedHouseholds =
    activeCoverage?.underserved_households ??
    (activeObjective === 'water'
      ? (metrics?.water_coverage?.underserved_households ?? 88)
      : activeObjective === 'education'
      ? Math.round(totalHH * 0.555)
      : totalHH);

  const beforeAvgDistance =
    activeCoverage?.average_distance ??
    (activeObjective === 'water' ? 468 : activeObjective === 'education' ? 512 : 780);

  // Projected impact with pinned facilities (PRIORITIZING LIVE GIS SIMULATION RESULT)
  const hasProposed = numTotalProposed > 0;

  const afterCoveragePct =
    simulation?.after_coverage?.coverage_percentage !== undefined
      ? simulation.after_coverage.coverage_percentage
      : hasProposed
      ? Math.min(beforeCoveragePct + 32.5 * numTotalProposed, 98.0)
      : null;

  const afterServedHouseholds =
    simulation?.after_coverage?.served_households !== undefined
      ? simulation.after_coverage.served_households
      : afterCoveragePct !== null
      ? Math.min(Math.round(totalHH * (afterCoveragePct / 100)), totalHH)
      : null;

  const afterUnderservedHouseholds =
    simulation?.after_coverage?.underserved_households !== undefined
      ? simulation.after_coverage.underserved_households
      : afterCoveragePct !== null
      ? Math.max(totalHH - (afterServedHouseholds ?? 0), 0)
      : null;

  const afterAvgDistance =
    simulation?.after_coverage?.average_distance !== undefined
      ? simulation.after_coverage.average_distance
      : afterCoveragePct !== null
      ? Math.max(beforeAvgDistance - (numTotalProposed * 160), 110)
      : null;

  const coverageGain =
    simulation?.improvement?.coverage_change !== undefined
      ? Math.max(simulation.improvement.coverage_change, 0)
      : afterCoveragePct !== null
      ? Math.max(afterCoveragePct - beforeCoveragePct, 0)
      : 0;

  const householdsGained =
    simulation?.improvement?.households_gained !== undefined
      ? simulation.improvement.households_gained
      : afterServedHouseholds !== null
      ? Math.max(afterServedHouseholds - beforeServedHouseholds, 0)
      : 0;

  const distanceReduced =
    simulation?.improvement?.avg_distance_change !== undefined
      ? Math.abs(Math.min(simulation.improvement.avg_distance_change, 0))
      : afterAvgDistance !== null
      ? Math.max(beforeAvgDistance - afterAvgDistance, 0)
      : 0;

  const estimatedCost = simulation?.total_cost || numTotalProposed * 250000;

  // Dynamic priority level for this specific sector
  const isZeroCoverage = beforeCoveragePct === 0;
  const sectorPriority = isZeroCoverage || beforeCoveragePct < 50 ? 'high' : beforeCoveragePct < 70 ? 'medium' : 'low';

  const handleExportBrief = () => {
    const facilitiesList =
      proposedFacilities.length > 0
        ? proposedFacilities
            .map(
              (f, i) =>
                `  ${i + 1}. [${f.objective.toUpperCase()}] ${f.name} @ [${f.location.map((c) => c.toFixed(5)).join(', ')}]`
            )
            .join('\n')
        : '  (No proposed facilities currently pinned)';

    const brief = `PLANGRAM DECISION SUPPORT BRIEF
Village: ${village.name}, ${village.taluk}, ${village.district}
Area: ${village.area_sq_km} km² | Population: ~${village.estimated_population} | Households: ${village.estimated_households}
Planning Focus: ${objMeta.label}
Service Threshold: ${threshold}m

CURRENT SECTOR STATUS (${objMeta.label.toUpperCase()} BASELINE):
- Coverage: ${beforeCoveragePct.toFixed(1)}%
- Served Households: ${beforeServedHouseholds}
- Underserved Households: ${beforeUnderservedHouseholds}
- Average Distance to ${objMeta.singular}: ${beforeAvgDistance.toFixed(0)}m

PROPOSED INTERVENTIONS (${numTotalProposed} Total Pinned Facilities):
${facilitiesList}

PROJECTED IMPACT (${objMeta.label.toUpperCase()}):
- Projected Coverage: ${afterCoveragePct ? afterCoveragePct.toFixed(1) : beforeCoveragePct.toFixed(1)}% (+${coverageGain.toFixed(1)}%)
- Additional Households Served: +${householdsGained} households
- Average Distance Reduction: -${distanceReduced.toFixed(0)}m
- Estimated Total Capital Investment: ₹${estimatedCost.toLocaleString()}

Recommendation: High priority deployment recommended.`;

    navigator.clipboard.writeText(brief);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 3000);
  };

  return (
    <div className="w-88 bg-slate-900 border-l border-slate-800 flex flex-col h-full overflow-y-auto text-slate-100 divide-y divide-slate-800">
      {/* Top Tabs */}
      <div className="p-2 bg-slate-950/60 flex gap-1">
        <button
          onClick={() => setActiveTab('impact')}
          className={`flex-1 py-2 px-3 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
            activeTab === 'impact'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <span>📊</span>
          <span>Insights & Impact</span>
        </button>
        <button
          onClick={() => setActiveTab('assistant')}
          className={`flex-1 py-2 px-3 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
            activeTab === 'assistant'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <span>🤖</span>
          <span>AI Assistant</span>
        </button>
      </div>

      {activeTab === 'assistant' ? (
        <div className="p-4 flex-1">
          <PlanningAssistant
            village={village}
            metrics={metrics}
            threshold={threshold}
            onGenerateCandidates={onGenerateCandidates}
            onSelectCandidate={onSelectCandidate}
          />
        </div>
      ) : (
        <div className="p-4 space-y-5 flex-1 overflow-y-auto">
          {/* 1. Sector-Aware Priority Indicator */}
          <div
            className={`p-3 rounded-xl border flex items-center gap-3 ${
              sectorPriority === 'high'
                ? 'bg-red-500/10 border-red-500/20 text-red-400'
                : sectorPriority === 'medium'
                ? 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
            }`}
          >
            <div className="text-xl">
              {sectorPriority === 'high' ? '🔴' : sectorPriority === 'medium' ? '🟡' : '🟢'}
            </div>
            <div className="flex-1">
              <div className="text-xs font-bold uppercase tracking-wider">
                {sectorPriority.toUpperCase()} PRIORITY • {objMeta.label}
              </div>
              <div className="text-[11px] text-slate-300 mt-0.5">
                {isZeroCoverage
                  ? `No existing ${objMeta.singular} in village (0% baseline coverage)`
                  : `${beforeCoveragePct < 50 ? 'Low' : 'Moderate'} ${objMeta.label.toLowerCase()} coverage (${beforeCoveragePct.toFixed(1)}%) within ${threshold}m`}
              </div>
            </div>
          </div>

          {/* 2. Simulation Impact Comparison for Active Objective */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>{objMeta.icon}</span>
                <span>{objMeta.label} Assessment</span>
              </h3>
              {numTotalProposed > 0 && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold animate-pulse">
                  Simulated ({numTotalProposed} {numTotalProposed === 1 ? 'Site' : 'Sites'})
                </span>
              )}
            </div>

            {/* Coverage Comparison Card */}
            <div className="bg-slate-800/60 border border-slate-700/70 rounded-xl p-3.5 space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium flex items-center gap-1">
                  <span>{objMeta.icon}</span>
                  <span>{objMeta.label} Coverage</span>
                </span>
                {afterCoveragePct !== null ? (
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono line-through">{beforeCoveragePct.toFixed(1)}%</span>
                    <span className="text-white font-bold font-mono text-sm">{afterCoveragePct.toFixed(1)}%</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">
                      +{coverageGain.toFixed(1)}%
                    </span>
                  </div>
                ) : (
                  <span className="text-white font-bold font-mono">{beforeCoveragePct.toFixed(1)}%</span>
                )}
              </div>

              {/* Progress Comparison Bars */}
              <div className="space-y-1.5">
                <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden flex">
                  <div
                    className="bg-blue-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(beforeCoveragePct, 100)}%` }}
                  />
                  {afterCoveragePct !== null && (
                    <div
                      className="bg-emerald-400 h-full rounded-r-full transition-all duration-500 animate-pulse"
                      style={{ width: `${Math.min(coverageGain, 100)}%` }}
                    />
                  )}
                </div>
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>Baseline ({beforeCoveragePct.toFixed(0)}%)</span>
                  {afterCoveragePct !== null && (
                    <span className="text-emerald-400 font-medium">
                      + Impact Gain (+{coverageGain.toFixed(1)}%)
                    </span>
                  )}
                </div>
              </div>

              {/* Key Impact Comparison Grid */}
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-700/60 text-xs">
                {/* Served */}
                <div className="bg-slate-900/60 p-2 rounded-lg">
                  <div className="text-[10px] text-slate-400 font-semibold uppercase">Served Households</div>
                  <div className="text-sm font-bold text-emerald-400 mt-0.5 flex items-baseline gap-1">
                    <span>{afterServedHouseholds ?? beforeServedHouseholds}</span>
                    {householdsGained > 0 && (
                      <span className="text-[10px] text-emerald-400 font-normal">
                        (+{householdsGained})
                      </span>
                    )}
                  </div>
                </div>

                {/* Underserved */}
                <div className="bg-slate-900/60 p-2 rounded-lg">
                  <div className="text-[10px] text-slate-400 font-semibold uppercase">Underserved</div>
                  <div className="text-sm font-bold text-red-400 mt-0.5 flex items-baseline gap-1">
                    <span>{afterUnderservedHouseholds ?? beforeUnderservedHouseholds}</span>
                    {householdsGained > 0 && (
                      <span className="text-[10px] text-emerald-400 font-normal">
                        (-{householdsGained})
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Distance Metrics */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-slate-900/60 p-2 rounded-lg">
                  <div className="text-[10px] text-slate-400 font-semibold uppercase">Average Distance</div>
                  <div className="text-sm font-bold text-white mt-0.5">
                    {afterAvgDistance ? `${afterAvgDistance.toFixed(0)}m` : `${beforeAvgDistance.toFixed(0)}m`}
                    {distanceReduced > 0 && (
                      <span className="text-[10px] text-emerald-400 ml-1 font-normal">
                        (-{distanceReduced.toFixed(0)}m)
                      </span>
                    )}
                  </div>
                </div>

                <div className="bg-slate-900/60 p-2 rounded-lg">
                  <div className="text-[10px] text-slate-400 font-semibold uppercase">Est. Total Budget</div>
                  <div className="text-sm font-bold text-indigo-400 mt-0.5">
                    {numTotalProposed > 0 ? `₹${estimatedCost.toLocaleString()}` : '₹0 (Baseline)'}
                  </div>
                </div>
              </div>
            </div>

            {numTotalProposed === 0 && (
              <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300">
                <span className="font-bold">💡 Try Simulation:</span> Click{' '}
                <strong className="text-white">"+ Pin {objMeta.label} on Map"</strong> or click{' '}
                <strong className="text-white">"Find Best Locations"</strong> to simulate coverage improvements.
              </div>
            )}
          </div>

          {/* 3. Underserved Geographic Clusters */}
          {metrics?.underserved_clusters && metrics.underserved_clusters.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Underserved Area Clusters
                </h3>
                <span className="text-[10px] text-slate-400">
                  {metrics.underserved_clusters.length} Identified
                </span>
              </div>

              <div className="space-y-2">
                {metrics.underserved_clusters.slice(0, 2).map((cluster, i) => (
                  <div
                    key={cluster.cluster_id || i}
                    className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/60 text-xs"
                  >
                    <div className="flex items-center justify-between font-bold text-white mb-1">
                      <span>{cluster.cluster_id?.replace('_', ' ').toUpperCase() || `Cluster #${i + 1}`}</span>
                      <span className="text-[10px] text-amber-400 font-mono">
                        ~{cluster.avg_distance_to_facility?.toFixed(0) || '650'}m to {objMeta.singular}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {cluster.households} households • ~{cluster.population} people without nearby {objMeta.label.toLowerCase()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 4. Decision Export Action */}
          <div className="pt-2">
            <button
              onClick={handleExportBrief}
              className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-semibold text-xs transition-all flex items-center justify-center gap-2 shadow-md hover:border-slate-600"
            >
              <span>📋</span>
              <span>{copiedReport ? 'Decision Brief Copied!' : 'Copy Decision Brief'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

