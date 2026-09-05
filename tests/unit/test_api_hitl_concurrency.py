"""
SATYA API HITL REST Snapshot Lock Concurrency Unit Tests (Phase 11)
Verifies that submitting a HITL validation decision against a superseded
reviewed_trust_version returns HTTP 409 Conflict with STALE_REVIEW_STATE error code.
"""

import os
import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI
from backend.models.domain_models import ValidationDecisionType, OverrideReasonCategory, TrustStatus

class TestAPIHITLConcurrency(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.api = SATYAApplicationAPI(self.db)
        self.project_id = "PRJ-NBG-2026"

        # Index baseline schedule
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.api.fingerprint_service.process_schedule_file(schedule_path)

        # Set schedule vocabulary for Rule 5 guardrails
        vocab = self.api.fingerprint_service.get_valid_activity_vocabulary()
        self.api.pipeline_service.set_schedule_vocabulary(vocab)
        self.api.validation_service.set_valid_vocabulary(vocab)

    def test_hitl_decision_against_stale_trust_version_returns_409_conflict(self):
        # 1. Ingest Event
        dpr_content = "2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA cleared."
        code1, _, body1 = self.api.dispatch("POST", "/api/v1/ingestion/upload", body={
            "project_id": self.project_id,
            "source_type": "DPR_EXCEL",
            "content": dpr_content
        })
        self.assertEqual(code1, 201)
        event_id = body1["events_extracted"][0]["event_id"]

        # 2. Match Event
        code2, _, body2 = self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": event_id})
        self.assertEqual(code2, 200)

        # 3. Upload already auto-evaluates trust (v1 TrustAssessment exists)
        ta_v1 = self.api.db.get_latest_trust_assessment(event_id)
        self.assertIsNotNone(ta_v1)
        self.assertEqual(ta_v1["version_index"], 1)

        # Planner A reads v1 TrustAssessment
        planner_a_reviewed_ver = 1

        # Planner B submits VALIDATE decision (Generates v2 TrustAssessment)
        code_b, _, body_b = self.api.dispatch("POST", "/api/v1/hitl/decisions", body={
            "event_id": event_id,
            "planner_id": "PLN-B",
            "decision_type": ValidationDecisionType.VALIDATE,
            "reviewed_trust_version": 1,
            "reviewed_match_result_id": "MTH-1",
            "reviewed_evidence_assessment_id": "EVA-1",
            "reason_notes": "Planner B validation"
        })
        self.assertEqual(code_b, 200)

        # Now current trust version is v2!
        # Planner A attempts to submit CHANGE_MATCH decision against stale v1
        code_a, _, body_a = self.api.dispatch("POST", "/api/v1/hitl/decisions", body={
            "event_id": event_id,
            "planner_id": "PLN-A",
            "decision_type": ValidationDecisionType.CHANGE_MATCH,
            "reviewed_trust_version": planner_a_reviewed_ver,  # Stale v1!
            "reviewed_match_result_id": "MTH-1",
            "reviewed_evidence_assessment_id": "EVA-1",
            "selected_activity_id": "ACT-1020",
            "override_reason_category": OverrideReasonCategory.OTHER,
            "reason_notes": "Planner A stale submission"
        })

        # MUST return 409 Conflict!
        self.assertEqual(code_a, 409)
        self.assertIn("error", body_a)
        err = body_a["error"]
        self.assertEqual(err["code"], "STALE_REVIEW_STATE")
        self.assertIn("v1", err["message"])
        self.assertIn("v2", err["message"])

if __name__ == "__main__":
    unittest.main()
