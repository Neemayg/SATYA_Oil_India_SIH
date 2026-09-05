import { useEffect, useState } from 'react';
import { AlertCircle, GitMerge, Route, TrendingUp, CalendarClock, ClipboardCheck, ShieldCheck } from 'lucide-react';
import { getAnalytics, getSignals, getProjection, getAudit, type Signal, type Projection, type AuditReport } from '../services/api';
import { Badge, Card, Empty, Label, PageHeader, Spinner, nice } from '../components/ui';

export function Reports() {
  const [a, setA] = useState<any>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [proj, setProj] = useState<Projection | null>(null);
  const [audit, setAudit] = useState<AuditReport | null>(null);
  const [open, setOpen] = useState<'audit' | 'gaps' | 'signals' | 'bench' | 'patterns' | null>('audit');

  useEffect(() => { (async () => { const [x, s, p, au] = await Promise.all([getAnalytics(), getSignals(), getProjection(), getAudit()]); setA(x); setSignals(s); setProj(p); setAudit(au); })(); }, []);
  if (!a) return <Spinner />;
  const gaps = Object.values(proj?.activity_progress ?? {}).filter(p => p.unverified_event_count > 0 || (p.is_critical && p.status === 'NOT_STARTED'));

  const tiles = [
    { key: 'audit', icon: ShieldCheck, title: 'Manager Audit Report', desc: 'Worker claims vs independent site audits', n: audit?.summary.activities_with_claims ?? 0 },
    { key: 'gaps', icon: AlertCircle, title: 'Evidence Gap Report', desc: 'Activities lacking supporting documentation', n: gaps.length },
    { key: 'signals', icon: GitMerge, title: 'Conflict & Signal Log', desc: 'Detected warnings and resolution state', n: signals.length },
    { key: 'bench', icon: TrendingUp, title: 'Productivity Benchmarks', desc: 'Actual execution rates by discipline', n: a.benchmarks.length },
    { key: 'patterns', icon: Route, title: 'Resolution Patterns', desc: 'How planners resolved past conflicts', n: a.patterns.length },
    { key: null, icon: CalendarClock, title: 'Schedule Variance Summary', desc: `Max delay ${proj?.max_schedule_delay_days ?? 0} days · ${proj?.critical_activity_delay_count ?? 0} critical` },
    { key: null, icon: ClipboardCheck, title: 'Audit Trail Export', desc: 'Full decision and approval history' },
  ] as const;

  return (
    <>
      <PageHeader title="Reports" subtitle="Standard and exportable reports across the active project" />
      <div className="px-8 py-6">
        <div className="grid grid-cols-3 gap-5">
          {tiles.map(t => (
            <button key={t.title} onClick={() => t.key && setOpen(t.key)} className={`text-left bg-surface border rounded-md p-6 transition-colors ${open === t.key ? 'border-brand' : 'border-line hover:border-ink-3'}`}>
              <t.icon className="w-5 h-5 text-ink-2" />
              <div className="text-ink text-base mt-4">{t.title}</div>
              <div className="text-sm text-ink-3 mt-1">{t.desc}</div>
              {'n' in t && <div className="text-brand text-sm mt-4">{t.n} records · Open</div>}
            </button>
          ))}
        </div>

        <div className="mt-6">
          {open === 'audit' && (
            <Card title={`Manager audit · ${audit?.summary.activities_audited ?? 0} of ${audit?.summary.activities_with_claims ?? 0} claimed activities audited · ${audit?.summary.discrepancies ?? 0} discrepancies · avg over-reporting ${audit?.summary.avg_over_reporting_pct ?? 0}%`}>
              {!audit?.activities.length ? <Empty>No worker claims yet.</Empty> : (
                <table className="w-full text-sm"><thead><tr className="text-[11px] tracking-[0.15em] uppercase text-ink-3 border-b border-line"><th className="text-left font-medium px-5 py-3">Activity</th><th className="text-left font-medium px-3 py-3">Worker claimed</th><th className="text-left font-medium px-3 py-3">Manager verified</th><th className="text-right font-medium px-3 py-3">Variance</th><th className="text-left font-medium px-5 py-3">Status</th></tr></thead>
                  <tbody>{audit.activities.map(r => (
                    <tr key={r.activity_id} className="border-b border-line last:border-0 align-top">
                      <td className="px-5 py-3"><div className="font-mono text-xs text-ink-3">{r.activity_id}</div><div className="text-ink">{r.activity_name}</div>{r.reasons[0] && <div className="text-xs text-ink-3 mt-1">{r.reasons[0]}</div>}</td>
                      <td className="px-3 py-3"><div>{r.claimed_quantity != null ? `${r.claimed_quantity} ${r.unit ?? ''}` : nice(r.latest_claim?.event_type)}</div><div className="font-mono text-xs text-ink-3">{r.latest_claim?.author} · {r.latest_claim?.observed_at?.slice(0, 10)}</div></td>
                      <td className="px-3 py-3">{r.latest_audit ? <><div>{r.audited_quantity != null ? `${r.audited_quantity} ${r.unit ?? ''}` : nice(r.latest_audit.event_type)}</div><div className="font-mono text-xs text-ink-3">{r.latest_audit.author} · {r.latest_audit.observed_at?.slice(0, 10)}</div></> : <span className="text-ink-3">—</span>}</td>
                      <td className={`px-3 py-3 text-right font-mono text-xs ${(r.variance_pct ?? 0) > 10 ? 'text-bad' : 'text-ink-2'}`}>{r.variance_pct == null ? '—' : `${r.variance_pct > 0 ? '+' : ''}${r.variance_pct}%`}</td>
                      <td className="px-5 py-3"><Badge tone={r.audit_status === 'DISCREPANCY' ? 'bad' : r.audit_status === 'CONFIRMED' ? 'ok' : r.audit_status === 'UNAUDITED' ? 'warn' : 'muted'}>{nice(r.audit_status)}</Badge></td>
                    </tr>))}</tbody></table>)}
            </Card>
          )}
          {open === 'gaps' && <Card title={`Evidence gap report · ${gaps.length}`}>{gaps.length === 0 ? <Empty>No gaps.</Empty> : (
            <table className="w-full text-sm"><thead><tr className="text-[11px] tracking-[0.15em] uppercase text-ink-3 border-b border-line"><th className="text-left font-medium px-5 py-3">Activity</th><th className="text-left font-medium px-3 py-3">Status</th><th className="text-left font-medium px-3 py-3">Gap type</th><th className="text-left font-medium px-5 py-3">Critical path</th></tr></thead>
              <tbody>{gaps.map(p => (<tr key={p.activity_id} className="border-b border-line last:border-0"><td className="px-5 py-3 font-mono text-xs">{p.activity_id}</td><td className="px-3 py-3 text-ink-2">{nice(p.status)}</td><td className="px-3 py-3"><Badge tone={p.unverified_event_count ? 'warn' : 'bad'}>{p.unverified_event_count ? `${p.unverified_event_count} unverified` : 'No evidence'}</Badge></td><td className={`px-5 py-3 ${p.is_critical ? 'text-amber' : 'text-ink-3'}`}>{p.is_critical ? 'Yes' : 'No'}</td></tr>))}</tbody></table>)}</Card>}

          {open === 'signals' && <Card title={`Signals · ${signals.length}`}>{signals.length === 0 ? <Empty>None.</Empty> : (
            <ul>{signals.map(s => (<li key={s.signal_id} className="px-5 py-3 border-b border-line last:border-0 flex items-start gap-4 text-sm"><Badge tone={s.severity === 'HIGH' || s.severity === 'CRITICAL' ? 'bad' : 'warn'}>{s.severity}</Badge><div className="flex-1"><div className="text-ink">{s.summary}</div><div className="text-xs text-ink-3 mt-1">{s.recommended_action}</div></div><span className="font-mono text-xs text-ink-3">{s.activity_id}</span></li>))}</ul>)}</Card>}

          {open === 'bench' && <Card title="Productivity benchmarks">{a.benchmarks.length === 0 ? <Empty>Not enough trusted history yet.</Empty> : (
            <table className="w-full text-sm"><thead><tr className="text-[11px] tracking-[0.15em] uppercase text-ink-3 border-b border-line"><th className="text-left font-medium px-5 py-3">Discipline</th><th className="text-left font-medium px-3 py-3">Unit</th><th className="text-right font-medium px-3 py-3">P50 rate / day</th><th className="text-right font-medium px-3 py-3">Samples</th><th className="text-left font-medium px-5 py-3">Status</th></tr></thead>
              <tbody>{a.benchmarks.map((b: any) => (<tr key={b.benchmark_id} className="border-b border-line last:border-0"><td className="px-5 py-3">{nice(b.discipline)}</td><td className="px-3 py-3 text-ink-2">{b.unit_of_measure}</td><td className="px-3 py-3 text-right font-mono text-xs">{b.p50_rate ?? '—'}</td><td className="px-3 py-3 text-right font-mono text-xs">{b.sample_count}</td><td className="px-5 py-3"><Badge tone={b.benchmark_status === 'INSUFFICIENT_SAMPLE' ? 'muted' : 'ok'}>{nice(b.benchmark_status)}</Badge></td></tr>))}</tbody></table>)}</Card>}

          {open === 'patterns' && <Card title="Resolution patterns">{a.patterns.length === 0 ? <Empty>No patterns recorded.</Empty> : (
            <ul>{a.patterns.map((p: any) => (<li key={p.pattern_id} className="px-5 py-3 border-b border-line last:border-0 flex justify-between text-sm"><span>{nice(p.conflict_or_signal_type)}</span><span className="text-ink-3 text-xs font-mono">{p.total_occurrences} seen · {p.resolved_count} resolved · avg {p.avg_resolution_hours} h</span></li>))}</ul>)}</Card>}
        </div>
        <div className="mt-6"><Label>Recent exports</Label><div className="text-sm text-ink-3 mt-2">Exports are generated from the API on demand. None yet.</div></div>
      </div>
    </>
  );
}
