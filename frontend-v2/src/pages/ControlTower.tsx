import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { getProjection, getQueue, getSignals, getFingerprints, runMonitoring, generateProjection, type Projection, type QueueItem, type Signal, type Fingerprint } from '../services/api';
import { Button, Card, Empty, Label, PageHeader, Spinner, nice } from '../components/ui';

export function ControlTower() {
  const [proj, setProj] = useState<Projection | null>(null);
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [fps, setFps] = useState<Fingerprint[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  async function load() {
    setLoading(true);
    const [p, q, s, f] = await Promise.all([getProjection(), getQueue().catch(() => []), getSignals(), getFingerprints()]);
    setProj(p); setQueue(q); setSignals(s); setFps(f); setLoading(false);
  }
  useEffect(() => { load(); }, []);
  async function recompute() { setBusy(true); try { await generateProjection(); await runMonitoring(); } catch {} await load(); setBusy(false); }

  if (loading) return <Spinner />;
  const names = Object.fromEntries(fps.map(f => [f.activity_id, f.activity_name]));
  const active = signals.filter(s => s.status === 'ACTIVE');
  const high = active.filter(s => s.severity === 'HIGH' || s.severity === 'CRITICAL');
  const acts = Object.values(proj?.activity_progress ?? {});
  const trusted = acts.reduce((n, a) => n + (a.trusted_event_count ?? 0), 0);
  const unverified = proj?.unverified_claims_count ?? 0;
  const byDisc = Object.entries(fps.reduce<Record<string, { observed: number; trusted: number }>>((m, f) => {
    const p = proj?.activity_progress?.[f.activity_id];
    const d = nice(f.discipline);
    m[d] = m[d] ?? { observed: 0, trusted: 0 };
    m[d].observed += (p?.unverified_event_count ?? 0) + (p?.trusted_event_count ?? 0);
    m[d].trusted += p?.trusted_event_count ?? 0;
    return m;
  }, {})).map(([name, v]) => ({ name, ...v }));
  const health = proj ? Math.round(100 - Math.min(100, (proj.critical_activity_delay_count / Math.max(1, proj.total_activities)) * 100)) : 0;

  return (
    <>
      <PageHeader title="Control Tower" subtitle={`Project-wide execution status · as of ${proj?.as_of_date ?? 'today'}`}
        action={<Button variant="secondary" onClick={recompute} disabled={busy}><RefreshCw className={busy ? 'w-4 h-4 animate-spin' : 'w-4 h-4'} />Recompute</Button>} />

      <div className="px-8 py-6">
        <div className="grid grid-cols-5 border border-line rounded-md divide-x divide-line bg-surface">
          <Cell label="Activities tracked" value={proj?.total_activities ?? fps.length} hint={`across ${byDisc.length} disciplines`} />
          <Cell label="Trusted events" value={trusted} tone="text-ok" hint={`${Math.round(proj?.overall_project_progress_pct ?? 0)}% physical progress`} />
          <Cell label="Awaiting review" value={queue.length} tone={queue.length ? 'text-amber' : 'text-ink'} hint="planner decision queue" />
          <Cell label="Unverified claims" value={unverified} tone={unverified ? 'text-bad' : 'text-ink'} hint="excluded from progress" />
          <Cell label="Schedule health" value={`${health}%`} tone={health >= 90 ? 'text-ok' : health >= 70 ? 'text-amber' : 'text-bad'} hint={`${proj?.critical_activity_delay_count ?? 0} critical delayed`} />
        </div>

        <div className="grid grid-cols-[1fr_360px] gap-5 mt-5">
          <div className="flex flex-col gap-5">
            <Card>
              <div className="px-5 pt-5">
                <Label className="text-ink">Execution lineage throughput</Label>
                <div className="text-xs text-ink-3 mt-1">Observed vs trusted events by discipline</div>
              </div>
              <div className="h-56 px-3 pb-3 mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={byDisc} barCategoryGap={18}>
                    <XAxis dataKey="name" tick={{ fill: 'var(--color-ink-3)', fontSize: 11 }} axisLine={{ stroke: 'var(--color-line)' }} tickLine={false} />
                    <Tooltip cursor={{ fill: 'var(--color-surface-2)' }} contentStyle={{ background: 'var(--color-surface)', border: '1px solid var(--color-line)', borderRadius: 4, fontSize: 12 }} labelStyle={{ color: 'var(--color-ink)' }} />
                    <Bar dataKey="observed" name="Observed" stackId="a" fill="var(--color-chart-muted)" />
                    <Bar dataKey="trusted" name="Trusted" stackId="a" fill="var(--color-ok)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="px-5 pb-4 flex gap-5 text-xs text-ink-3"><span><i className="inline-block w-2 h-2 rounded-full bg-chart-muted mr-1.5" />Observed</span><span><i className="inline-block w-2 h-2 rounded-full bg-ok mr-1.5" />Trusted</span></div>
            </Card>

            <Card>
              <div className="px-5 pt-5 pb-3">
                <Label className="text-ink">Critical path at risk</Label>
                <div className="text-xs text-ink-3 mt-1">Activities requiring supervisor attention</div>
              </div>
              {high.length === 0 ? <Empty>No critical path warnings.</Empty> : (
                <table className="w-full text-sm">
                  <thead><tr className="text-[11px] tracking-[0.15em] uppercase text-ink-3 border-b border-line"><th className="text-left font-medium px-5 py-2">Activity ID</th><th className="text-left font-medium px-3 py-2">Activity</th><th className="text-left font-medium px-3 py-2">Signal</th><th className="px-5 py-2" /></tr></thead>
                  <tbody>{high.slice(0, 6).map(s => (
                    <tr key={s.signal_id} className="border-b border-line last:border-0">
                      <td className="px-5 py-3 font-mono text-xs text-ink-2">{s.activity_id}</td>
                      <td className="px-3 py-3 text-ink">{names[s.activity_id] ?? '—'}</td>
                      <td className="px-3 py-3"><span className="text-bad text-[11px] tracking-[0.12em] uppercase">{nice(s.signal_type)}</span></td>
                      <td className="px-5 py-3 text-right"><Link to="/schedule" className="text-ink-2 hover:text-ink">View</Link></td>
                    </tr>
                  ))}</tbody>
                </table>
              )}
            </Card>
          </div>

          <div className="flex flex-col gap-5">
            <Card>
              <div className="px-5 pt-5 pb-2"><Label className="text-ink">Decision queue</Label><div className="text-xs text-ink-3 mt-1">Items awaiting reconciliation</div></div>
              <div className="px-5">
                {groupBy(queue, q => q.trigger_reason).map(([k, n]) => (
                  <div key={k} className="flex justify-between items-center py-3 border-b border-line last:border-0">
                    <span className="text-[11px] tracking-[0.15em] uppercase text-amber">{nice(k)}</span><span className="font-mono font-semibold text-amber">{String(n).padStart(2, '0')}</span>
                  </div>
                ))}
                {queue.length === 0 && <div className="py-3 text-sm text-ink-3">Queue is empty.</div>}
              </div>
              <div className="p-5"><Link to="/reconciliation"><Button className="w-full justify-center">Go to Reconciliation Desk</Button></Link></div>
            </Card>

            <Card>
              <div className="px-5 pt-5 pb-2"><Label className="text-ink">Recent activity</Label><div className="text-xs text-ink-3 mt-1">Latest execution lineage events</div></div>
              <ul className="px-5 pb-3">
                {active.slice(0, 5).map(s => (
                  <li key={s.signal_id} className="py-3 border-b border-line last:border-0">
                    <div className="font-mono text-[11px] text-ink-3">{s.as_of_date}</div>
                    <div className="text-sm text-ink mt-1 leading-snug">{s.summary}</div>
                  </li>
                ))}
                {active.length === 0 && <li className="py-3 text-sm text-ink-3">Nothing yet.</li>}
              </ul>
            </Card>

            <Card>
              <div className="px-5 pt-5 pb-2"><Label className="text-ink">Sources health</Label></div>
              <ul className="px-5 pb-4">
                {[['Daily Progress Reports', true], ['Field Capture App', true], ['Primavera P6 Schedule Feed', fps.length > 0]].map(([n, ok]) => (
                  <li key={String(n)} className="flex justify-between items-center py-2.5 border-b border-line last:border-0 text-sm">
                    <span className="flex items-center gap-2 text-ink"><i className={`w-2 h-2 rounded-full ${ok ? 'bg-ok' : 'bg-amber'}`} />{n}</span>
                    <span className={`text-xs ${ok ? 'text-ok' : 'text-amber'}`}>{ok ? 'Synced' : 'Delayed'}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}

function Cell({ label, value, hint, tone = 'text-ink' }: { label: string; value: string | number; hint: string; tone?: string }) {
  return <div className="px-6 py-5"><Label>{label}</Label><div className={`text-3xl font-semibold mt-2 tabular-nums ${tone}`}>{value}</div><div className={`text-xs mt-1 ${tone === 'text-ink' ? 'text-ink-3' : tone}`}>{hint}</div></div>;
}
function groupBy<T>(arr: T[], key: (t: T) => string): [string, number][] {
  const m = new Map<string, number>(); arr.forEach(a => m.set(key(a), (m.get(key(a)) ?? 0) + 1));
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
}
