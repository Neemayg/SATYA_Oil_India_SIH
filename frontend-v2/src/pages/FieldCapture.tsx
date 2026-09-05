import { useState } from 'react';
import { Link } from 'react-router-dom';
import { UploadCloud } from 'lucide-react';
import { uploadText } from '../services/api';
import { Badge, Button, Card, Label, PageHeader, nice } from '../components/ui';
import { cn } from '../lib/utils';

const SAMPLE = `Daily Progress Report - Duliajan Field Office - Date: 2026-09-05
ACT-1014: Mainline ROW Clearing & Grading Sec 1 Km 2.0 to 4.0, 600 Meters completed today.
Trench excavation Section 1 continued, 350 m done, backfilling pending.
HDD river crossing Section 3 pullback halted, NDT clearance pending.`;
const TYPES = [['DPR_EXCEL', 'Daily Progress Report'], ['SITE_DIARY', 'Site Diary'], ['SUPERVISOR_NOTE', 'Supervisor Note'], ['QA_REPORT', 'QA Report'], ['VOICE_TRANSCRIPT', 'Voice Transcript']];

export function FieldCapture() {
  const [text, setText] = useState(''); const [type, setType] = useState('DPR_EXCEL'); const [name, setName] = useState('');
  const [busy, setBusy] = useState(false); const [result, setResult] = useState<any>(null); const [error, setError] = useState('');

  async function onFile(f: File | null) { if (!f) return; setName(f.name); setText(await f.text()); }
  async function submit() { setBusy(true); setError(''); setResult(null); try { setResult(await uploadText(text, type, name || 'web_upload.txt')); } catch (e: any) { setError(String(e?.message ?? e)); } setBusy(false); }

  return (
    <>
      <PageHeader title="Field Capture" subtitle="Upload source documents · extraction and matching run automatically" />
      <div className="px-8 py-6 grid grid-cols-[1fr_380px] gap-5">
        <Card>
          <div className="p-5">
            <label className="block border border-dashed border-ink-3/60 rounded-sm p-8 text-center cursor-pointer hover:border-ink-2">
              <UploadCloud className="w-7 h-7 mx-auto text-ink-2" />
              <div className="text-ink mt-3">Drag and drop a file here, or click to browse</div>
              <div className="text-xs text-ink-3 mt-1">Supports TXT and CSV daily progress reports, site notes, transcripts</div>
              <input type="file" accept=".txt,.csv,.md,.json" className="hidden" onChange={e => onFile(e.target.files?.[0] ?? null)} />
            </label>
            <Label className="mt-6 mb-2">Source type</Label>
            <div className="flex border border-line rounded-sm overflow-hidden">
              {TYPES.map(([v, l]) => <button key={v} onClick={() => setType(v)} className={cn('flex-1 py-2.5 text-sm', type === v ? 'bg-surface-2 text-ink' : 'text-ink-3 hover:text-ink-2')}>{l}</button>)}
            </div>
            <div className="flex items-center justify-between mt-6 mb-2"><Label>Content{name ? ` · ${name}` : ''}</Label><button onClick={() => { setText(SAMPLE); setName('sample_dpr.txt'); }} className="text-xs text-brand">Use sample report</button></div>
            <textarea value={text} onChange={e => setText(e.target.value)} rows={10} placeholder="Paste report text, one observation per line…" className="w-full bg-bg border border-line rounded-sm p-3 text-sm font-mono focus:outline-none focus:border-ink-3" />
            <div className="flex items-center justify-between mt-4"><span className="text-xs text-ink-3">Extraction typically completes within seconds</span><Button onClick={submit} disabled={busy || !text.trim()}>{busy ? 'Processing…' : 'Upload & Process'}</Button></div>
            {error && <div className="mt-3 text-sm text-bad">{error}</div>}
          </div>
        </Card>
        <Card title="Result">
          {!result ? <div className="p-5 text-sm text-ink-3">Nothing processed yet.</div> : (
            <div className="p-5 text-sm">
              <div className="flex justify-between"><span className="text-ink-3">Source</span><span className="font-mono text-xs">{result.source_id}</span></div>
              <div className="flex justify-between mt-2"><span className="text-ink-3">Events extracted</span><span className="text-ok font-semibold">{result.events_extracted_count}</span></div>
              <div className="flex justify-between mt-2"><span className="text-ink-3">Quarantined</span><span>{result.quarantined_count}</span></div>
              <ul className="mt-5 space-y-3">{(result.events_extracted ?? []).map((e: any) => (
                <li key={e.event_id} className="border border-line rounded-sm p-3">
                  <div className="flex items-center gap-2"><Badge tone="brand">{nice(e.event_type)}</Badge><span className="text-xs text-ink-3">{nice(e.discipline)}</span></div>
                  <p className="text-ink mt-2 leading-snug">{e.extracted_statement}</p>
                  <Link to={`/reconciliation/${e.event_id}`} className="text-brand text-xs mt-2 inline-block">Open in Reconciliation →</Link>
                </li>))}</ul>
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
