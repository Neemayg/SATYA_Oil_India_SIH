import { Observation, Settings, Activity, AuditReport } from './types';

const base = (s: Settings) => s.serverUrl.replace(/\/+$/, '');

async function req(url: string, init?: RequestInit, ms = 15000) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), ms);
  try {
    const res = await fetch(url, { ...init, signal: ctl.signal });
    const text = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${text.slice(0, 140)}`);
    return JSON.parse(text);
  } finally { clearTimeout(t); }
}

/** Builds the DPR-style sentence the SATYA extractor understands. */
export function buildStatement(o: Observation): string {
  const verb = o.type === 'COMPLETION' ? 'completed' : o.type === 'ISSUE' ? 'halted' : 'in progress';
  const parts: string[] = [];
  if (o.activityId) parts.push(`${o.activityId.toUpperCase()}:`);
  if (o.isAudit) parts.push('Manager audit verified:');
  const note = o.note.trim();
  parts.push(note || `${o.activityName || o.discipline.toLowerCase() + ' work'} ${verb}`);
  if (o.quantity && o.unit) parts.push(`${o.quantity} ${o.unit}`);
  if (o.area && !note.toLowerCase().includes(o.area.toLowerCase())) parts.push(`at ${o.area}`);
  if (o.photoUri) parts.push('[site photo attached]');
  if (o.audioUri) parts.push('[voice note attached]');
  let s = parts.join(' ').replace(/\s+/g, ' ').trim();
  if (!/[.!?]$/.test(s)) s += '.';
  return s;
}

export async function checkHealth(s: Settings): Promise<boolean> {
  try { await req(`${base(s)}/api/v1/health`, undefined, 5000); return true; } catch { return false; }
}

export async function fetchActivities(s: Settings): Promise<Activity[]> {
  const json = await req(`${base(s)}/api/v1/fingerprints/projects/${encodeURIComponent(s.projectId)}`, undefined, 10000);
  const list = (json.fingerprints ?? json.data?.fingerprints ?? []) as any[];
  return list.map(f => ({
    activity_id: f.activity_id, activity_name: f.activity_name, discipline: f.discipline,
    area_location: f.area_location, wbs_code: f.wbs_code, planned_start: f.planned_start,
    planned_finish: f.planned_finish, is_critical: !!f.is_critical, unit_of_measure: f.unit_of_measure,
  }));
}

export async function uploadObservation(o: Observation, s: Settings) {
  const json = await req(`${base(s)}/api/v1/ingestion/upload`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: o.projectId || s.projectId,
      source_type: o.isAudit ? 'MANAGER_AUDIT' : o.audioUri ? 'VOICE_TRANSCRIPT' : 'SUPERVISOR_NOTE',
      file_name: `${o.isAudit ? 'audit' : 'field'}_${o.id}.txt`,
      author: o.author || s.name || (o.isAudit ? 'Site Manager' : 'Field Engineer'),
      content: buildStatement(o),
      observed_timestamp: o.observedAt.slice(0, 10),
    }),
  });
  const d = json.data ?? json;
  const events = (d.events_extracted ?? []) as any[];
  return { sourceId: d.source_id as string | undefined, eventIds: events.map(e => e.event_id as string) };
}

export async function fetchAudit(s: Settings): Promise<AuditReport> {
  return req(`${base(s)}/api/v1/audit/projects/${encodeURIComponent(s.projectId)}`, undefined, 15000);
}

/** Pull match + trust state for a synced observation's first event. */
export async function fetchEventStatus(eventId: string, s: Settings) {
  const out: Partial<Observation> = {};
  try {
    const m = await req(`${base(s)}/api/v1/matching/events/${eventId}`, undefined, 8000);
    const r = (m.match_results ?? m.data?.match_results ?? [])[0];
    if (r) { out.matchOutcome = r.outcome; out.matchActivityId = r.selected_activity_id ?? undefined; out.matchConfidence = r.confidence_score; }
  } catch {}
  try {
    const t = await req(`${base(s)}/api/v1/evidence/events/${eventId}/trust`, undefined, 8000);
    const ta = t.latest_trust_assessment ?? t.data?.latest_trust_assessment ?? t.trust_assessment ?? t;
    if (ta?.trust_status) out.trustStatus = ta.trust_status;
  } catch {}
  return out;
}
