
interface LandingHeroProps {
  onStartDemo: () => void;
  onOpenUpload: () => void;
  onOpenCatalog: () => void;
}

export default function LandingHero({ onStartDemo, onOpenUpload, onOpenCatalog }: LandingHeroProps) {
  return (
    <div className="min-h-full flex flex-col bg-slate-900 text-slate-100 relative overflow-hidden">
      {/* Subtle Background Grid & Gradients */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-gradient-to-tr from-blue-600/20 via-indigo-500/20 to-emerald-500/10 blur-[120px] pointer-events-none" />

      {/* Top Navbar */}
      <header className="relative z-10 border-b border-slate-800/80 bg-slate-950/40 backdrop-blur-md px-8 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20 text-white font-bold text-xl tracking-tight">
              P
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white">PlanGram</span>
              </div>
              <p className="text-xs text-slate-400 font-medium">Spatial Decision Support Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-sm">
            <button
              onClick={onOpenUpload}
              className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800/60 hover:bg-slate-800 text-slate-200 transition-all flex items-center gap-2"
            >
              <span>📁</span>
              <span>Data Manager</span>
            </button>
            <button
              onClick={onStartDemo}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium shadow-md shadow-blue-600/25 transition-all flex items-center gap-2"
            >
              <span>Try Demo</span>
              <span className="text-xs">→</span>
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 flex-1 max-w-7xl mx-auto px-8 py-16 flex flex-col justify-center">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider">
            <span>Rural Infrastructure Intelligence</span>
            <span className="text-slate-500">•</span>
            <span>Decision Support System</span>
          </div>

          {/* Title & Tagline */}
          <div className="space-y-3">
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-tight">
              PlanGram
            </h1>
            <p className="text-2xl md:text-3xl font-semibold bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400 bg-clip-text text-transparent">
              Explore. Simulate. Plan.
            </p>
          </div>

          {/* Supporting Text */}
          <p className="text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Turn village geospatial data into actionable infrastructure planning decisions.
            Simulate facility placement, evaluate population coverage, and optimize public investments before ground implementation.
          </p>

          {/* Primary Action Buttons */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={onStartDemo}
              className="px-8 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-base shadow-xl shadow-blue-600/25 hover:shadow-blue-500/35 transform hover:-translate-y-0.5 transition-all flex items-center gap-3"
            >
              <span>🚀</span>
              <span>Try Demo</span>
              <span className="text-blue-200">→</span>
            </button>

            <button
              onClick={onOpenUpload}
              className="px-8 py-4 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-semibold text-base shadow-md hover:border-slate-600 transition-all flex items-center gap-3"
            >
              <span>📤</span>
              <span>Upload Village Data</span>
            </button>

            <button
              onClick={onOpenCatalog}
              className="px-6 py-4 rounded-xl bg-transparent hover:bg-slate-800/40 text-slate-400 hover:text-slate-200 font-medium text-sm transition-all"
            >
              Open Existing Project
            </button>
          </div>
        </div>

        {/* 3-Step Explanation Section */}
        <div className="mt-20 pt-12 border-t border-slate-800/80">
          <div className="text-center mb-8">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Planning Workflow</span>
            <h2 className="text-xl font-bold text-slate-200 mt-1">How PlanGram Powers Rural Planning</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {/* Step 1 */}
            <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 hover:border-blue-500/40 transition-all group">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-lg mb-4 group-hover:scale-105 transition-transform">
                01
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Explore</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Understand your village through spatial data. Inspect buildings, existing facilities, land parcels, and identify underserved household clusters.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 hover:border-indigo-500/40 transition-all group">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-lg mb-4 group-hover:scale-105 transition-transform">
                02
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Simulate</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Test infrastructure proposals before implementation. Generate algorithmic candidate sites or place custom proposed facilities directly on the map.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 hover:border-emerald-500/40 transition-all group">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-lg mb-4 group-hover:scale-105 transition-transform">
                03
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Decide</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Compare impact, cost, and accessibility before investing. Measure coverage gain, underserved reduction, and average distance improvements.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/80 bg-slate-950/60 px-8 py-4">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
          <div className="flex items-center gap-4">
            <span>© 2026 PlanGram Decision Support System</span>
            <span>•</span>
            <span className="text-slate-400">Compatible with SVAMITVA, OpenStreetMap & Custom GIS</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Demonstration Prototype Ready</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
