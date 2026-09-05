import { Observation, Settings } from './types';

/** Builds the DPR-style sentence the SATYA extractor understands. */
export function buildStatement(o: Observation): string {
  const parts: string[] = [];
  if (o.activityId) parts.push(`${o.activityId.toUpperCase()}:`);
  parts.push(o.statement.trim());
  if (o.quantity && o.unit) parts.push(`${o.quantity} ${o.unit}`);
  if (o.location) parts.push(`at ${o.location}`);
  if (o.photoUri) parts.push('[photo evidence attached]');
  if (o.audioUri) parts.push('[voice note attached]');
  return parts.join(' ').replace(/\s+/g, ' ').trim() + '.';
}

export async function uploadObservation(o: Observation, s: Settings) {
  const base = s.serverUrl.replace(/\/+$/, '');
  const payload = {
    project_id: o.projectId || s.projectId,
    source_type: o.audioUri ? 'VOICE_TRANSCRIPT' : 'SUPERVISOR_NOTE',
    file_name: `field_${o.id}.txt`,
    content: buildStatement(o),
    observed_timestamp: o.observedAt,
  };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const res = await fetch(`${base}/api/v1/ingestion/upload`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    const text = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${text.slice(0, 120)}`);
    const json = JSON.parse(text);
    const data = json.data ?? json;
    return {
      sourceId: data.source_id as string | undefined,
      eventsExtracted: (data.events_extracted?.length ?? data.events_count ?? data.event_count) as number | undefined,
    };
  } finally {
    clearTimeout(timer);
  }
}

export async function checkHealth(s: Settings): Promise<boolean> {
  try {
    const res = await fetch(`${s.serverUrl.replace(/\/+$/, '')}/api/v1/health`);
    return res.ok;
  } catch {
    return false;
  }
}
