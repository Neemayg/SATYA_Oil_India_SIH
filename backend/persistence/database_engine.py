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
    ProvenanceRecord, QuarantineRecord, ActivityFingerprint, MatchResult
)

class DatabaseEngine:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:")
            self._mem_conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._mem_conn:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path)
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
                INSERT INTO execution_events (
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
                    INSERT INTO provenance_records (
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

    def get_events_by_source(self, source_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM execution_events WHERE source_id = ?", (source_id,))
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
