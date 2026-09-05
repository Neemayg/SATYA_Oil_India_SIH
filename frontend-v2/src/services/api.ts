import { apiClient } from './apiClient';

export const PROJECT_ID = 'PRJ-NBG-2026';
export const PLANNER_ID = 'PLN-WEB-01';

export interface QueueItem {
  queue_item_id: string; event_id: string; project_id: string; priority: string;
  trigger_reason: string; match_confidence: number; evidence_support: number;
  latest_trust_version: number; created_at: string;
}
export interface ExecutionEvent {
  event_id: string; source_id: string; event_type: string; observed_timestamp: string | null;
  extracted_statement: string; observed_activity_id: string | null; raw_observed_activity_id: string | null;
  discipline: string; area_location: string | null; observed_quantity: number | null; unit_of_measure: string | null;
  extraction_confidence: number;
}
export interface Candidate {
  activity_id: string; activity_name: string; wbs_name_path: string;
  scores: Record<string, number>; match_reasons: string[];
}
export interface MatchResult {
  match_id: string; outcome: string; selected_activity_id: string | null; selected_activity_name: string | null;
  confidence_score: number; candidates: Candidate[]; reasoning: string[]; evaluated_at: string;
}
export interface TrustAssessment {
  assessment_id: string; version_index: number; trust_status: string; gating_trigger: string;
  match_confidence: number; evidence_support: number; has_critical_conflict: boolean; has_evidence_gaps: boolean;
  rationale_breakdown: Record<string, unknown>; evaluated_at: string;
}
export interface Trace {
  event_id: string; execution_event: ExecutionEvent; source_document: any;
  evidence_assessment: any; latest_trust_assessment: TrustAssessment | null; trust_history: TrustAssessment[]; conflicts: any[];
}
export interface Fingerprint {
  activity_id: string; activity_name: string; discipline: string; wbs_code: string; wbs_name_path: string;
  planned_start: string | null; planned_finish: string | null; is_critical: boolean; area_location: string | null;
  planned_quantity: number | null; unit_of_measure: string | null;
}
export interface ActivityProgress {
  activity_id: string; status: string; physical_progress_pct: number | null; forecast_status: string;
  actual_start: string | null; actual_finish: string | null; forecast_finish: string | null;
  finish_variance_days: number | null; is_critical: boolean; trusted_event_count: number; unverified_event_count: number;
  qa_clearance_status: string;
}
export interface Projection {
  projection_id: string; as_of_date: string; total_activities: number; completed_activities: number;
  in_progress_activities: number; not_started_activities: number; overall_project_progress_pct: number;
  critical_activity_delay_count: number; max_schedule_delay_days: number; unverified_claims_count: number;
  activity_progress: Record<string, ActivityProgress>;
}
export interface Signal {
  signal_id: string; activity_id: string; signal_type: string; severity: string; status: string;
  as_of_date: string; summary: string; recommended_action: string; reasoning: string[];
}

const j = (s: unknown, fb: any) => { if (typeof s !== 'string') return s ?? fb; try { return JSON.parse(s); } catch { return fb; } };

