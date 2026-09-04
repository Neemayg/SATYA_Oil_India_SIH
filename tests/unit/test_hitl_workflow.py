"""
SATYA Human Validation (HITL) Workflow Unit Tests (Phase 9)
"""

import unittest
from datetime import datetime
from backend.models.domain_models import (
    ExecutionEvent, SourceDocument, SourceFragment, MatchResult, MatchOutcome,
    Evidence, ValidationDecisionType, OverrideReasonCategory, TrustStatus,
    QueuePriority
)
from backend.persistence.database_engine import DatabaseEngine
from backend.services.trust_evaluator_service import TrustEvaluatorService
from backend.hitl.queue_manager import PlannerQueueManager
from backend.hitl.validation_service import ValidationService

class TestHITLWorkflow(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.trust_service = TrustEvaluatorService(self.db)
        self.queue_manager = PlannerQueueManager(self.db)
        self.validation_service = ValidationService(self.db, valid_vocabulary={"ACT-1010", "ACT-1020", "ACT-1030"})

    def _create_sample_event(self, event_id: str = "EVT-1001") -> ExecutionEvent:
        event = ExecutionEvent(
            event_id=event_id,
            source_id="SRC-1001",
            fragment_id="FRG-1001",
            event_type="PROGRESS",
            observed_timestamp="2026-09-02",
            source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Mainline trenching 400m completed on PL-16-01.",
            discipline="CIVIL",
            line_number="PL-16-01",
            observed_quantity=400.0,
            unit_of_measure="METER",
            progress_percent=100.0,
            extraction_confidence=0.95
        )
        self.db.save_execution_event(event)

        match_res = MatchResult(
            match_id=f"MTH-{event_id}",
            event_id=event_id,
            source_id="SRC-1001",
            outcome=MatchOutcome.MATCHED,
            selected_activity_id="ACT-1010",
            selected_activity_name="Mainline Trenching",
            confidence_score=0.91
        )
        self.db.save_match_result(match_res)

        # Initial Trust Evaluation
        self.trust_service.evaluate_trust_for_event(event, match_res)
        return event

    def test_decision_validate_appends_version(self):
        event = self._create_sample_event("EVT-VAL")

        decision = self.validation_service.validate_event(
            event_id="EVT-VAL",
            planner_id="PLN-EXPERT-01",
            reason_notes="Verified by senior planner."
        )

        self.assertEqual(decision.decision_type, ValidationDecisionType.VALIDATE)
        self.assertEqual(decision.previous_trust_version, 1)
        self.assertEqual(decision.resulting_trust_version, 2)
        self.assertEqual(decision.resulting_trust_status, TrustStatus.TRUSTED)

        # Verify historical v1 remains intact!
        trust_history = self.db.get_trust_assessments_by_event("EVT-VAL")
        self.assertEqual(len(trust_history), 2)
        self.assertEqual(trust_history[0]["version_index"], 1)
        self.assertEqual(trust_history[1]["version_index"], 2)
        self.assertEqual(trust_history[1]["trust_status"], TrustStatus.TRUSTED)

    def test_decision_change_match_non_mutating(self):
        event = self._create_sample_event("EVT-CHG")

        decision = self.validation_service.change_match(
            event_id="EVT-CHG",
            new_activity_id="ACT-1020",
            planner_id="PLN-EXPERT-01",
            reason_category=OverrideReasonCategory.TERMINOLOGY_ALIAS,
            reason_notes="Re-mapped from ACT-1010 to ACT-1020 based on site plan."
        )

        self.assertEqual(decision.decision_type, ValidationDecisionType.CHANGE_MATCH)
        self.assertEqual(decision.selected_activity_id, "ACT-1020")
        self.assertEqual(decision.resulting_trust_status, TrustStatus.TRUSTED)

        # Original MatchResult MUST REMAIN UNTOUCHED!
        matches = self.db.get_match_results_by_event("EVT-CHG")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["selected_activity_id"], "ACT-1010")  # Original preserved!

        # Derived PlannerCorrectionRecord MUST BE EMITTED for Phase 14!
        corrections = self.db.get_planner_corrections()
        self.assertEqual(len(corrections), 1)
        self.assertEqual(corrections[0]["event_id"], "EVT-CHG")
        self.assertEqual(corrections[0]["original_activity_id"], "ACT-1010")
        self.assertEqual(corrections[0]["corrected_activity_id"], "ACT-1020")

    def test_decision_change_match_invalid_id_rule5(self):
        event = self._create_sample_event("EVT-R5")

        # Re-mapping to hallucinated ID "ACT-9999" MUST raise ValueError under Rule 5
        with self.assertRaises(ValueError) as ctx:
            self.validation_service.change_match(
                event_id="EVT-R5",
                new_activity_id="ACT-9999",
                planner_id="PLN-EXPERT-01"
            )
        self.assertIn("Rule 5 Violation", str(ctx.exception))

    def test_decision_reject(self):
        event = self._create_sample_event("EVT-REJ")

        decision = self.validation_service.reject_event(
            event_id="EVT-REJ",
            planner_id="PLN-EXPERT-01",
            reason_category=OverrideReasonCategory.SCOPE_EXCLUSION,
            reason_notes="Work outside project scope."
        )

        self.assertEqual(decision.decision_type, ValidationDecisionType.REJECT)
        self.assertEqual(decision.resulting_trust_status, TrustStatus.UNTRUSTED)

        latest_ta = self.db.get_latest_trust_assessment("EVT-REJ")
        self.assertEqual(latest_ta["trust_status"], TrustStatus.UNTRUSTED)

    def test_decision_request_evidence(self):
        event = self._create_sample_event("EVT-REQ")

        decision = self.validation_service.request_evidence(
            event_id="EVT-REQ",
            planner_id="PLN-EXPERT-01",
            reason_notes="Missing QA clearance certificate."
        )

        self.assertEqual(decision.decision_type, ValidationDecisionType.REQUEST_EVIDENCE)
        self.assertEqual(decision.resulting_trust_status, TrustStatus.REVIEW_REQUIRED)

    def test_decision_defer(self):
        event = self._create_sample_event("EVT-DEF")

        decision = self.validation_service.defer_event(
            event_id="EVT-DEF",
            planner_id="PLN-EXPERT-01",
            reason_notes="Shift handoff deferral."
        )

        self.assertEqual(decision.decision_type, ValidationDecisionType.DEFER)
        self.assertEqual(decision.resulting_trust_status, TrustStatus.REVIEW_REQUIRED)

    def test_decision_snapshot_lock(self):
        event = self._create_sample_event("EVT-SNAP")

        decision = self.validation_service.validate_event(
            event_id="EVT-SNAP",
            planner_id="PLN-EXPERT-01"
        )

        # Decision MUST lock reviewed_trust_version, reviewed_match_result_id, reviewed_evidence_assessment_id
        self.assertEqual(decision.reviewed_trust_version, 1)
        self.assertTrue(decision.reviewed_match_result_id.startswith("MTH-"))
        self.assertTrue(decision.reviewed_evidence_assessment_id.startswith("EVA-"))

    def test_queue_prioritization_deterministic_order(self):
        # Create events with different risk levels
        self._create_sample_event("EVT-LOW")

        # Event with QA Conflict (P1 Critical)
        event_crit = ExecutionEvent("EVT-CRIT", "SRC-1", "FRG-1", "FINISH", "2026-09-02", "2026-09-02", "Valve complete, QA rejected.", progress_percent=100.0, extraction_confidence=0.9)
        self.db.save_execution_event(event_crit)
        match_crit = MatchResult("MTH-CRIT", "EVT-CRIT", "SRC-1", MatchOutcome.MATCHED, "ACT-1010", "Mainline Valve", 0.90)
        self.db.save_match_result(match_crit)
        self.trust_service.evaluate_trust_for_event(event_crit, match_crit)

        queue = self.queue_manager.get_review_queue()
        self.assertTrue(len(queue) >= 1)
        # P1 Critical items must be placed at the top of the queue!
        self.assertEqual(queue[0].event_id, "EVT-CRIT")
        self.assertEqual(queue[0].priority, QueuePriority.P1_CRITICAL)

if __name__ == "__main__":
    unittest.main()
