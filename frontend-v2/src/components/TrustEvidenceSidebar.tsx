import { Check } from 'lucide-react';

export function TrustEvidenceSidebar() {
  return (
    <div className="space-y-8 p-6">
      
      {/* Match Confidence */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-3">MATCH CONFIDENCE</div>
        <div className="text-accent-500 text-5xl font-bold mb-2">94%</div>
        <div className="text-industrial-400 text-sm">High confidence — deterministic signals</div>
      </div>

      <div className="h-px bg-industrial-800" />

      {/* Trust State */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-3">TRUST STATE</div>
        {/* Progress Bar placeholder */}
        <div className="h-1.5 w-full bg-industrial-800 mb-6 flex">
          <div className="h-full bg-accent-500 w-[94%]"></div>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-start gap-3 text-sm">
            <Check className="w-4 h-4 text-verified mt-0.5 shrink-0" />
            <span className="text-verified">2 supporting sources</span>
          </div>
          <div className="flex items-start gap-3 text-sm">
            <Check className="w-4 h-4 text-verified mt-0.5 shrink-0" />
            <span className="text-verified">6 compatible signals</span>
          </div>
          <div className="flex items-start gap-3 text-sm">
            <Check className="w-4 h-4 text-verified mt-0.5 shrink-0" />
            <span className="text-verified">No conflicts</span>
          </div>
        </div>
      </div>

      <div className="h-px bg-industrial-800" />

      {/* Evidence */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-4">EVIDENCE</div>
        
        <div className="space-y-6">
          <div>
            <div className="text-industrial-400 text-xs font-mono mb-2">SOURCE: DPR-238</div>
            <p className="text-industrial-200 text-sm italic mb-2">"24 dia line erection completed in Unit 3."</p>
            <div className="flex items-center gap-2 text-xs text-industrial-500 font-mono">
              <span>Page 2</span>
              <span>·</span>
              <span>Piping</span>
            </div>
          </div>
          
          <div>
            <div className="text-industrial-400 text-xs font-mono mb-2">SOURCE: Photo-1182</div>
            <p className="text-industrial-200 text-sm mb-2">Site photo, Unit 3 tie-in point</p>
          </div>
        </div>
      </div>

      <div className="h-px bg-industrial-800" />

      {/* Schedule Context */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-4">SCHEDULE CONTEXT</div>
        <div className="space-y-3">
          <div className="flex justify-between items-center text-sm">
            <span className="text-industrial-400">Planned</span>
            <span className="font-mono text-white">01-05 SEP</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-industrial-400">Observed</span>
            <span className="font-mono text-white">03 SEP · 16:00</span>
          </div>
          <div className="flex justify-between items-center text-sm mt-4">
            <span className="text-industrial-400">Predecessor</span>
            <span className="text-verified flex items-center gap-1">Complete <Check className="w-3 h-3" /></span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-industrial-400">Successor</span>
            <span className="text-white">Pending</span>
          </div>
          <div className="flex justify-between items-center text-sm mt-4">
            <span className="text-industrial-400">Critical path</span>
            <span className="text-accent-500">Yes</span>
          </div>
        </div>
      </div>

      <div className="h-px bg-industrial-800" />

      {/* Conflicts */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-3">CONFLICTS</div>
        <div className="text-verified text-sm">None detected</div>
      </div>

      <div className="h-px bg-industrial-800" />

      {/* Audit */}
      <div>
        <div className="text-industrial-400 text-xs tracking-widest uppercase mb-3">AUDIT</div>
        {/* Placeholder for audit trail */}
      </div>

    </div>
  );
}
