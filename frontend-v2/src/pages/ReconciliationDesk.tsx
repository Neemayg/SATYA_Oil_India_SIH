import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Check } from 'lucide-react';
import { getQueue, getTrace, getMatch, getFingerprints, submitDecision, type QueueItem, type Trace, type MatchResult, type Fingerprint, type DecisionType } from '../services/api';
import { Badge, Button, Empty, Label, Spinner, fmtDate, nice, outcomeTone, pct, trustTone } from '../components/ui';
import { cn } from '../lib/utils';

export function ReconciliationDesk() {
  const { eventId } = useParams();
  const nav = useNavigate();
  const [queue, setQueue] = useState<QueueItem[] | null>(null);
  const [fps, setFps] = useState<Fingerprint[]>([]);
  const [trace, setTrace] = useState<Trace | null>(null);
  const [match, setMatch] = useState<MatchResult | null>(null);
  const [loadingItem, setLoadingItem] = useState(false);
  const [note, setNote] = useState('');
  const [pick, setPick] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  async function loadQueue() {
    const [q, f] = await Promise.all([getQueue().catch(() => []), getFingerprints()]);
    setQueue(q); setFps(f);
    if (!eventId && q[0]) nav(`/reconciliation/${q[0].event_id}`, { replace: true });
  }
  useEffect(() => { loadQueue(); }, []);
  useEffect(() => {
    if (!eventId) { setTrace(null); setMatch(null); return; }
    setLoadingItem(true); setMsg(null); setNote(''); setPick('');
    Promise.all([getTrace(eventId).catch(() => null), getMatch(eventId)]).then(([t, m]) => { setTrace(t); setMatch(m); setLoadingItem(false); });
  }, [eventId]);

  async function decide(type: DecisionType) {
    if (!trace || !eventId) return;
    if (type === 'CHANGE_MATCH' && !pick) { setMsg({ ok: false, text: 'Select the correct activity first.' }); return; }
    setBusy(true); setMsg(null);
    try {
      await submitDecision({
        event_id: eventId, decision_type: type, reviewed_trust_version: trace.latest_trust_assessment?.version_index ?? 1,
        reviewed_match_result_id: match?.match_id, selected_activity_id: pick || undefined,
        override_reason_category: type === 'CHANGE_MATCH' ? 'OTHER' : undefined, reason_notes: note,
        requested_evidence_types: type === 'REQUEST_EVIDENCE' ? ['SITE_PHOTO', 'QA_CERTIFICATE'] : undefined,
      });
      setMsg({ ok: true, text: `${nice(type)} recorded. Trusted event created.` });
      const q = await getQueue().catch(() => []); setQueue(q);
      const next = q.find(i => i.event_id !== eventId);
      setTimeout(() => nav(next ? `/reconciliation/${next.event_id}` : '/reconciliation'), 700);
    } catch (e: any) { setMsg({ ok: false, text: String(e?.message ?? e) }); }
    setBusy(false);
  }

  if (!queue) return <Spinner />;
  const names = Object.fromEntries(fps.map(f => [f.activity_id, f]));
  const ev = trace?.execution_event; const ta = trace?.latest_trust_assessment; const top = match?.candidates?.[0]; const conflicts = trace?.conflicts ?? [];
  const byReason = (r: string) => queue.filter(q => q.trigger_reason === r).length;
  const sel = names[pick || match?.selected_activity_id || ''];

  return (
    <div className="flex flex-col min-h-[calc(100vh-56px)]">
      <div className="px-8 py-4 border-b border-line flex items-center justify-between">
        <div><h1 className="text-lg font-bold tracking-[0.2em] uppercase text-ink">Reconciliation Desk</h1><p className="text-sm text-ink-3 mt-0.5">Decision Queue</p></div>
        <div className="text-xs text-ink-3 font-mono">Sort: Confidence ↓</div>
      </div>
      <div className="grid grid-cols-4 border-b border-line divide-x divide-line">
        <Cnt label="Conflicted" n={queue.filter(q => q.trigger_reason.includes('CONFLICT')).length} tone="text-bad" />
        <Cnt label="Ambiguous / gaps" n={byReason('INSUFFICIENT_EVIDENCE_OR_GAPS') + byReason('AMBIGUOUS_MATCH')} tone="text-amber" />
        <Cnt label="Unmatched" n={byReason('UNMATCHED')} tone="text-ink-2" />
        <Cnt label="Low confidence" n={byReason('LOW_MATCH_CONFIDENCE')} tone="text-amber" />
      </div>

      <div className="flex flex-1 min-h-0">
        {/* Queue */}
        <aside className="w-[320px] shrink-0 border-r border-line">
          <div className="px-5 py-3 border-b border-line flex justify-between items-center"><Label className="text-ink">Queue</Label><span className="text-xs text-ink-3 font-mono">{queue.length} items</span></div>
          {queue.length === 0 ? <Empty>Nothing to review.</Empty> : queue.map(q => {
            const on = q.event_id === eventId;
            return (
              <div key={q.queue_item_id} onClick={() => nav(`/reconciliation/${q.event_id}`)} className={cn('px-5 py-4 border-b border-line cursor-pointer border-l-2', on ? 'bg-brand-soft/60 border-l-brand' : 'border-l-transparent hover:bg-surface-2')}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2 min-w-0"><i className={cn('w-2 h-2 rounded-full mt-1.5 shrink-0', q.match_confidence >= 0.75 ? 'bg-ok' : q.match_confidence >= 0.4 ? 'bg-amber' : 'bg-bad')} /><span className="text-sm text-ink truncate">{nice(q.trigger_reason)}</span></div>
                  <span className={cn('font-semibold tabular-nums', q.match_confidence >= 0.75 ? 'text-ok' : 'text-amber')}>{pct(q.match_confidence)}</span>
                </div>
                <div className="flex justify-between mt-1.5 font-mono text-[11px] text-ink-3"><span>{q.event_id}</span><span>{q.priority.replace(/^P\d_/, '')} · {fmtDate(q.created_at)}</span></div>
              </div>
            );
          })}
        </aside>

        {/* Investigation */}
        <section className="flex-1 min-w-0 px-8 py-6 pb-28 relative">
          {!eventId ? <Empty>Select an item from the queue.</Empty> : loadingItem || !ev ? <Spinner /> : (
            <div className="max-w-3xl space-y-8">
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <div className="font-mono text-xs text-ink-3">{match?.selected_activity_id ?? ev.raw_observed_activity_id ?? '—'}</div>
                  <div className="text-sm tracking-[0.15em] uppercase text-ink-2 mt-1">{nice(ev.discipline)}{ev.area_location ? ` · ${ev.area_location}` : ''}</div>
                  <div className="mt-2"><Badge tone={outcomeTone(match?.outcome)}>{nice(match?.outcome ?? 'not matched')}</Badge></div>
                </div>
                <div><Label>Planned</Label><div className="font-mono text-sm mt-2">{sel ? `${fmtDate(sel.planned_start)} – ${fmtDate(sel.planned_finish)}` : '—'}</div></div>
                <div><Label>Observed</Label><div className="font-mono text-sm mt-2">{fmtDate(ev.observed_timestamp)}</div></div>
              </div>

              <div>
                <Label className="mb-3">Field observation</Label>
                <div className="bg-surface border-l-2 border-amber p-5 rounded-r-sm">
                  <p className="text-lg italic text-ink leading-relaxed">“{ev.extracted_statement}”</p>
                  <div className="font-mono text-xs text-ink-3 mt-3">{trace?.source_document?.file_name ?? ev.source_id} · {nice(ev.event_type)}</div>
                </div>
              </div>

              <div>
                <Label className="mb-3">Extracted event</Label>
                <div className="grid grid-cols-2 gap-4">
                  <Box label={nice(ev.event_type)} value={`${fmtDate(ev.observed_timestamp)}${ev.observed_quantity != null ? ` · ${ev.observed_quantity} ${ev.unit_of_measure ?? ''}` : ''}`} />
                  <Box label="Discipline / area" value={`${nice(ev.discipline)} / ${ev.area_location ?? 'unspecified'}`} />
                </div>
              </div>

              <div>
                <Label className="mb-3">Candidate activities</Label>
                {!match?.candidates?.length ? <div className="text-sm text-ink-3">No candidates scored. Choose an activity manually below.</div> : (
                  <div className="grid grid-cols-2 gap-4">
                    {match.candidates.slice(0, 4).map((c, i) => {
                      const on = (pick || match.selected_activity_id) === c.activity_id;
                      return (
                        <div key={c.activity_id} onClick={() => setPick(c.activity_id)} className={cn('relative bg-surface border p-5 rounded-sm cursor-pointer', on ? 'border-amber' : 'border-line hover:border-ink-3')}>
                          {on && <div className="absolute left-0 top-0 bottom-0 w-1 bg-amber" />}
                          <div className="font-mono text-xs text-ink-3">{c.activity_id}</div>
                          <div className="text-ink text-base mt-1 leading-snug">{c.activity_name}</div>
                          <div className="flex items-end justify-between mt-4"><span className={cn('text-3xl font-semibold tabular-nums', on ? 'text-amber' : 'text-ink-2')}>{pct(c.scores?.overall_confidence_score)}</span><span className="text-sm text-ink-3">{on ? 'Selected' : i === 0 ? 'Top' : 'Alternate'}</span></div>
                        </div>
                      );
                    })}
                  </div>
                )}
                <div className="mt-3 flex items-center gap-3 text-xs text-ink-3"><span>Reassign to:</span>
                  <select value={pick} onChange={e => setPick(e.target.value)} className="flex-1 bg-surface border border-line rounded-sm px-2 py-1.5 text-sm text-ink font-mono"><option value="">—</option>{fps.map(f => <option key={f.activity_id} value={f.activity_id}>{f.activity_id} · {f.activity_name}</option>)}</select>
                </div>
              </div>

              {top && (
                <div>
                  <Label className="mb-3">Why this match?</Label>
                  <div className="grid grid-cols-2 gap-x-8">
                    {Object.entries(top.scores ?? {}).filter(([k]) => k !== 'overall_confidence_score').map(([k, v]) => (
                      <div key={k} className="flex justify-between items-center border-b border-line py-2.5 text-sm"><span className="text-ink-2">{nice(k.replace('_score', ''))}</span><span className={cn('text-[11px] tracking-[0.15em] uppercase font-semibold', v >= 0.8 ? 'text-ok' : v >= 0.4 ? 'text-amber' : 'text-ink-3')}>{v >= 0.8 ? 'Match' : v >= 0.4 ? 'Compatible' : 'No signal'}</span></div>
                    ))}
                  </div>
                  <ul className="mt-4 space-y-1.5">{(top.match_reasons ?? []).map((r, i) => <li key={i} className="text-xs text-ink-2 font-mono">{r}</li>)}</ul>
                </div>
              )}

              <textarea value={note} onChange={e => setNote(e.target.value)} rows={2} placeholder="Validation note…" className="w-full bg-surface border border-line rounded-sm p-3 text-sm focus:outline-none focus:border-ink-3" />
              {msg && <div className={cn('text-sm', msg.ok ? 'text-ok' : 'text-bad')}>{msg.text}</div>}
            </div>
          )}
          {eventId && ev && (
            <div className="fixed bottom-0 left-[320px] right-[320px] px-8 py-4 bg-bg border-t border-line flex items-center justify-end gap-3 z-10">
              <Button variant="ghost" onClick={() => decide('DEFER')} disabled={busy}>Defer</Button>
              <Button variant="secondary" onClick={() => decide('REQUEST_EVIDENCE')} disabled={busy}>Request evidence</Button>
              <Button variant="danger" onClick={() => decide('REJECT')} disabled={busy}>Reject match</Button>
              <Button variant="secondary" onClick={() => decide('CHANGE_MATCH')} disabled={busy}>Reassign</Button>
              <Button onClick={() => decide('VALIDATE')} disabled={busy}><Check className="w-4 h-4" />Approve & Validate</Button>
            </div>
          )}
        </section>

        {/* Trust + evidence */}
        <aside className="w-[320px] shrink-0 border-l border-line">
          <div className="px-5 py-3 border-b border-line"><Label className="text-ink">Trust + Evidence</Label></div>
          {ev && (
            <div className="p-5 space-y-7">
              <div><Label>Match confidence</Label><div className={cn('text-5xl font-semibold mt-2 tabular-nums', (match?.confidence_score ?? 0) >= 0.75 ? 'text-amber' : 'text-bad')}>{pct(match?.confidence_score)}</div><div className="text-sm text-ink-3 mt-1">{(match?.confidence_score ?? 0) >= 0.75 ? 'High confidence — deterministic signals' : 'Low confidence — needs planner input'}</div></div>
              <hr className="border-line" />
              <div>
                <Label>Trust state</Label>
                <div className="mt-3"><Badge tone={trustTone(ta?.trust_status)} filled>{nice(ta?.trust_status ?? 'none')}</Badge></div>
                <ul className="mt-4 space-y-2 text-sm">
                  <Li ok={(ta?.evidence_support ?? 0) >= 0.6}>{pct(ta?.evidence_support)} evidence support</Li>
                  <Li ok={conflicts.length === 0}>{conflicts.length === 0 ? 'No conflicts' : `${conflicts.length} conflict(s)`}</Li>
                  <Li ok={!ta?.has_evidence_gaps}>{ta?.has_evidence_gaps ? 'Evidence gaps present' : 'No evidence gaps'}</Li>
                </ul>
                {ta?.gating_trigger && <p className="text-xs text-ink-3 mt-3 leading-relaxed font-mono">{ta.gating_trigger}</p>}
              </div>
              <hr className="border-line" />
              <div>
                <Label>Evidence</Label>
                <div className="font-mono text-xs text-ink-3 mt-3">SOURCE: {trace?.source_document?.file_name ?? ev.source_id}</div>
                <p className="text-sm italic text-ink-2 mt-1">“{ev.extracted_statement}”</p>
                <div className="font-mono text-[11px] text-ink-3 mt-1">{nice(trace?.source_document?.source_type)} · extraction {pct(ev.extraction_confidence)}</div>
              </div>
              {sel && (<>
                <hr className="border-line" />
                <div>
                  <Label>Schedule context</Label>
                  <div className="mt-3 text-sm space-y-2">
                    <div className="flex justify-between"><span className="text-ink-3">Planned</span><span className="font-mono text-xs">{fmtDate(sel.planned_start)} – {fmtDate(sel.planned_finish)}</span></div>
                    <div className="flex justify-between"><span className="text-ink-3">Observed</span><span className="font-mono text-xs">{fmtDate(ev.observed_timestamp)}</span></div>
                    <div className="flex justify-between"><span className="text-ink-3">Discipline</span><span>{nice(sel.discipline)}</span></div>
                    <div className="flex justify-between"><span className="text-ink-3">Critical path</span><span className={sel.is_critical ? 'text-amber' : ''}>{sel.is_critical ? 'Yes' : 'No'}</span></div>
                  </div>
                </div>
              </>)}
              <hr className="border-line" />
              <div><Label>Conflicts</Label>{conflicts.length === 0 ? <div className="text-ok text-sm mt-2">None detected</div> : conflicts.map((c: any) => <div key={c.conflict_id} className="mt-2 text-sm"><Badge tone="bad">{c.severity}</Badge> <span className="text-ink-2">{nice(c.conflict_type)}</span></div>)}</div>
              <hr className="border-line" />
              <div><Label>Audit</Label><div className="text-xs text-ink-3 mt-2 font-mono">Trust v{ta?.version_index ?? '—'} · {fmtDate(ta?.evaluated_at)}</div></div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

function Cnt({ label, n, tone }: { label: string; n: number; tone: string }) { return <div className="px-6 py-5"><Label>{label}</Label><div className={`text-3xl font-mono mt-1 ${tone}`}>{String(n).padStart(2, '0')}</div></div>; }
function Box({ label, value }: { label: string; value: string }) { return <div className="bg-surface border border-line p-5 rounded-sm"><Label>{label}</Label><div className="text-xl text-ink mt-2">{value}</div></div>; }
function Li({ ok, children }: { ok: boolean; children: React.ReactNode }) { return <li className={cn('flex items-center gap-2', ok ? 'text-ok' : 'text-amber')}><Check className="w-4 h-4" />{children}</li>; }
