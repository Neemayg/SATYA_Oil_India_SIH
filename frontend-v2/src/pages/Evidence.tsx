import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getQueue, getTrace, getSource, type Trace } from '../services/api';
import { Badge, Card, Empty, Label, PageHeader, Row, Spinner, fmtDate, nice, trustTone, pct } from '../components/ui';
import { cn } from '../lib/utils';

export function Evidence() {
  const { eventId } = useParams();
  const [events, setEvents] = useState<string[]>([]);
  const [trace, setTrace] = useState<Trace | null>(null);
  const [source, setSource] = useState<any>(null);
  const [q, setQ] = useState('');

  useEffect(() => { getQueue().then(qs => setEvents(qs.map(x => x.event_id))).catch(() => setEvents([])); }, []);
  useEffect(() => {
    if (!eventId) return;
    setTrace(null); setSource(null);
    getTrace(eventId).then(async t => { setTrace(t); if (t.execution_event?.source_id) setSource(await getSource(t.execution_event.source_id).catch(() => null)); }).catch(() => setTrace(null));
  }, [eventId]);

  const ev = trace?.execution_event; const ta = trace?.latest_trust_assessment;
  return (
    <>
      <PageHeader title="Evidence Center" subtitle="Source library · trace any claim from raw text to its trust decision" />
      <div className="flex min-h-[calc(100vh-130px)]">
        <aside className="w-[300px] shrink-0 border-r border-line">
          <div className="p-4 border-b border-line">
            <input value={q} onChange={e => setQ(e.target.value)} placeholder="Event ID…" className="w-full bg-surface border border-line rounded-sm px-3 py-1.5 text-sm font-mono focus:outline-none focus:border-ink-3" />
            {q.trim() && <Link to={`/evidence/${q.trim()}`} className="text-xs text-brand mt-2 inline-block">Open {q.trim()}</Link>}
          </div>
          <div className="px-5 py-3 border-b border-line"><Label className="text-ink">Events in review</Label></div>
          {events.length === 0 ? <Empty>No events in review.</Empty> : events.map(id => (
            <Link key={id} to={`/evidence/${id}`} className={cn('block px-5 py-3 font-mono text-xs border-b border-line border-l-2', id === eventId ? 'bg-brand-soft/60 border-l-brand text-ink' : 'border-l-transparent text-ink-2 hover:bg-surface-2')}>{id}</Link>
          ))}
        </aside>

        <section className="flex-1 min-w-0 px-8 py-6">
          {!eventId ? <Empty>Select an event to see its full lineage.</Empty> : !trace ? <Spinner /> : (
            <div className="grid grid-cols-[1fr_360px] gap-5">
              <Card>
                <div className="px-5 py-3 border-b border-line flex items-center gap-3">
                  <span className="font-mono text-sm text-ink">{source?.file_name ?? trace.source_document?.file_name ?? ev?.source_id}</span>
                  <Badge>{nice(source?.source_type ?? trace.source_document?.source_type)}</Badge>
                  <span className="text-xs text-ink-3 ml-auto font-mono">{source?.author ?? trace.source_document?.author} · {fmtDate(source?.submitted_at ?? trace.source_document?.submitted_at)}</span>
                </div>
                <div className="p-5">
                  <pre className="bg-paper text-paper-ink border border-line rounded-sm p-6 text-[13px] font-mono whitespace-pre-wrap leading-relaxed min-h-[320px]">{highlight(trace.source_document?.raw_content ?? '', ev?.extracted_statement ?? '')}</pre>
                </div>
              </Card>

              <div className="flex flex-col gap-5">
                <Card title="Extraction detail">
                  <div className="px-5 py-2">
                    <Row k="Event" v={ev?.event_id} mono />
                    <Row k="Type" v={nice(ev?.event_type)} />
                    <Row k="Discipline" v={nice(ev?.discipline)} />
                    <Row k="Observed" v={fmtDate(ev?.observed_timestamp)} />
                    <Row k="Activity ID" v={ev?.observed_activity_id ?? '—'} mono />
                    <Row k="Quantity" v={ev?.observed_quantity != null ? `${ev.observed_quantity} ${ev.unit_of_measure ?? ''}` : '—'} />
                    <Row k="Extraction confidence" v={pct(ev?.extraction_confidence)} />
                  </div>
                </Card>
                <Card title="Trust">
                  <div className="px-5 py-2">
                    <Row k="State" v={<Badge tone={trustTone(ta?.trust_status)} filled>{nice(ta?.trust_status ?? 'none')}</Badge>} />
                    <Row k="Match confidence" v={pct(ta?.match_confidence)} />
                    <Row k="Evidence support" v={pct(ta?.evidence_support)} />
                    <Row k="Versions" v={String(trace.trust_history?.length ?? 0)} />
                  </div>
                  {ta?.gating_trigger && <p className="px-5 pb-3 text-xs text-ink-3 font-mono">{ta.gating_trigger}</p>}
                  <div className="px-5 pb-4"><Link to={`/reconciliation/${eventId}`} className="text-brand text-sm">Open in Reconciliation →</Link></div>
                </Card>
                {(trace.trust_history?.length ?? 0) > 1 && (
                  <Card title="Audit">
                    <ul>{trace.trust_history.map(h => (
                      <li key={h.assessment_id} className="px-5 py-3 border-b border-line last:border-0 text-xs">
                        <span className="font-mono text-ink-3">v{h.version_index}</span> <Badge tone={trustTone(h.trust_status)}>{nice(h.trust_status)}</Badge>
                        <div className="text-ink-3 mt-1 font-mono">{fmtDate(h.evaluated_at)} · {h.gating_trigger?.split(':')[0]}</div>
                      </li>
                    ))}</ul>
                  </Card>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </>
  );
}

function highlight(text: string, needle: string) {
  if (!needle || !text.includes(needle)) return text;
  const [a, b] = text.split(needle);
  return <>{a}<mark className="bg-[#f7d27a] text-[#1a1a1a] rounded-sm px-0.5">{needle}</mark>{b}</>;
}
