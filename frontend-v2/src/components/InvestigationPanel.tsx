export function InvestigationPanel() {
  return (
    <div className="space-y-8 pb-8">
      {/* Header Info */}
      <div className="grid grid-cols-3 gap-8">
        <div>
          <div className="text-industrial-500 text-xs font-mono mb-1">ACT-PIP-2045</div>
          <div className="text-industrial-200 text-sm tracking-widest font-medium uppercase mb-2">PIPING · UNIT 3</div>
          <div className="inline-block border border-accent-500 text-accent-500 px-2 py-0.5 text-xs font-bold tracking-widest uppercase">
            AMBIGUOUS MATCH
          </div>
        </div>
        <div>
          <div className="text-industrial-500 text-xs tracking-widest uppercase mb-2">PLANNED</div>
          <div className="text-white font-mono text-sm">01-05 SEP</div>
        </div>
        <div>
          <div className="text-industrial-500 text-xs tracking-widest uppercase mb-2">OBSERVED</div>
          <div className="text-white font-mono text-sm">03 SEP · 16:00</div>
        </div>
        {/* ACTUAL is empty in the design until validated */}
      </div>

      {/* Field Observation */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-3">FIELD OBSERVATION</div>
        <div className="bg-industrial-900 border-l-2 border-accent-500 p-5 rounded-r">
          <p className="text-white text-lg italic font-medium leading-relaxed mb-4">
            "24 dia line erection completed in Unit 3."
          </p>
          <div className="flex items-center gap-4 text-xs font-mono text-industrial-500">
            <span>DPR-238</span>
            <span>·</span>
            <span>Page 2</span>
            <span>·</span>
            <span>Piping</span>
          </div>
        </div>
      </div>

      {/* Extracted Event */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-3">EXTRACTED EVENT</div>
        <div className="grid grid-cols-2 gap-4">
          <div className="border border-industrial-800 bg-industrial-950 p-5 rounded">
            <div className="text-industrial-500 text-xs tracking-widest uppercase mb-2">FINISH</div>
            <div className="text-2xl text-white font-medium">03 SEP 2026 · 16:00</div>
          </div>
          <div className="border border-industrial-800 bg-industrial-950 p-5 rounded">
            <div className="text-industrial-500 text-xs tracking-widest uppercase mb-2">DISCIPLINE / AREA</div>
            <div className="text-2xl text-white font-medium">Piping / Unit 3</div>
          </div>
        </div>
      </div>

      {/* Candidate Activities */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-3">CANDIDATE ACTIVITIES</div>
        <div className="grid grid-cols-2 gap-4">
          {/* Selected Candidate */}
          <div className="border border-accent-500 bg-industrial-950 p-5 rounded relative overflow-hidden">
            {/* Selection highlight bar */}
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-accent-500"></div>
            <div className="text-industrial-500 text-xs font-mono mb-2">ACT-PIP-2045</div>
            <div className="text-white text-lg font-medium mb-4">Erect Line 24"-XX</div>
            <div className="flex items-end justify-between">
              <div className="text-accent-500 text-3xl font-bold">94%</div>
              <div className="text-industrial-400 text-sm">Selected</div>
            </div>
          </div>
          
          {/* Alternate Candidate */}
          <div className="border border-industrial-800 bg-industrial-950 p-5 rounded hover:border-industrial-700 transition-colors cursor-pointer">
            <div className="text-industrial-500 text-xs font-mono mb-2">ACT-PIP-2054</div>
            <div className="text-industrial-200 text-lg font-medium mb-4">Erect Line 24"-YY</div>
            <div className="flex items-end justify-between">
              <div className="text-industrial-400 text-3xl font-bold">67%</div>
              <div className="text-industrial-500 text-sm">Alternate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Why This Match */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-3">WHY THIS MATCH?</div>
        <div className="grid grid-cols-2 gap-x-8 gap-y-4">
          <div className="flex justify-between items-center border-b border-industrial-800 pb-2">
            <span className="text-industrial-300">Line identifier</span>
            <span className="text-verified font-medium text-sm tracking-widest uppercase">MATCH</span>
          </div>
          <div className="flex justify-between items-center border-b border-industrial-800 pb-2">
            <span className="text-industrial-300">Discipline</span>
            <span className="text-verified font-medium text-sm tracking-widest uppercase">MATCH</span>
          </div>
          <div className="flex justify-between items-center border-b border-industrial-800 pb-2">
            <span className="text-industrial-300">Area</span>
            <span className="text-verified font-medium text-sm tracking-widest uppercase">MATCH</span>
          </div>
          <div className="flex justify-between items-center border-b border-industrial-800 pb-2">
            <span className="text-industrial-300">WBS context</span>
            <span className="text-accent-500 font-medium text-sm tracking-widest uppercase">COMPATIBLE</span>
          </div>
          <div className="flex justify-between items-center border-b border-industrial-800 pb-2">
            <span className="text-industrial-300">Terminology</span>
            <span className="text-verified font-medium text-sm tracking-widest uppercase">MATCH</span>
          </div>
          <div className="flex justify-between items-center border-b border-industrial-800 pb-2">
            <span className="text-industrial-300">Temporal</span>
            <span className="text-accent-500 font-medium text-sm tracking-widest uppercase">COMPATIBLE</span>
          </div>
        </div>
      </div>

    </div>
  );
}