export async function getQueue(): Promise<QueueItem[]> {
  const r = await apiClient.get<any>(`/hitl/queue?project_id=${PROJECT_ID}`);
  return r.queue_items ?? [];
}
export async function getTrace(eventId: string): Promise<Trace> {
  const r = await apiClient.get<any>(`/evidence/events/${eventId}/trace`);
  const lt = r.latest_trust_assessment;
  if (lt) lt.rationale_breakdown = j(lt.rationale_breakdown ?? lt.rationale_breakdown_json, {});
  return r;
}
export async function getMatch(eventId: string): Promise<MatchResult | null> {
  try {
    const r = await apiClient.get<any>(`/matching/events/${eventId}`);
    const m = (r.match_results ?? []).slice(-1)[0];
    if (!m) return null;
    return {
      match_id: m.match_id, outcome: m.outcome, selected_activity_id: m.selected_activity_id,
      selected_activity_name: m.selected_activity_name, confidence_score: m.confidence_score ?? 0,
      candidates: j(m.candidate_matches ?? m.candidate_matches_json, []),
      reasoning: j(m.reasoning_trace ?? m.reasoning_trace_json, []), evaluated_at: m.evaluated_at,
    };
  } catch { return null; }
}
export async function getFingerprints(): Promise<Fingerprint[]> {
  try { const r = await apiClient.get<any>(`/fingerprints/projects/${PROJECT_ID}`); return r.fingerprints ?? []; } catch { return []; }
}
export async function getProjection(): Promise<Projection | null> {
  try {
    const r = await apiClient.get<any>(`/projections/projects/${PROJECT_ID}/latest`);
    return { ...r, activity_progress: j(r.activity_progress ?? r.activity_progress_json, {}) };
  } catch { return null; }
}
export async function getSignals(): Promise<Signal[]> {
  try {
    const r = await apiClient.get<any>(`/monitoring/projects/${PROJECT_ID}/signals`);
    return (r.signals ?? []).map((s: any) => ({ ...s, reasoning: j(s.reasoning_trace ?? s.reasoning_trace_json, []) }));
  } catch { return []; }
}
export async function getEvent(eventId: string): Promise<ExecutionEvent> {
  return apiClient.get<ExecutionEvent>(`/ingestion/events/${eventId}`);
}
export async function getSource(sourceId: string): Promise<any> {
  return apiClient.get<any>(`/ingestion/sources/${sourceId}`);
}
export async function getAnalytics() {
  const [p, c, k] = await Promise.all([
    apiClient.get<any>(`/analytics/projects/${PROJECT_ID}/productivity`).catch(() => ({ benchmarks: [] })),
    apiClient.get<any>(`/analytics/projects/${PROJECT_ID}/contractors`).catch(() => ({ profiles: [] })),
    apiClient.get<any>(`/analytics/projects/${PROJECT_ID}/conflicts`).catch(() => ({ patterns: [] })),
  ]);
  return { benchmarks: p.benchmarks ?? [], contractors: c.profiles ?? c.contractors ?? [], patterns: k.patterns ?? [] };
}

export interface AuditActivity {
  activity_id: string; activity_name: string; discipline: string | null; is_critical: boolean; unit: string | null;
  worker_claim_count: number; audit_count: number; claimed_quantity: number | null; audited_quantity: number | null;
  variance_pct: number | null; audit_status: 'DISCREPANCY' | 'UNAUDITED' | 'AUDIT_ONLY' | 'CONFIRMED'; reasons: string[];
  latest_claim: { author: string; observed_at: string; statement: string; event_type: string } | null;
  latest_audit: { author: string; observed_at: string; statement: string; event_type: string } | null;
}
export interface AuditReport {
  generated_at: string; activities: AuditActivity[];
  summary: { activities_with_claims: number; activities_audited: number; audit_coverage_pct: number; confirmed: number; discrepancies: number; unaudited: number; avg_over_reporting_pct: number; total_worker_claims: number; total_audits: number };
}
export async function getAudit(): Promise<AuditReport | null> {
  try { return await apiClient.get<AuditReport>(`/audit/projects/${PROJECT_ID}`); } catch { return null; }
}

export type DecisionType = 'VALIDATE' | 'CHANGE_MATCH' | 'REJECT' | 'REQUEST_EVIDENCE' | 'DEFER';
export async function submitDecision(p: {
  event_id: string; decision_type: DecisionType; reviewed_trust_version: number; reviewed_match_result_id?: string;
  selected_activity_id?: string; reason_notes?: string; override_reason_category?: string; requested_evidence_types?: string[];
}) {
  return apiClient.post<any>('/hitl/decisions', { planner_id: PLANNER_ID, reviewed_evidence_assessment_id: '', ...p });
}
export async function uploadText(content: string, sourceType = 'SUPERVISOR_NOTE', fileName = 'web_upload.txt') {
  return apiClient.post<any>('/ingestion/upload', { project_id: PROJECT_ID, source_type: sourceType, file_name: fileName, content });
}
export async function runMonitoring() {
  return apiClient.post<any>('/monitoring/evaluate', { project_id: PROJECT_ID, as_of_date: new Date().toISOString().slice(0, 10) });
}
export async function generateProjection() {
  return apiClient.post<any>('/projections/generate', { project_id: PROJECT_ID });
}
