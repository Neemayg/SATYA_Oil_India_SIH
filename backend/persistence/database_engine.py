"""
SATYA Database Engine
Lightweight, ACID-compliant SQLite persistence engine for local development.
Implements append-only event ledger tables and audit logs.
"""

import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from backend.models.domain_models import (
    SourceDocument, SourceFragment, ExecutionEvent,
    ProvenanceRecord, QuarantineRecord, ActivityFingerprint, MatchResult,
    Evidence, EvidenceClaim, EvidenceReliabilityAssessment, EvidenceAssessment,
    ConflictFlag, TrustAssessment, ValidationDecision, PlannerCorrectionRecord,
    MemoryDistillationRun, TerminologyAliasRecord, ExecutionRateBenchmark,
    ContractorReportingProfile, ConflictResolutionPattern
)

class DatabaseEngine:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._mem_conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._mem_conn:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates schema tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Source Documents Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_documents (
                    source_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    sha256_hash TEXT NOT NULL UNIQUE,
                    raw_content TEXT NOT NULL,
                    submitted_at TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    author TEXT,
                    reporting_period TEXT,
                    extraction_status TEXT NOT NULL,
                    metadata_json TEXT
                )
            """)

            # Activity Fingerprints Table (Phase 6)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_fingerprints (
                    fingerprint_id TEXT PRIMARY KEY,
                    activity_id TEXT NOT NULL UNIQUE,
                    project_id TEXT NOT NULL,
                    activity_name TEXT NOT NULL,
                    normalized_name TEXT NOT NULL,
                    wbs_id TEXT NOT NULL,
                    wbs_code TEXT NOT NULL,
                    wbs_name_path TEXT NOT NULL,
                    discipline TEXT NOT NULL,
                    area_location TEXT,
                    equipment_tag TEXT,
                    line_number TEXT,
                    start_km REAL,
                    end_km REAL,
                    planned_start TEXT,
                    planned_finish TEXT,
                    baseline_duration_days INTEGER,
                    planned_quantity REAL,
                    unit_of_measure TEXT,
                    is_critical INTEGER,
                    predecessors_json TEXT,
                    successors_json TEXT,
                    action_verbs_json TEXT,
                    entity_nouns_json TEXT,
                    synonyms_json TEXT,
                    field_aliases_json TEXT,
                    search_tokens_json TEXT,
                    fingerprint_version TEXT NOT NULL
                )
            """)

            # Match Results Table (Phase 7)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS match_results (
                    match_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    selected_activity_id TEXT,
                    selected_activity_name TEXT,
                    confidence_score REAL NOT NULL,
                    top_candidate_json TEXT,
                    candidate_matches_json TEXT,
                    reasoning_trace_json TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES execution_events (event_id)
                )
            """)

            # Source Fragments Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_fragments (
                    fragment_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    fragment_index INTEGER NOT NULL,
                    raw_text TEXT NOT NULL,
                    normalized_text TEXT NOT NULL,
                    locator_type TEXT NOT NULL,
                    locator_value TEXT NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES source_documents (source_id)
                )
            """)

            # Execution Events Ledger Table (Append-Only)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_events (
                    event_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    fragment_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    observed_timestamp TEXT,
                    source_timestamp TEXT NOT NULL,
                    extracted_statement TEXT NOT NULL,
                    raw_observed_activity_id TEXT,
                    observed_activity_id TEXT,
                    activity_id_validation_status TEXT NOT NULL,
                    temporal_resolution_status TEXT NOT NULL,
                    temporal_resolution_basis TEXT,
                    discipline TEXT NOT NULL,
                    area_location TEXT,
                    equipment_tag TEXT,
                    line_number TEXT,
                    observed_quantity REAL,
                    unit_of_measure TEXT,
                    progress_percent REAL,
                    status_text TEXT,
                    extraction_confidence REAL NOT NULL,
                    lifecycle_state TEXT NOT NULL,
                    shift_context TEXT,
                    pending_qa_clearance INTEGER,
                    remaining_quantity REAL,
                    work_front_tag TEXT,
                    quarantine_reasons_json TEXT,
                    FOREIGN KEY (source_id) REFERENCES source_documents (source_id)
                )
            """)

            # Provenance Records Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS provenance_records (
                    provenance_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    locator_type TEXT NOT NULL,
                    locator_value TEXT NOT NULL,
                    raw_text_snippet TEXT NOT NULL,
                    field_provenance_map_json TEXT,
                    FOREIGN KEY (event_id) REFERENCES execution_events (event_id)
                )
            """)

            # Quarantine Records Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quarantine_records (
                    quarantine_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    event_id TEXT,
                    failure_stage TEXT NOT NULL,
                    quarantine_reasons_json TEXT NOT NULL,
                    raw_payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Evidence Ledger Table (Phase 8 Append-Only)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence_ledger (
                    evidence_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    fragment_id TEXT NOT NULL,
                    locator_type TEXT NOT NULL,
                    locator_value TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    origin_group_id TEXT NOT NULL,
                    raw_text_snippet TEXT NOT NULL,
                    observed_timestamp TEXT,
                    provenance_map_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES execution_events (event_id)
                )
            """)

            # Evidence Claims Table (Phase 8)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence_claims (
                    claim_id TEXT PRIMARY KEY,
                    evidence_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    claim_type TEXT NOT NULL,
                    raw_statement TEXT NOT NULL,
                    claim_value_json TEXT,
                    unit TEXT,
                    normalized_value REAL,
                    confidence REAL NOT NULL,
                    FOREIGN KEY (evidence_id) REFERENCES evidence_ledger (evidence_id)
                )
            """)

            # Evidence Assessments Table (Phase 8)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence_assessments (
                    assessment_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    evidence_ids_json TEXT NOT NULL,
                    claim_ids_json TEXT NOT NULL,
                    corroboration_status TEXT NOT NULL,
                    unique_origin_count INTEGER NOT NULL,
                    evidence_support_score REAL NOT NULL,
                    reliability_assessments_json TEXT NOT NULL,
                    evidence_gaps_json TEXT NOT NULL,
                    reasoning_trace_json TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES execution_events (event_id)
                )
            """)

            # Conflict Flags Table (Phase 8 Versioned Ledger)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conflict_flags (
                    conflict_id TEXT NOT NULL,
                    conflict_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    involved_event_ids_json TEXT NOT NULL,
                    involved_claim_ids_json TEXT NOT NULL,
                    involved_evidence_ids_json TEXT NOT NULL,
                    description TEXT NOT NULL,
                    snippet_comparison_json TEXT NOT NULL,
                    version_index INTEGER NOT NULL,
                    resolution_status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (conflict_id, version_index)
                )
            """)

            # Trust Assessments Table (Phase 8 Append-Only Versioned Ledger)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trust_assessments (
                    assessment_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    version_index INTEGER NOT NULL,
                    match_confidence REAL NOT NULL,
                    evidence_support REAL NOT NULL,
                    trust_status TEXT NOT NULL,
                    gating_trigger TEXT NOT NULL,
                    rationale_breakdown_json TEXT NOT NULL,
                    has_critical_conflict INTEGER NOT NULL,
                    has_evidence_gaps INTEGER NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    PRIMARY KEY (event_id, version_index)
                )
            """)

            # Validation Decisions Table (Phase 9 Append-Only Audit Ledger)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_decisions (
                    decision_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    planner_id TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    reviewed_trust_version INTEGER NOT NULL,
                    reviewed_match_result_id TEXT NOT NULL,
                    reviewed_evidence_assessment_id TEXT NOT NULL,
                    selected_activity_id TEXT,
                    previous_trust_version INTEGER NOT NULL,
                    resulting_trust_version INTEGER NOT NULL,
                    resulting_trust_status TEXT NOT NULL,
                    override_reason_category TEXT,
                    reason_notes TEXT,
                    evidence_reviewed_ids_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES execution_events (event_id)
                )
            """)

            # Planner Corrections Table (Phase 9 Institutional Memory Hook for Phase 14)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS planner_corrections (
                    correction_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    original_activity_id TEXT,
                    corrected_activity_id TEXT NOT NULL,
                    original_match_result_id TEXT NOT NULL,
                    validation_decision_id TEXT NOT NULL,
                    reason_category TEXT NOT NULL,
                    reason_notes TEXT,
                    planner_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES execution_events (event_id),
                    FOREIGN KEY (validation_decision_id) REFERENCES validation_decisions (decision_id)
                )
            """)

            # Schedule Projections Table (Phase 10 Calculated Progress Layer)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedule_projections (
                    projection_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    as_of_date TEXT NOT NULL,
                    total_activities INTEGER NOT NULL,
                    completed_activities INTEGER NOT NULL,
                    in_progress_activities INTEGER NOT NULL,
                    not_started_activities INTEGER NOT NULL,
                    overall_project_progress_pct REAL,
                    critical_activity_delay_count INTEGER NOT NULL,
                    max_schedule_delay_days REAL NOT NULL,
                    unverified_claims_count INTEGER NOT NULL,
                    activity_progress_json TEXT NOT NULL,
                    wbs_progress_json TEXT NOT NULL,
                    generated_at TEXT NOT NULL
                )
            """)

            # Monitoring Evaluation Runs Table (Phase 13 Auditable Evaluation Run)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_evaluation_runs (
                    evaluation_run_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    as_of_date TEXT NOT NULL,
                    policy_version TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    total_signals_detected INTEGER NOT NULL,
                    active_signal_count INTEGER NOT NULL
                )
            """)

            # Temporal Warning Signals Table (Phase 13 Lifecycle Managed Signals)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temporal_warning_signals (
                    signal_id TEXT PRIMARY KEY,
                    signal_key TEXT NOT NULL,
                    evaluation_run_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    activity_id TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    as_of_date TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    reasoning_trace_json TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    involved_event_ids_json TEXT NOT NULL,
                    involved_evidence_ids_json TEXT NOT NULL,
                    first_detected_at TEXT NOT NULL,
                    last_detected_at TEXT NOT NULL
                )
            """)

            # Memory Distillation Runs Table (Phase 14 Auditable Distillation Log)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_distillation_runs (
                    distillation_run_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    as_of_date TEXT NOT NULL,
                    policy_version TEXT NOT NULL,
                    input_corrections_count INTEGER NOT NULL,
                    candidates_created_count INTEGER NOT NULL,
                    promoted_aliases_count INTEGER NOT NULL,
                    superseded_aliases_count INTEGER NOT NULL,
                    executed_at TEXT NOT NULL
                )
            """)

            # Terminology Aliases Table (Phase 14 Gated & Versioned Terminology Memory)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS terminology_aliases (
                    alias_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    alias_phrase TEXT NOT NULL,
                    target_activity_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    confidence_weight REAL NOT NULL,
                    confirmation_count INTEGER NOT NULL,
                    distinct_planner_count INTEGER NOT NULL,
                    distinct_source_count INTEGER NOT NULL,
                    reoverride_count INTEGER NOT NULL,
                    supersedes_alias_id TEXT,
                    last_validated_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Execution Rate Benchmarks Table (Phase 14 UOM-Safe Productivity Analytics)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_rate_benchmarks (
                    benchmark_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    wbs_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    discipline TEXT NOT NULL,
                    unit_of_measure TEXT NOT NULL,
                    quantity_basis TEXT NOT NULL,
                    planned_rate REAL,
                    mean_actual_rate REAL NOT NULL,
                    p50_rate REAL NOT NULL,
                    p90_rate REAL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    benchmark_status TEXT NOT NULL,
                    last_calculated_at TEXT NOT NULL
                )
            """)

            # Contractor Reporting Profiles Table (Phase 14 Reporting & Evidence Completeness Profiles)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contractor_reporting_profiles (
                    profile_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    contractor_id TEXT,
                    total_events INTEGER NOT NULL,
                    trusted_events INTEGER NOT NULL,
                    untrusted_events INTEGER NOT NULL,
                    verification_ratio REAL NOT NULL,
                    avg_reporting_delay_days REAL,
                    last_updated_at TEXT NOT NULL
                )
            """)

            # Conflict Resolution Patterns Table (Phase 14 Resolution Pathways Analytics)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conflict_resolution_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    conflict_or_signal_type TEXT NOT NULL,
                    total_occurrences INTEGER NOT NULL,
                    validated_count INTEGER NOT NULL,
                    remapped_count INTEGER NOT NULL,
                    rejected_count INTEGER NOT NULL,
                    acknowledged_count INTEGER NOT NULL,
                    resolved_count INTEGER NOT NULL,
                    avg_resolution_hours REAL NOT NULL,
                    last_updated_at TEXT NOT NULL
                )
            """)

            conn.commit()

    def save_source_document(self, doc: SourceDocument):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO source_documents (
                    source_id, project_id, source_type, file_name, sha256_hash,
                    raw_content, submitted_at, received_at, author, reporting_period,
                    extraction_status, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.source_id, doc.project_id, doc.source_type, doc.file_name, doc.sha256_hash,
                doc.raw_content, doc.submitted_at, doc.received_at, doc.author, doc.reporting_period,
                doc.extraction_status, json.dumps(doc.metadata_json)
            ))
            conn.commit()

    def save_execution_event(self, event: ExecutionEvent):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO execution_events (
                    event_id, source_id, fragment_id, event_type, observed_timestamp,
                    source_timestamp, extracted_statement, raw_observed_activity_id, observed_activity_id,
                    activity_id_validation_status, temporal_resolution_status, temporal_resolution_basis,
                    discipline, area_location, equipment_tag, line_number, observed_quantity, unit_of_measure,
                    progress_percent, status_text, extraction_confidence, lifecycle_state,
                    shift_context, pending_qa_clearance, remaining_quantity, work_front_tag,
                    quarantine_reasons_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id, event.source_id, event.fragment_id, event.event_type, event.observed_timestamp,
                event.source_timestamp, event.extracted_statement, event.raw_observed_activity_id, event.observed_activity_id,
                event.activity_id_validation_status, event.temporal_resolution_status, event.temporal_resolution_basis,
                event.discipline, event.area_location, event.equipment_tag, event.line_number, event.observed_quantity, event.unit_of_measure,
                event.progress_percent, event.status_text, event.extraction_confidence, event.lifecycle_state,
                event.shift_context, 1 if event.pending_qa_clearance else 0, event.remaining_quantity, event.work_front_tag,
                json.dumps(event.quarantine_reasons)
            ))

            if event.provenance:
                p = event.provenance
                cursor.execute("""
                    INSERT OR REPLACE INTO provenance_records (
                        provenance_id, event_id, source_id, source_type, locator_type,
                        locator_value, raw_text_snippet, field_provenance_map_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p.provenance_id, p.event_id, p.source_id, p.source_type, p.locator_type,
                    p.locator_value, p.raw_text_snippet, json.dumps(p.field_provenance_map)
                ))

            conn.commit()

    def save_quarantine_record(self, record: QuarantineRecord):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quarantine_records (
                    quarantine_id, source_id, event_id, failure_stage,
                    quarantine_reasons_json, raw_payload, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record.quarantine_id, record.source_id, record.event_id, record.failure_stage,
                json.dumps(record.quarantine_reasons), record.raw_payload, record.created_at
            ))
            conn.commit()

    def get_source_document(self, source_id: str) -> Optional[SourceDocument]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM source_documents WHERE source_id = ?", (source_id,))
            row = cursor.fetchone()
            if not row:
                return None
            r = dict(row)
            meta = json.loads(r["metadata_json"]) if r.get("metadata_json") else {}
            return SourceDocument(
                source_id=r["source_id"],
                project_id=r["project_id"],
                source_type=r["source_type"],
                file_name=r["file_name"],
                sha256_hash=r["sha256_hash"],
                raw_content=r["raw_content"],
                submitted_at=r["submitted_at"],
                received_at=r["received_at"],
                author=r.get("author", "Unknown"),
                reporting_period=r.get("reporting_period"),
                extraction_status=r.get("extraction_status", "EXTRACTED"),
                metadata_json=meta
            )

    def get_execution_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM execution_events WHERE event_id = ?", (event_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_events_by_source(self, source_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM execution_events WHERE source_id = ?", (source_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_all_execution_events(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM execution_events")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_execution_events_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ee.* FROM execution_events ee
                JOIN source_documents sd ON ee.source_id = sd.source_id
                WHERE sd.project_id = ?
            """, (project_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_quarantine_records(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quarantine_records")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def save_activity_fingerprint(self, fp: ActivityFingerprint):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO activity_fingerprints (
                    fingerprint_id, activity_id, project_id, activity_name, normalized_name,
                    wbs_id, wbs_code, wbs_name_path, discipline, area_location,
                    equipment_tag, line_number, start_km, end_km, planned_start,
                    planned_finish, baseline_duration_days, planned_quantity, unit_of_measure,
                    is_critical, predecessors_json, successors_json, action_verbs_json,
                    entity_nouns_json, synonyms_json, field_aliases_json, search_tokens_json,
                    fingerprint_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fp.fingerprint_id, fp.activity_id, fp.project_id, fp.activity_name, fp.normalized_name,
                fp.wbs_id, fp.wbs_code, fp.wbs_name_path, fp.discipline, fp.area_location,
                fp.equipment_tag, fp.line_number, fp.start_km, fp.end_km, fp.planned_start,
                fp.planned_finish, fp.baseline_duration_days, fp.planned_quantity, fp.unit_of_measure,
                1 if fp.is_critical else 0, json.dumps(fp.predecessors), json.dumps(fp.successors),
                json.dumps(fp.action_verbs), json.dumps(fp.entity_nouns), json.dumps(fp.synonyms),
                json.dumps(fp.field_aliases), json.dumps(fp.search_tokens), fp.fingerprint_version
            ))
            conn.commit()

    def get_fingerprint_by_activity_id(self, activity_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM activity_fingerprints WHERE activity_id = ?", (activity_id.upper(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_fingerprints_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM activity_fingerprints WHERE project_id = ?", (project_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    get_activity_fingerprints_by_project = get_fingerprints_by_project

    def get_all_fingerprints(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM activity_fingerprints")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def save_match_result(self, match: MatchResult):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO match_results (
                    match_id, event_id, source_id, outcome, selected_activity_id,
                    selected_activity_name, confidence_score, top_candidate_json,
                    candidate_matches_json, reasoning_trace_json, evaluated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match.match_id, match.event_id, match.source_id, match.outcome,
                match.selected_activity_id, match.selected_activity_name, match.confidence_score,
                json.dumps(match.top_candidate.to_dict()) if match.top_candidate else None,
                json.dumps([c.to_dict() for c in match.candidate_matches]),
                json.dumps(match.reasoning_trace), match.evaluated_at
            ))
            conn.commit()

    def get_match_results_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM match_results WHERE event_id = ?", (event_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_all_match_results(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM match_results")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    # ---------------------------------------------------------
    # PHASE 8 EVIDENCE, CLAIM, CONFLICT & TRUST PERSISTENCE
    # ---------------------------------------------------------

    def save_evidence(self, ev: Evidence):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO evidence_ledger (
                    evidence_id, event_id, source_id, fragment_id, locator_type,
                    locator_value, source_type, origin_group_id, raw_text_snippet,
                    observed_timestamp, provenance_map_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ev.evidence_id, ev.event_id, ev.source_id, ev.fragment_id, ev.locator_type,
                ev.locator_value, ev.source_type, ev.origin_group_id, ev.raw_text_snippet,
                ev.observed_timestamp, json.dumps(ev.provenance_map), ev.created_at
            ))
            conn.commit()

    def save_evidence_claim(self, claim: EvidenceClaim):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO evidence_claims (
                    claim_id, evidence_id, event_id, claim_type, raw_statement,
                    claim_value_json, unit, normalized_value, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claim.claim_id, claim.evidence_id, claim.event_id, claim.claim_type,
                claim.raw_statement, json.dumps(claim.claim_value), claim.unit,
                claim.normalized_value, claim.confidence
            ))
            conn.commit()

    def save_evidence_assessment(self, ea: EvidenceAssessment):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO evidence_assessments (
                    assessment_id, event_id, evidence_ids_json, claim_ids_json,
                    corroboration_status, unique_origin_count, evidence_support_score,
                    reliability_assessments_json, evidence_gaps_json, reasoning_trace_json, evaluated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ea.assessment_id, ea.event_id, json.dumps(ea.evidence_ids), json.dumps(ea.claim_ids),
                ea.corroboration_status, ea.unique_origin_count, ea.evidence_support_score,
                json.dumps([r.to_dict() for r in ea.reliability_assessments]),
                json.dumps(ea.evidence_gaps), json.dumps(ea.reasoning_trace), ea.evaluated_at
            ))
            conn.commit()

    def save_conflict_flag(self, flag: ConflictFlag):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO conflict_flags (
                    conflict_id, conflict_type, severity, involved_event_ids_json,
                    involved_claim_ids_json, involved_evidence_ids_json, description,
                    snippet_comparison_json, version_index, resolution_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flag.conflict_id, flag.conflict_type, flag.severity,
                json.dumps(flag.involved_event_ids), json.dumps(flag.involved_claim_ids),
                json.dumps(flag.involved_evidence_ids), flag.description,
                json.dumps(flag.snippet_comparison), flag.version_index,
                flag.resolution_status, flag.created_at
            ))
            conn.commit()

    def save_trust_assessment(self, ta: TrustAssessment):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trust_assessments (
                    assessment_id, event_id, version_index, match_confidence,
                    evidence_support, trust_status, gating_trigger, rationale_breakdown_json,
                    has_critical_conflict, has_evidence_gaps, evaluated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ta.assessment_id, ta.event_id, ta.version_index, ta.match_confidence,
                ta.evidence_support, ta.trust_status, ta.gating_trigger,
                json.dumps(ta.rationale_breakdown), 1 if ta.has_critical_conflict else 0,
                1 if ta.has_evidence_gaps else 0, ta.evaluated_at
            ))
            conn.commit()

    def get_evidence_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence_ledger WHERE event_id = ?", (event_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_claims_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence_claims WHERE event_id = ?", (event_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_evidence_assessment_by_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence_assessments WHERE event_id = ?", (event_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_conflict_flags_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Search inside JSON array for event_id
            cursor.execute("SELECT * FROM conflict_flags WHERE involved_event_ids_json LIKE ?", (f'%"{event_id}"%',))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_trust_assessments_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trust_assessments WHERE event_id = ? ORDER BY version_index ASC", (event_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_latest_trust_assessment(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trust_assessments WHERE event_id = ? ORDER BY version_index DESC LIMIT 1", (event_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ---------------------------------------------------------
    # PHASE 9 HUMAN VALIDATION (HITL) PERSISTENCE
    # ---------------------------------------------------------

    def save_validation_decision(self, decision: ValidationDecision):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO validation_decisions (
                    decision_id, event_id, planner_id, decision_type, reviewed_trust_version,
                    reviewed_match_result_id, reviewed_evidence_assessment_id, selected_activity_id,
                    previous_trust_version, resulting_trust_version, resulting_trust_status,
                    override_reason_category, reason_notes, evidence_reviewed_ids_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision.decision_id, decision.event_id, decision.planner_id, decision.decision_type,
                decision.reviewed_trust_version, decision.reviewed_match_result_id,
                decision.reviewed_evidence_assessment_id, decision.selected_activity_id,
                decision.previous_trust_version, decision.resulting_trust_version,
                decision.resulting_trust_status, decision.override_reason_category,
                decision.reason_notes, json.dumps(decision.evidence_reviewed_ids), decision.created_at
            ))
            conn.commit()

    def save_planner_correction(self, correction: PlannerCorrectionRecord):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO planner_corrections (
                    correction_id, event_id, original_activity_id, corrected_activity_id,
                    original_match_result_id, validation_decision_id, reason_category,
                    reason_notes, planner_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                correction.correction_id, correction.event_id, correction.original_activity_id,
                correction.corrected_activity_id, correction.original_match_result_id,
                correction.validation_decision_id, correction.reason_category,
                correction.reason_notes, correction.planner_id, correction.created_at
            ))
            conn.commit()

    def get_validation_decisions_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM validation_decisions WHERE event_id = ? ORDER BY created_at ASC", (event_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_planner_corrections(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM planner_corrections ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_all_validation_decisions(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM validation_decisions ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_validation_decisions_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vd.* FROM validation_decisions vd
                JOIN execution_events ee ON vd.event_id = ee.event_id
                JOIN source_documents sd ON ee.source_id = sd.source_id
                WHERE sd.project_id = ?
                ORDER BY vd.created_at DESC
            """, (project_id,))
            rows = cursor.fetchall()
            if not rows:
                cursor.execute("SELECT * FROM validation_decisions ORDER BY created_at DESC")
                rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def save_schedule_projection(self, projection: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            act_map_json = json.dumps({
                k: (v.to_dict() if hasattr(v, "to_dict") else v)
                for k, v in projection.activity_progress_map.items()
            })
            wbs_map_json = json.dumps({
                k: (v.to_dict() if hasattr(v, "to_dict") else v)
                for k, v in projection.wbs_progress_map.items()
            })
            cursor.execute("""
                INSERT OR REPLACE INTO schedule_projections (
                    projection_id, project_id, as_of_date, total_activities,
                    completed_activities, in_progress_activities, not_started_activities,
                    overall_project_progress_pct, critical_activity_delay_count,
                    max_schedule_delay_days, unverified_claims_count,
                    activity_progress_json, wbs_progress_json, generated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                projection.projection_id, projection.project_id, projection.as_of_date,
                projection.total_activities, projection.completed_activities,
                projection.in_progress_activities, projection.not_started_activities,
                projection.overall_project_progress_pct, projection.critical_activity_delay_count,
                projection.max_schedule_delay_days, projection.unverified_claims_count,
                act_map_json, wbs_map_json, projection.generated_at
            ))
            conn.commit()

    def get_latest_schedule_projection(self, project_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM schedule_projections WHERE project_id = ? ORDER BY generated_at DESC LIMIT 1",
                (project_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            res["activity_progress_map"] = json.loads(res["activity_progress_json"])
            res["wbs_progress_map"] = json.loads(res["wbs_progress_json"])
            return res

    def save_monitoring_evaluation_run(self, run: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO monitoring_evaluation_runs (
                    evaluation_run_id, project_id, as_of_date, policy_version,
                    evaluated_at, total_signals_detected, active_signal_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run.evaluation_run_id, run.project_id, run.as_of_date,
                run.policy_version, run.evaluated_at, run.total_signals_detected,
                run.active_signal_count
            ))
            conn.commit()

    def save_temporal_warning_signal(self, sig: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO temporal_warning_signals (
                    signal_id, signal_key, evaluation_run_id, project_id, activity_id,
                    signal_type, severity, status, as_of_date, summary, reasoning_trace_json,
                    recommended_action, involved_event_ids_json, involved_evidence_ids_json,
                    first_detected_at, last_detected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sig.signal_id, sig.signal_key, sig.evaluation_run_id, sig.project_id,
                sig.activity_id, sig.signal_type, sig.severity, sig.status,
                sig.as_of_date, sig.summary, json.dumps(sig.reasoning_trace),
                sig.recommended_action, json.dumps(sig.involved_event_ids),
                json.dumps(sig.involved_evidence_ids), sig.first_detected_at,
                sig.last_detected_at
            ))
            conn.commit()

    def get_active_signals_by_project(self, project_id: str, severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if severity_filter:
                cursor.execute(
                    "SELECT * FROM temporal_warning_signals WHERE project_id = ? AND status = 'ACTIVE' AND severity = ? ORDER BY last_detected_at DESC",
                    (project_id, severity_filter)
                )
            else:
                cursor.execute(
                    "SELECT * FROM temporal_warning_signals WHERE project_id = ? AND status = 'ACTIVE' ORDER BY last_detected_at DESC",
                    (project_id,)
                )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["reasoning_trace"] = json.loads(d["reasoning_trace_json"])
                d["involved_event_ids"] = json.loads(d["involved_event_ids_json"])
                d["involved_evidence_ids"] = json.loads(d["involved_evidence_ids_json"])
                results.append(d)
            return results

    def get_signal_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM temporal_warning_signals WHERE signal_id = ?", (signal_id,))
            row = cursor.fetchone()
            if not row:
                return None
            d = dict(row)
            d["reasoning_trace"] = json.loads(d["reasoning_trace_json"])
            d["involved_event_ids"] = json.loads(d["involved_event_ids_json"])
            d["involved_evidence_ids"] = json.loads(d["involved_evidence_ids_json"])
            return d

    def get_signals_by_key(self, signal_key: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM temporal_warning_signals WHERE signal_key = ? ORDER BY last_detected_at DESC", (signal_key,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["reasoning_trace"] = json.loads(d["reasoning_trace_json"])
                d["involved_event_ids"] = json.loads(d["involved_event_ids_json"])
                d["involved_evidence_ids"] = json.loads(d["involved_evidence_ids_json"])
                results.append(d)
            return results

    def save_memory_distillation_run(self, run: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memory_distillation_runs (
                    distillation_run_id, project_id, as_of_date, policy_version,
                    input_corrections_count, candidates_created_count,
                    promoted_aliases_count, superseded_aliases_count, executed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.distillation_run_id, run.project_id, run.as_of_date,
                run.policy_version, run.input_corrections_count,
                run.candidates_created_count, run.promoted_aliases_count,
                run.superseded_aliases_count, run.executed_at
            ))
            conn.commit()

    def get_memory_distillation_runs(self, project_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM memory_distillation_runs WHERE project_id = ? ORDER BY executed_at DESC",
                (project_id,)
            )
            return [dict(r) for r in cursor.fetchall()]

    def save_terminology_alias(self, alias: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO terminology_aliases (
                    alias_id, project_id, version, alias_phrase, target_activity_id,
                    status, confidence_weight, confirmation_count,
                    distinct_planner_count, distinct_source_count, reoverride_count,
                    supersedes_alias_id, last_validated_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alias.alias_id, alias.project_id, alias.version, alias.alias_phrase,
                alias.target_activity_id, alias.status, alias.confidence_weight,
                alias.confirmation_count, alias.distinct_planner_count,
                alias.distinct_source_count, alias.reoverride_count,
                alias.supersedes_alias_id, alias.last_validated_at, alias.created_at
            ))
            conn.commit()

    def get_terminology_aliases_by_project(self, project_id: str, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status_filter:
                cursor.execute(
                    "SELECT * FROM terminology_aliases WHERE project_id = ? AND status = ? ORDER BY confidence_weight DESC, created_at DESC",
                    (project_id, status_filter)
                )
            else:
                cursor.execute(
                    "SELECT * FROM terminology_aliases WHERE project_id = ? ORDER BY confidence_weight DESC, created_at DESC",
                    (project_id,)
                )
            return [dict(r) for r in cursor.fetchall()]

    def find_terminology_aliases_by_phrase(self, project_id: str, phrase: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM terminology_aliases WHERE project_id = ? AND lower(alias_phrase) = lower(?) AND status IN ('ACTIVE', 'VALIDATED') ORDER BY confidence_weight DESC",
                (project_id, phrase.strip())
            )
            return [dict(r) for r in cursor.fetchall()]

    def save_execution_rate_benchmark(self, bench: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO execution_rate_benchmarks (
                    benchmark_id, project_id, wbs_id, activity_type, discipline, unit_of_measure,
                    quantity_basis, planned_rate, mean_actual_rate, p50_rate,
                    p90_rate, sample_count, benchmark_status, last_calculated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bench.benchmark_id, bench.project_id, bench.wbs_id, bench.activity_type,
                bench.discipline, bench.unit_of_measure, bench.quantity_basis, bench.planned_rate,
                bench.mean_actual_rate, bench.p50_rate, bench.p90_rate,
                bench.sample_count, bench.benchmark_status, bench.last_calculated_at
            ))
            conn.commit()

    def get_execution_rate_benchmarks_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM execution_rate_benchmarks WHERE project_id = ? ORDER BY wbs_id ASC, activity_type ASC",
                (project_id,)
            )
            return [dict(r) for r in cursor.fetchall()]

    def save_contractor_reporting_profile(self, prof: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO contractor_reporting_profiles (
                    profile_id, project_id, contractor_id, total_events, trusted_events,
                    untrusted_events, verification_ratio, avg_reporting_delay_days, last_updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prof.profile_id, prof.project_id, prof.contractor_id, prof.total_events,
                prof.trusted_events, prof.untrusted_events, prof.verification_ratio,
                prof.avg_reporting_delay_days, prof.last_updated_at
            ))
            conn.commit()

    def get_contractor_reporting_profiles_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM contractor_reporting_profiles WHERE project_id = ? ORDER BY total_events DESC",
                (project_id,)
            )
            return [dict(r) for r in cursor.fetchall()]

    def save_conflict_resolution_pattern(self, pat: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO conflict_resolution_patterns (
                    pattern_id, project_id, conflict_or_signal_type, total_occurrences,
                    validated_count, remapped_count, rejected_count, acknowledged_count,
                    resolved_count, avg_resolution_hours, last_updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pat.pattern_id, pat.project_id, pat.conflict_or_signal_type,
                pat.total_occurrences, pat.validated_count, pat.remapped_count,
                pat.rejected_count, pat.acknowledged_count, pat.resolved_count,
                pat.avg_resolution_hours, pat.last_updated_at
            ))
            conn.commit()

    def get_conflict_resolution_patterns_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conflict_resolution_patterns WHERE project_id = ? ORDER BY total_occurrences DESC",
                (project_id,)
            )
            return [dict(r) for r in cursor.fetchall()]




