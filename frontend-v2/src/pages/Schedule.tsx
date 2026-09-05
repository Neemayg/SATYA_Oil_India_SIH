import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { getFingerprints, getProjection, type Fingerprint, type ActivityProgress } from '../services/api';
import { Badge, Card, Empty, PageHeader, Spinner, fmtDate, nice } from '../components/ui';
import { cn } from '../lib/utils';

type Filter = 'ALL' | 'CRITICAL' | 'SLIPPING' | 'UNVERIFIED';

export function Schedule() {
  const [fps, setFps] = useState<Fingerprint[]>([]);
  const [prog, setProg] = useState<Record<string, ActivityProgress>>({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>('ALL');
  const [q, setQ] = useState('');
  const [open, setOpen] = useState<string | null>(null);

  useEffect(() => { (async () => { const [f, p] = await Promise.all([getFingerprints(), getProjection()]); setFps(f); setProg(p?.activity_progress ?? {}); setLoading(false); })(); }, []);

  const rows = useMemo(() => fps.filter(f => {
    const p = prog[f.activity_id];
    if (filter === 'CRITICAL' && !f.is_critical) return false;
    if (filter === 'SLIPPING' && !((p?.finish_variance_days ?? 0) > 0)) return false;
    if (filter === 'UNVERIFIED' && !(p?.unverified_event_count)) return false;
    const t = q.trim().toLowerCase();
    return !t || f.activity_id.toLowerCase().includes(t) || f.activity_name.toLowerCase().includes(t) || f.wbs_name_path.toLowerCase().includes(t);
  }), [fps, prog, filter, q]);

  const counts = { SLIPPING: fps.filter(f => (prog[f.activity_id]?.finish_variance_days ?? 0) > 0).length, UNVERIFIED: fps.filter(f => prog[f.activity_id]?.unverified_event_count).length };
  if (loading) return <Spinner />;

  const statusOf = (p?: ActivityProgress): { t: string; tone: 'ok' | 'warn' | 'bad' | 'muted' | 'brand' } =>
    p?.status === 'COMPLETED' ? { t: 'Trusted', tone: 'ok' } : p?.unverified_event_count ? { t: 'Unverified', tone: 'warn' } : p?.status === 'IN_PROGRESS' ? { t: 'In progress', tone: 'brand' } : { t: 'Not started', tone: 'muted' };

  return (
    <>
      <PageHeader title="Schedule Explorer" subtitle={`North Basin Gas Expansion · WBS view · ${fps.length} activities`} />
      <div className="px-8 py-4 border-b border-line flex items-center gap-6 text-sm">
        {([['ALL', 'All disciplines'], ['CRITICAL', 'Critical path only'], ['SLIPPING', `Slipping (${counts.SLIPPING})`], ['UNVERIFIED', `Unverified (${counts.UNVERIFIED})`]] as [Filter, string][]).map(([f, l]) => (
          <button key={f} onClick={() => setFilter(f)} className={cn('transition-colors', filter === f ? 'text-ink font-medium' : 'text-ink-3 hover:text-ink-2')}>{l}</button>
        ))}
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search activity, ID, WBS…"
          className="ml-auto w-72 bg-surface border border-line rounded-sm px-3 py-1.5 text-sm font-mono focus:outline-none focus:border-ink-3" />
      </div>

      <div className="px-8 py-6">
        <Card>
          {rows.length === 0 ? <Empty>No activities match.</Empty> : (
            <table className="w-full text-sm">
              <thead><tr className="text-[11px] tracking-[0.15em] uppercase text-ink-3 border-b border-line">
                <th className="text-left font-medium px-5 py-3">WBS</th><th className="text-left font-medium px-3 py-3">Activity</th><th className="text-left font-medium px-3 py-3">Planned start</th><th className="text-left font-medium px-3 py-3">Planned finish</th><th className="text-left font-medium px-3 py-3">Actual finish</th><th className="text-left font-medium px-3 py-3">Variance</th><th className="text-left font-medium px-3 py-3">Status</th><th className="text-left font-medium px-3 py-3">Critical</th><th className="px-5" />
              </tr></thead>
              <tbody>
                {rows.map(f => {
                  const p = prog[f.activity_id]; const v = p?.finish_variance_days; const isOpen = open === f.activity_id; const st = statusOf(p);
                  return (<>
                    <tr key={f.activity_id} onClick={() => setOpen(isOpen ? null : f.activity_id)} className={cn('border-b border-line cursor-pointer', isOpen ? 'bg-brand-soft/60' : 'hover:bg-surface-2')}>
                      <td className="px-5 py-4 font-mono text-xs text-ink-2">{f.wbs_code}</td>
                      <td className="px-3 py-4"><div className="font-mono text-xs text-ink-2">{f.activity_id}</div><div className="text-ink mt-1">{f.activity_name}</div><div className="text-xs text-ink-3 mt-1">{nice(f.discipline)}</div></td>
                      <td className="px-3 py-4 font-mono text-xs">{fmtDate(f.planned_start)}</td>
                      <td className="px-3 py-4 font-mono text-xs">{fmtDate(f.planned_finish)}</td>
                      <td className="px-3 py-4 font-mono text-xs text-ink-2">{p?.actual_finish ? fmtDate(p.actual_finish) : p?.unverified_event_count ? 'Unconfirmed' : 'Pending'}</td>
                      <td className={cn('px-3 py-4 font-mono text-xs', (v ?? 0) > 0 ? 'text-bad' : (v ?? 0) < 0 ? 'text-ok' : 'text-ink-3')}>{v == null ? '—' : v > 0 ? `-${v} days` : v < 0 ? `${-v} days early` : 'On time'}</td>
                      <td className="px-3 py-4"><Badge tone={st.tone} filled>{st.t}</Badge></td>
                      <td className="px-3 py-4">{f.is_critical ? 'Yes' : 'No'}</td>
                      <td className="px-5 py-4 text-ink-3">›</td>
                    </tr>
                    {isOpen && (
                      <tr key={f.activity_id + '-d'} className="bg-surface-2 border-b border-line">
                        <td colSpan={9} className="px-5 py-5">
                          <div className="grid grid-cols-4 gap-6 text-sm">
                            <D k="WBS path" v={f.wbs_name_path} />
                            <D k="Planned quantity" v={f.planned_quantity ? `${f.planned_quantity} ${f.unit_of_measure ?? ''}` : '—'} />
                            <D k="Physical progress" v={`${Math.round(p?.physical_progress_pct ?? 0)}%`} />
                            <D k="Forecast finish" v={`${fmtDate(p?.forecast_finish)} · ${nice(p?.forecast_status ?? 'n/a')}`} />
                            <D k="Trusted events" v={String(p?.trusted_event_count ?? 0)} />
                            <D k="Unverified events" v={String(p?.unverified_event_count ?? 0)} />
                            <D k="QA clearance" v={nice(p?.qa_clearance_status ?? 'n/a')} />
                            <div className="self-end"><Link to="/reconciliation" className="text-brand text-sm underline underline-offset-4">View in Reconciliation</Link></div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>);
                })}
              </tbody>
            </table>
          )}
          <div className="px-5 py-3 text-xs text-ink-3 border-t border-line">Showing {rows.length} of {fps.length} activities</div>
        </Card>
      </div>
    </>
  );
}
function D({ k, v }: { k: string; v: string }) { return <div><div className="text-[11px] tracking-[0.15em] uppercase text-ink-3">{k}</div><div className="text-ink mt-1">{v}</div></div>; }
