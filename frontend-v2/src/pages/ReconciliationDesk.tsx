import { useState } from 'react';
import { InvestigationPanel } from '../components/InvestigationPanel';
import { TrustEvidenceSidebar } from '../components/TrustEvidenceSidebar';

export function ReconciliationDesk() {
  return (
    <div className="flex flex-col h-full w-full overflow-hidden">
      {/* Sub Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-industrial-800 shrink-0">
        <div>
          <h1 className="text-lg font-bold tracking-widest text-white">RECONCILIATION DESK</h1>
          <p className="text-xs text-industrial-500 mt-1">Decision Queue</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex bg-industrial-900 border border-industrial-800 rounded p-1">
            <button className="px-4 py-1.5 text-xs rounded bg-industrial-800 text-white font-medium shadow-sm">All Sources</button>
            <button className="px-4 py-1.5 text-xs rounded text-industrial-400 hover:text-white">Unassigned</button>
            <button className="px-4 py-1.5 text-xs rounded text-industrial-400 hover:text-white">Aging</button>
          </div>
          <div className="flex items-center text-xs text-industrial-400 gap-2 px-2">
            Sort: Confidence ↓
          </div>
          <button className="px-4 py-1.5 bg-accent-500 hover:bg-accent-600 text-black font-semibold text-xs rounded transition-colors">
            Bulk Validate
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 border-b border-industrial-800 shrink-0 divide-x divide-industrial-800">
        <StatCard value="04" label="CONFLICTED" color="text-conflict" />
        <StatCard value="11" label="AMBIGUOUS" color="text-industrial-400" />
        <StatCard value="07" label="UNMATCHED" color="text-industrial-400" />
        <StatCard value="09" label="LOW CONFIDENCE" color="text-accent-500" />
      </div>

      {/* Main Workspace (3 columns) */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* Left Column: Queue */}
        <div className="w-[320px] border-r border-industrial-800 flex flex-col bg-industrial-950 shrink-0">
          <div className="flex items-center justify-between px-4 py-3 border-b border-industrial-800 uppercase tracking-widest text-xs font-bold text-industrial-100">
            <span>Queue</span>
            <span className="text-industrial-500 font-normal tracking-normal lowercase">27 items</span>
          </div>
          <div className="flex-1 overflow-y-auto">
            {/* Placeholder Queue Items */}
            <QueueItem title="Erect Line 24&quot; line, Unit 3" id="ACT-PIP-2045" conf="94%" doc="DPR-238" status="amber" active />
            <QueueItem title="Formwork stripped, Column..." id="ACT-CIV-1180" conf="88%" doc="DPR-241" status="amber" />
            <QueueItem title="Cable tray installation comp..." id="ACT-ELE-0872" conf="61%" doc="DPR-235" status="amber" />
            <QueueItem title="Hydrotest passed, Line 18-..." id="ACT-PIP-2091" conf="97%" doc="DPR-229" status="red" />
          </div>
        </div>

        {/* Center Column: Investigation */}
        <div className="flex-1 overflow-y-auto bg-[#0c0c0c] p-6 pb-24 relative">
          <div className="max-w-4xl mx-auto">
             <InvestigationPanel />
          </div>
          
          {/* Action Bar (Fixed at bottom of center panel) */}
          <div className="fixed bottom-0 left-[320px] right-[320px] p-4 bg-industrial-950 border-t border-industrial-800 flex items-center justify-end gap-3 z-10">
             <button className="px-4 py-2 text-sm font-medium text-white hover:bg-industrial-800 rounded border border-industrial-700 transition-colors">Reject Match</button>
             <button className="px-4 py-2 text-sm font-medium text-white hover:bg-industrial-800 rounded border border-industrial-700 transition-colors">Reassign</button>
             <button className="px-4 py-2 text-sm font-medium text-black bg-accent-500 hover:bg-accent-600 rounded transition-colors">Approve & Validate</button>
          </div>
        </div>

        {/* Right Column: Trust & Evidence */}
        <div className="w-[320px] border-l border-industrial-800 bg-industrial-950 flex flex-col shrink-0">
          <div className="px-4 py-3 border-b border-industrial-800 uppercase tracking-widest text-xs font-bold text-industrial-100">
            Trust + Evidence
          </div>
          <div className="flex-1 overflow-y-auto">
             <TrustEvidenceSidebar />
          </div>
        </div>

      </div>
    </div>
  );
}

// Subcomponents for layout demonstration
function StatCard({ value, label, color }: { value: string; label: string; color: string }) {
  return (
    <div className="p-6 bg-industrial-950 hover:bg-industrial-900 transition-colors cursor-pointer">
      <div className={`text-3xl font-mono mb-1 ${color}`}>{value}</div>
      <div className="text-xs tracking-[0.2em] font-medium text-industrial-500 uppercase">{label}</div>
    </div>
  );
}

function QueueItem({ title, id, conf, doc, status, active = false }: any) {
  const dotColor = status === 'amber' ? 'bg-accent-500' : status === 'red' ? 'bg-conflict' : 'bg-industrial-600';
  return (
    <div className={`px-4 py-4 border-b border-industrial-800/50 cursor-pointer transition-colors ${active ? 'bg-industrial-900' : 'hover:bg-industrial-900/50'}`}>
      <div className="flex items-start gap-3">
        <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${dotColor}`} />
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start mb-1">
            <h3 className={`text-sm truncate pr-2 ${active ? 'text-white font-medium' : 'text-industrial-200'}`}>{title}</h3>
            <span className="text-accent-500 font-bold text-sm">{conf}</span>
          </div>
          <div className="flex justify-between items-center text-xs font-mono text-industrial-500">
            <span>{id}</span>
            <span>{doc}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
