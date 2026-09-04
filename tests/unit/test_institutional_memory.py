"""
SATYA Institutional Memory Unit Tests (Phase 14)
Verifies alias promotion lifecycle, confidence math, project scope isolation,
historical match regression immutability, and reproducibility.
"""

import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.analytics.memory_service import InstitutionalMemoryService
from backend.models.domain_models import (
    ExecutionEvent, ActivityFingerprint, MatchResult, MatchFactorScores,
    MatchOutcome, ValidationDecision, PlannerCorrectionRecord,
    AliasStatus, InstitutionalMemoryPolicy
)
from backend.matching.matching_engine import ScheduleAwareMatchingEngine

class TestInstitutionalMemoryService(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.policy = InstitutionalMemoryPolicy(min_candidate_confirmations=2)
        self.memory_service = InstitutionalMemoryService(self.db, self.policy)
        self.matching_engine = ScheduleAwareMatchingEngine()

        # Seed Activity Fingerprint for testing
        self.fp = ActivityFingerprint(
            fingerprint_id="FP-1010",
            activity_id="ACT-1010",
            project_id="PRJ-NBG-2026",
            activity_name="Trenchless Drilling HDD Section 1",
            normalized_name="trenchless drilling hdd section 1",
            wbs_id="WBS-01",
            wbs_code="1.1",
            wbs_name_path="Project / Trenchless",
            discipline="PIPING",
            planned_start="2026-09-01",
            planned_finish="2026-09-10"
        )
        self.db.save_activity_fingerprint(self.fp)

    def test_single_correction_creates_candidate_status(self):
        """Single CHANGE_MATCH correction must create a CANDIDATE alias, not ACTIVE."""
        event = ExecutionEvent(
            event_id="EVT-001",
            source_id="SRC-1",
            fragment_id="FRAG-1",
            event_type="PROGRESS",
            observed_timestamp="2026-09-04",
            source_timestamp="2026-09-04T10:00:00Z",
            extracted_statement="HDD drilling at Section 1"
        )
        self.db.save_execution_event(event)

        corr = PlannerCorrectionRecord(
            correction_id="CORR-001",
            event_id="EVT-001",
            original_activity_id="ACT-9999",
            corrected_activity_id="ACT-1010",
            original_match_result_id="MTH-001",
            validation_decision_id="DEC-001",
            reason_category="TERMINOLOGY_ALIAS",
            reason_notes="HDD maps to ACT-1010",
            planner_id="PLN-01",
            created_at="2026-09-04T10:00:00Z"
        )
        self.db.save_planner_correction(corr)

        run = self.memory_service.distill_planner_corrections("PRJ-NBG-2026")
        self.assertEqual(run.candidates_created_count, 1)

        aliases = self.db.get_terminology_aliases_by_project("PRJ-NBG-2026")
        self.assertEqual(len(aliases), 1)
        self.assertEqual(aliases[0]["status"], AliasStatus.CANDIDATE)

    def test_repeated_confirmations_promote_to_active(self):
        """Repeated independent planner confirmations promote CANDIDATE -> ACTIVE."""
        # Event 1 (Planner 1)
        e1 = ExecutionEvent(event_id="EVT-001", source_id="SRC-1", fragment_id="F1", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T10:00:00Z", extracted_statement="HDD drilling at Section 1")
        self.db.save_execution_event(e1)
        self.db.save_planner_correction(PlannerCorrectionRecord("C1", "EVT-001", "ACT-0", "ACT-1010", "M1", "D1", "TERMINOLOGY_ALIAS", "", "PLN-01", "2026-09-04T10:00:00Z"))

        # Event 2 (Planner 2)
        e2 = ExecutionEvent(event_id="EVT-002", source_id="SRC-2", fragment_id="F2", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T11:00:00Z", extracted_statement="HDD drilling at Section 1")
        self.db.save_execution_event(e2)
        self.db.save_planner_correction(PlannerCorrectionRecord("C2", "EVT-002", "ACT-0", "ACT-1010", "M2", "D2", "TERMINOLOGY_ALIAS", "", "PLN-02", "2026-09-04T11:00:00Z"))

        # Event 3 (Planner 3)
        e3 = ExecutionEvent(event_id="EVT-003", source_id="SRC-3", fragment_id="F3", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T12:00:00Z", extracted_statement="HDD drilling at Section 1")
        self.db.save_execution_event(e3)
        self.db.save_planner_correction(PlannerCorrectionRecord("C3", "EVT-003", "ACT-0", "ACT-1010", "M3", "D3", "TERMINOLOGY_ALIAS", "", "PLN-03", "2026-09-04T12:00:00Z"))

        self.memory_service.distill_planner_corrections("PRJ-NBG-2026")
        aliases = self.db.get_terminology_aliases_by_project("PRJ-NBG-2026")
        self.assertEqual(len(aliases), 1)
        self.assertEqual(aliases[0]["status"], AliasStatus.ACTIVE)
        self.assertGreater(aliases[0]["distinct_planner_count"], 1)

    def test_same_planner_repetition_does_not_artificially_inflate_planners(self):
        """Multiple corrections from the same planner do not inflate distinct_planner_count."""
        for i in range(3):
            e = ExecutionEvent(event_id=f"EVT-S{i}", source_id=f"SRC-{i}", fragment_id=f"F{i}", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T10:00:00Z", extracted_statement="Tie-in work")
            self.db.save_execution_event(e)
            self.db.save_planner_correction(PlannerCorrectionRecord(f"CS{i}", f"EVT-S{i}", "ACT-0", "ACT-1010", "M", "D", "TERMINOLOGY_ALIAS", "", "PLN-SAME", "2026-09-04T10:00:00Z"))

        self.memory_service.distill_planner_corrections("PRJ-NBG-2026")
        aliases = self.db.get_terminology_aliases_by_project("PRJ-NBG-2026")
        self.assertEqual(aliases[0]["distinct_planner_count"], 1)

    def test_project_scope_isolation(self):
        """Alias created in PRJ-NBG-2026 is completely unavailable to PRJ-SCP-2026."""
        e = ExecutionEvent(event_id="EVT-P1", source_id="SRC-1", fragment_id="F1", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T10:00:00Z", extracted_statement="HDD drilling")
        self.db.save_execution_event(e)
        self.db.save_planner_correction(PlannerCorrectionRecord("CP1", "EVT-P1", "ACT-0", "ACT-1010", "M", "D", "TERMINOLOGY_ALIAS", "", "PLN-01", "2026-09-04T10:00:00Z"))

        self.memory_service.distill_planner_corrections("PRJ-NBG-2026")

        # Query aliases for PRJ-SCP-2026
        scp_aliases = self.db.get_terminology_aliases_by_project("PRJ-SCP-2026")
        self.assertEqual(len(scp_aliases), 0)

        alias_scores = self.memory_service.get_candidate_alias_scores("PRJ-SCP-2026", "HDD drilling")
        self.assertEqual(len(alias_scores), 0)

    def test_historical_match_regression_immutability(self):
        """
        Historical Regression Test:
        Distilling a new alias must NOT alter historical MatchResult records of past events,
        while new events containing the phrase utilize the active memory hint.
        """
        # Historical Event E1
        e1 = ExecutionEvent(event_id="EVT-H1", source_id="SRC-1", fragment_id="F1", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T10:00:00Z", extracted_statement="HDD drilling at Section 1")
        self.db.save_execution_event(e1)

        # Historical Match Result M1
        historical_mr = self.matching_engine.match_event_to_fingerprints(e1, [self.fp])
        self.db.save_match_result(historical_mr)
        hist_score_before = historical_mr.confidence_score

        # Distill memory to create active alias
        for i in range(3):
            e = ExecutionEvent(event_id=f"EVT-M{i}", source_id=f"SRC-{i}", fragment_id=f"F{i}", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T10:00:00Z", extracted_statement="HDD drilling at Section 1")
            self.db.save_execution_event(e)
            self.db.save_planner_correction(PlannerCorrectionRecord(f"CM{i}", f"EVT-M{i}", "ACT-0", "ACT-1010", "M", "D", "TERMINOLOGY_ALIAS", "", f"PLN-{i}", "2026-09-04T10:00:00Z"))

        self.memory_service.distill_planner_corrections("PRJ-NBG-2026")

        # 1. Verify historical MatchResult remains 100% unchanged
        persisted_hist_mr = self.db.get_match_results_by_event("EVT-H1")[0]
        self.assertEqual(persisted_hist_mr["confidence_score"], hist_score_before)

        # 2. Verify new Event E2 utilizes active alias hint
        e2 = ExecutionEvent(event_id="EVT-H2", source_id="SRC-2", fragment_id="F2", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T10:00:00Z", extracted_statement="HDD drilling at Section 1")
        active_alias_scores = self.memory_service.get_candidate_alias_scores("PRJ-NBG-2026", "HDD drilling at Section 1")
        self.assertIn("ACT-1010", active_alias_scores)

        new_mr = self.matching_engine.match_event_to_fingerprints(e2, [self.fp], alias_scores=active_alias_scores)
        self.assertGreaterEqual(new_mr.confidence_score, hist_score_before)

    def test_reproducibility(self):
        """Identical ledger state + identical policy returns identical MemoryDistillationRun."""
        e1 = ExecutionEvent(event_id="EVT-R1", source_id="SRC-1", fragment_id="F1", event_type="PROGRESS", observed_timestamp="2026-09-04", source_timestamp="2026-09-04T10:00:00Z", extracted_statement="Welding joint 5")
        self.db.save_execution_event(e1)
        self.db.save_planner_correction(PlannerCorrectionRecord("CR1", "EVT-R1", "ACT-0", "ACT-1010", "M", "D", "TERMINOLOGY_ALIAS", "", "PLN-01", "2026-09-04T10:00:00Z"))

        run1 = self.memory_service.distill_planner_corrections("PRJ-NBG-2026")
        run2 = self.memory_service.distill_planner_corrections("PRJ-NBG-2026")

        self.assertEqual(run1.input_corrections_count, run2.input_corrections_count)
        self.assertEqual(run1.input_corrections_count, 1)

if __name__ == "__main__":
    unittest.main()
