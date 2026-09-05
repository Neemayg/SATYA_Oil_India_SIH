export type ObservationType = 'PROGRESS' | 'ISSUE' | 'COMPLETION';
export type SyncStatus = 'DRAFT' | 'PENDING' | 'SYNCED' | 'FAILED';
export type Role = 'FIELD' | 'MANAGER';

export interface Activity {
  activity_id: string;
  activity_name: string;
  discipline: string;
  area_location?: string | null;
  wbs_code?: string;
  planned_start?: string | null;
  planned_finish?: string | null;
  is_critical?: boolean;
  unit_of_measure?: string | null;
}

export interface Observation {
  id: string;
  projectId: string;
  activityId?: string;
  activityName?: string;
  type: ObservationType;
  discipline: string;
  area: string;
  note: string;
  quantity?: string;
  unit?: string;
  photoUri?: string;
  audioUri?: string;
  observedAt: string;   // ISO datetime
  createdAt: string;
  syncStatus: SyncStatus;
  isAudit?: boolean;    // submitted in Manager mode
  author?: string;
  syncError?: string;
  serverSourceId?: string;
  serverEventIds?: string[];
  matchOutcome?: string;
  matchActivityId?: string;
  matchConfidence?: number;
  trustStatus?: string;
}

export interface Settings {
  signedIn: boolean;
  name: string;
  crew: string;
  role: Role;
  projectId: string;
  serverUrl: string;
}

/** Server-side comparison of worker claims vs manager audits. */
export interface AuditRecord {
  event_id: string; event_type: string; quantity: number | null; unit: string | null;
  observed_at: string; statement: string; author: string; source_type: string;
}
export type AuditStatus = 'DISCREPANCY' | 'UNAUDITED' | 'AUDIT_ONLY' | 'CONFIRMED';
export interface AuditActivity {
  activity_id: string; activity_name: string; discipline: string | null; is_critical: boolean;
  planned_quantity: number | null; unit: string | null; planned_finish: string | null;
  worker_claim_count: number; audit_count: number;
  latest_claim: AuditRecord | null; latest_audit: AuditRecord | null;
  claimed_quantity: number | null; audited_quantity: number | null; variance_pct: number | null;
  audit_status: AuditStatus; reasons: string[]; days_since_audit: number | null;
}
export interface AuditReport {
  project_id: string; generated_at: string;
  summary: {
    activities_with_claims: number; activities_audited: number; audit_coverage_pct: number;
    confirmed: number; discrepancies: number; unaudited: number; audit_only: number;
    avg_over_reporting_pct: number; total_worker_claims: number; total_audits: number;
  };
  activities: AuditActivity[];
}

export const TYPE_LABEL: Record<ObservationType, string> = { PROGRESS: 'Progress Note', ISSUE: 'Issue', COMPLETION: 'Completion' };
export const AUDIT_TYPE_LABEL: Record<ObservationType, string> = { PROGRESS: 'Still in progress', ISSUE: 'Problem found', COMPLETION: 'Verified complete' };

export const DISCIPLINES = ['CIVIL', 'PIPING', 'STRUCTURAL', 'MECHANICAL', 'ELECTRICAL', 'INSTRUMENTATION', 'QA_QC', 'SAFETY_HSE'];
export const UNITS = ['Meters', 'Joints', 'Spools', 'Cu.M', 'Sq.M', 'MT', 'Nos', 'Loops', '%'];
