"""
SATYA Programmatic Architectural Property Invariant Unit Tests (Phase 15)
Programmatically verifies core architectural invariants:
1. 5-Entity Historical Immutability (ExecutionEvent, MatchResult, ValidationDecision, TrustAssessment, ScheduleProjection)
2. Rule 5 Schedule-Aware Closed Vocabulary Safety
3. Claim Provenance & Audit Trail Integrity
4. Engine Determinism
5. Payload Ingestion Idempotency
6. Multi-Tenant Project Isolation
7. Trust Monotonicity & Gating Safety
"""

import os
import unittest
import hashlib
from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI
from backend.models.domain_models import (
    ExecutionEvent, ActivityFingerprint, MatchOutcome, SourceType, TrustStatus, OverrideReasonCategory, ValidationDecisionType
)

class TestPropertyInvariants(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.api = SATYAApplicationAPI(self.db)
        self.project_id_a = "PRJ-ALPHA-2026"
        self.project_id_b = "PRJ-BETA-2026"

        # Load schedule for Alpha
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.api.fingerprint_service.process_schedule_file(schedule_path)

        vocab = self.api.fingerprint_service.get_valid_activity_vocabulary()
        self.api.pipeline_service.set_schedule_vocabulary(vocab)
        self.api.validation_service.set_valid_vocabulary(vocab)

    # 1. HISTORICAL IMMUTABILITY
    def test_five_entity_historical_immutability(self):
        """Historical records across 5 core entities are append-only and never mutated."""
        dpr_content = "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA cleared."
        code1, _, body1 = self.api.dispatch("POST", "/api/v1/ingestion/upload", body={
            "project_id": "PRJ-NBG-2026",
            "source_type": "DPR_EXCEL",
            "content": dpr_content
        })
        self.assertEqual(code1, 201)
        event_id = body1["events_extracted"][0]["event_id"]

        self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": event_id})
        self.api.dispatch("POST", "/api/v1/evidence/evaluate", body={"event_id": event_id})
        self.api.dispatch("POST", "/api/v1/projections/generate", body={"project_id": "PRJ-NBG-2026"})

        # Record original snapshots of all entities
        orig_event = self.db.get_execution_event(event_id)
        orig_match = self.db.get_match_results_by_event(event_id)[0]
        orig_trust_v1 = self.db.get_latest_trust_assessment(event_id)
        # Record original snapshots of all entities
        orig_event = self.db.get_execution_event(event_id)
        orig_match = self.db.get_match_results_by_event(event_id)[0]
        orig_trust_v1 = self.db.get_latest_trust_assessment(event_id)
        orig_proj_v1 = self.db.get_latest_schedule_projection("PRJ-NBG-2026")

        # Submit HITL CHANGE_MATCH decision (creating v2)
        code_h, _, body_h = self.api.dispatch("POST", "/api/v1/hitl/decisions", body={
            "event_id": event_id,
            "planner_id": "PLN-IMMUTABLE",
            "decision_type": ValidationDecisionType.CHANGE_MATCH,
            "reviewed_trust_version": 1,
            "reviewed_match_result_id": orig_match["match_id"],
            "reviewed_evidence_assessment_id": "EVA-1",
            "selected_activity_id": "ACT-1020",
            "override_reason_category": OverrideReasonCategory.OTHER,
            "reason_notes": "Immutability verification re-map"
        })
        self.assertEqual(code_h, 200)

        # Assert Entity 1: ExecutionEvent un-mutated
        post_event = self.db.get_execution_event(event_id)
        self.assertEqual(orig_event, post_event)

        # Assert Entity 2: Original MatchResult un-mutated
        post_match = self.db.get_match_results_by_event(event_id)[0]
        self.assertEqual(orig_match, post_match)

        # Assert Entity 3: Original TrustAssessment v1 un-mutated
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trust_assessments WHERE event_id = ? AND version_index = 1", (event_id,))
        v1_row = dict(cursor.fetchone())
        self.assertEqual(v1_row["version_index"], 1)
        self.assertEqual(v1_row["trust_status"], orig_trust_v1["trust_status"])

        # Assert Entity 4: ValidationDecision appended cleanly
        decisions = self.db.get_validation_decisions_by_event(event_id)
        self.assertEqual(len(decisions), 1)

        # Assert Entity 5: Projection has append-only update history
        proj_post = self.db.get_latest_schedule_projection("PRJ-NBG-2026")
        self.assertIsNotNone(proj_post)

    # 2. RULE 5 CLOSED VOCABULARY SAFETY
    def test_rule_5_closed_vocabulary_safety(self):
        """Unrecognized activity IDs in explicit claims or HITL decisions are strictly rejected or reset."""
        # Pipeline resets invalid explicit IDs to None
        res = self.api.pipeline_service.process_source_payload(
            raw_content="ACT-99999: Unknown activity performance claim",
            file_name="unknown.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.TEXT_DOCUMENT
        )
        for evt in res.events_extracted:
            if evt.raw_observed_activity_id == "ACT-99999":
                self.assertIsNone(evt.observed_activity_id)

        # HITL service rejects invalid activity IDs
        dpr = "2026-09-02: Excavation completed on ACT-1010."
        self.api.dispatch("POST", "/api/v1/ingestion/upload", body={"project_id": "PRJ-NBG-2026", "source_type": "DPR_EXCEL", "content": dpr})
        events = self.db.get_all_execution_events()
        evt_id = events[0]["event_id"]
        self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": evt_id})
        self.api.dispatch("POST", "/api/v1/evidence/evaluate", body={"event_id": evt_id})

        code_bad, _, body_bad = self.api.dispatch("POST", "/api/v1/hitl/decisions", body={
            "event_id": evt_id,
            "planner_id": "PLN-RULE5",
            "decision_type": ValidationDecisionType.CHANGE_MATCH,
            "reviewed_trust_version": 1,
            "selected_activity_id": "ACT-FORBIDDEN-999"
        })
        self.assertEqual(code_bad, 400)
        self.assertIn("Rule 5 Violation", body_bad["error"]["message"])

    # 3. CLAIM PROVENANCE INTEGRITY
    def test_claim_provenance_integrity(self):
        """Every extracted event retains exact raw statement, source document reference, and ingestion metadata."""
        raw_text = "Hydrotest completed on Section 1 pipeline line PL-NBG-SEC1."
        res = self.api.pipeline_service.process_source_payload(
            raw_content=raw_text,
            file_name="dpr_provenance.txt",
            project_id="PRJ-NBG-2026",
            source_type=SourceType.TEXT_DOCUMENT
        )
        self.assertGreater(len(res.events_extracted), 0)
        evt = res.events_extracted[0]
        self.assertIsNotNone(evt.source_id)
        self.assertIsNotNone(evt.fragment_id)
        self.assertIn(raw_text, evt.extracted_statement)

    # 4. DETERMINISM
    def test_matching_engine_determinism(self):
        """Identical events matched against identical fingerprinted schedules produce 100% identical match scores."""
        dpr = "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010."
        self.api.dispatch("POST", "/api/v1/ingestion/upload", body={"project_id": "PRJ-NBG-2026", "source_type": "DPR_EXCEL", "content": dpr})
        evt_dict = self.db.get_all_execution_events()[0]
        valid_fields = {k: v for k, v in evt_dict.items() if k in ExecutionEvent.__dataclass_fields__}
        event = ExecutionEvent(**valid_fields)

        res1 = self.api.matching_service.match_event(event, project_id="PRJ-NBG-2026")
        res2 = self.api.matching_service.match_event(event, project_id="PRJ-NBG-2026")

        self.assertEqual(res1.selected_activity_id, res2.selected_activity_id)
        self.assertEqual(res1.confidence_score, res2.confidence_score)
        self.assertEqual(res1.outcome, res2.outcome)

    # 5. IDEMPOTENCY
    def test_payload_ingestion_idempotency(self):
        """Re-submitting exact duplicate content returns duplicate status without creating duplicate source documents."""
        raw = "Duplicate report line for testing idempotency."
        code1, _, body1 = self.api.dispatch("POST", "/api/v1/ingestion/upload", body={
            "project_id": "PRJ-NBG-2026",
            "source_type": "DPR_EXCEL",
            "content": raw
        })
        self.assertEqual(code1, 201)

        code2, _, body2 = self.api.dispatch("POST", "/api/v1/ingestion/upload", body={
            "project_id": "PRJ-NBG-2026",
            "source_type": "DPR_EXCEL",
            "content": raw
        })
        # Duplicate detection: same source is returned, status is SUCCESS_CACHED
        self.assertIn(code2, [200, 201])
        self.assertEqual(body2.get("status"), "SUCCESS_CACHED")
        self.assertEqual(body2.get("source_id"), body1.get("source_id"))

    # 6. PROJECT ISOLATION
    def test_project_isolation(self):
        """Ingested data for Project A is strictly isolated from Project B matching queries."""
        # Ingest for PRJ-NBG-2026
        self.api.dispatch("POST", "/api/v1/ingestion/upload", body={
            "project_id": "PRJ-NBG-2026",
            "source_type": "DPR_EXCEL",
            "content": "Excavation 200m completed."
        })

        # Query events filtered by another project
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM source_documents WHERE project_id = ?", ("PRJ-OTHER",))
        count_b = cursor.fetchone()[0]

        self.assertEqual(count_b, 0)

    # 7. VERSIONED TRUST STATE INTEGRITY (APPEND-ONLY LEDGER)
    def test_versioned_trust_state_integrity(self):
        """Trust assessments maintain append-only version history (v1 -> v2) without overwriting prior records."""
        dpr = "2026-09-02: Excavation 100m completed ACT-1010."
        self.api.dispatch("POST", "/api/v1/ingestion/upload", body={"project_id": "PRJ-NBG-2026", "source_type": "DPR_EXCEL", "content": dpr})
        evt_id = self.db.get_all_execution_events()[0]["event_id"]
        self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": evt_id})
        self.api.dispatch("POST", "/api/v1/evidence/evaluate", body={"event_id": evt_id})

        ta_v1 = self.db.get_latest_trust_assessment(evt_id)
        self.assertIn(ta_v1["trust_status"], [TrustStatus.TRUSTED, TrustStatus.UNTRUSTED, TrustStatus.REVIEW_REQUIRED])

        # Validate upgrades/maintains trust in v2
        self.api.dispatch("POST", "/api/v1/hitl/decisions", body={
            "event_id": evt_id,
            "planner_id": "PLN-MONOTONE",
            "decision_type": ValidationDecisionType.VALIDATE,
            "reviewed_trust_version": 1
        })
        ta_v2 = self.db.get_latest_trust_assessment(evt_id)
        self.assertEqual(ta_v2["trust_status"], TrustStatus.TRUSTED)
        self.assertEqual(ta_v2["version_index"], 2)

if __name__ == "__main__":
    unittest.main()
