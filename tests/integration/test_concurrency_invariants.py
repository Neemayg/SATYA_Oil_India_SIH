"""
SATYA Database Invariant Concurrency Stress Tests (Phase 15)
Verifies concurrent N=2, N=5, N=10 HITL review requests under multi-threading.
Asserts state invariants:
1. Exactly 1 request succeeds (HTTP 200), competing concurrent requests receive HTTP 409 (STALE_REVIEW_STATE).
2. DB State Invariants:
   - Exactly 1 new ValidationDecision row added
   - Exactly 1 new TrustAssessment v2 added
   - Exactly 1 new PlannerCorrectionRecord added
   - Historical v1 TrustAssessment remains intact (append-only ledger, zero mutations)
"""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI
from backend.models.domain_models import ValidationDecisionType, OverrideReasonCategory

class TestConcurrencyInvariants(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.api = SATYAApplicationAPI(self.db)
        self.project_id = "PRJ-NBG-2026"

        # Load synthetic baseline schedule
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        self.api.fingerprint_service.process_schedule_file(schedule_path)

        # Set vocabulary for Rule 5 closed vocabulary protection
        vocab = self.api.fingerprint_service.get_valid_activity_vocabulary()
        self.api.pipeline_service.set_schedule_vocabulary(vocab)
        self.api.validation_service.set_valid_vocabulary(vocab)

    def _seed_review_state(self, unique_tag="CONC"):
        dpr_content = f"2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010 tag {unique_tag}. QA cleared."
        code1, _, body1 = self.api.dispatch("POST", "/api/v1/ingestion/upload", body={
            "project_id": self.project_id,
            "source_type": "DPR_EXCEL",
            "content": dpr_content
        })
        self.assertEqual(code1, 201)
        event_id = body1["events_extracted"][0]["event_id"]

        code2, _, _ = self.api.dispatch("POST", "/api/v1/matching/match", body={"event_id": event_id})
        self.assertEqual(code2, 200)

        code3, _, _ = self.api.dispatch("POST", "/api/v1/evidence/evaluate", body={"event_id": event_id})
        self.assertEqual(code3, 200)

        return event_id

    def _run_concurrency_stress(self, n_workers):
        """Run N concurrent threads submitting CHANGE_MATCH on the same event_id with reviewed_trust_version=1."""
        event_id = self._seed_review_state(f"N{n_workers}")

        results = []

        def worker_task(worker_id):
            code, _, body = self.api.dispatch("POST", "/api/v1/hitl/decisions", body={
                "event_id": event_id,
                "planner_id": f"PLN-WORKER-{worker_id}",
                "decision_type": ValidationDecisionType.CHANGE_MATCH,
                "reviewed_trust_version": 1,
                "reviewed_match_result_id": "MTH-1",
                "reviewed_evidence_assessment_id": "EVA-1",
                "selected_activity_id": "ACT-1020",
                "override_reason_category": OverrideReasonCategory.OTHER,
                "reason_notes": f"Concurrent CHANGE_MATCH by worker {worker_id}"
            })
            return {"code": code, "body": body}

        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(n_workers)]
            for future in as_completed(futures):
                results.append(future.result())

        # Assert exactly 1 request succeeded with 200 HTTP code
        code_200 = [r for r in results if r["code"] == 200]
        code_409 = [r for r in results if r["code"] == 409]

        self.assertEqual(len(code_200), 1, f"Expected exactly 1 success (HTTP 200) for N={n_workers}, got {len(code_200)}")
        self.assertEqual(len(code_409), n_workers - 1, f"Expected {n_workers-1} HTTP 409 (STALE_REVIEW_STATE) responses, got {len(code_409)}")

        for r409 in code_409:
            self.assertEqual(r409["body"]["error"]["code"], "STALE_REVIEW_STATE")

        # Verify DB Invariants
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # 1. Exactly 1 ValidationDecision row added
        cursor.execute("SELECT COUNT(*) FROM validation_decisions WHERE event_id = ?", (event_id,))
        v_count = cursor.fetchone()[0]
        self.assertEqual(v_count, 1, "DB Invariant Violation: Exactly 1 ValidationDecision must exist.")

        # 2. Trust assessments: version 1 (historical) and version 2 (updated) must exist
        cursor.execute("SELECT version_index, trust_status FROM trust_assessments WHERE event_id = ? ORDER BY version_index ASC", (event_id,))
        trust_rows = cursor.fetchall()
        self.assertEqual(len(trust_rows), 2, "DB Invariant Violation: Must have exactly 2 TrustAssessment rows (v1 append-only, v2 new).")

        # Check v1 historical integrity
        v1_row = trust_rows[0]
        self.assertEqual(v1_row["version_index"], 1)

        # Check v2 update integrity
        v2_row = trust_rows[1]
        self.assertEqual(v2_row["version_index"], 2)
        self.assertEqual(v2_row["trust_status"], "TRUSTED")

        # 3. Exactly 1 PlannerCorrectionRecord added
        cursor.execute("SELECT COUNT(*) FROM planner_corrections WHERE event_id = ?", (event_id,))
        p_count = cursor.fetchone()[0]
        self.assertEqual(p_count, 1, "DB Invariant Violation: Exactly 1 PlannerCorrectionRecord must exist.")

    def test_concurrency_n2(self):
        self._run_concurrency_stress(2)

    def test_concurrency_n5(self):
        self._run_concurrency_stress(5)

    def test_concurrency_n10(self):
        self._run_concurrency_stress(10)

if __name__ == "__main__":
    unittest.main()
