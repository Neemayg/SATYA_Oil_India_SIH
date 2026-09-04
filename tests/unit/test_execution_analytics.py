"""
SATYA Execution Analytics Unit Tests (Phase 14)
Verifies UOM-safe productivity rate benchmarks, sample thresholds,
contractor reporting latency, and conflict resolution pathway analytics.
"""

import unittest
from backend.persistence.database_engine import DatabaseEngine
from backend.analytics.analytics_engine import ExecutionAnalyticsEngine
from backend.models.domain_models import (
    ExecutionEvent, ScheduleProjection, ActivityProgress,
    BenchmarkStatus, InstitutionalMemoryPolicy, ValidationDecision
)

class TestExecutionAnalyticsEngine(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.policy = InstitutionalMemoryPolicy(min_provisional_sample=3, min_validated_sample=10)
        self.analytics_engine = ExecutionAnalyticsEngine(self.db, self.policy)

    def test_sample_size_policy_thresholds(self):
        """Sample size count N dictates BenchmarkStatus (INSUFFICIENT_SAMPLE vs PROVISIONAL vs VALIDATED)."""
        # Create projection with activity progress
        act_map = {
            "ACT-1010": ActivityProgress(
                activity_id="ACT-1010",
                status="IN_PROGRESS",
                calculation_policy="QUANTITY_BASED",
                calculation_status="CALCULATED",
                forecast_status="AVAILABLE",
                unit="m",
                planned_quantity=100.0,
                actual_quantity=50.0
            ).to_dict()
        }
        proj = ScheduleProjection(
            projection_id="PROJ-001",
            project_id="PRJ-NBG-2026",
            as_of_date="2026-09-04",
            activity_progress_map=act_map
        )
        self.db.save_schedule_projection(proj)

        # 1. 2 events -> INSUFFICIENT_SAMPLE
        for i in range(2):
            e = ExecutionEvent(
                event_id=f"EVT-A{i}",
                source_id=f"SRC-{i}",
                fragment_id=f"F{i}",
                event_type="PROGRESS",
                observed_timestamp="2026-09-04",
                source_timestamp="2026-09-04T10:00:00Z",
                extracted_statement="Excavation 10m",
                observed_activity_id="ACT-1010",
                observed_quantity=10.0
            )
            self.db.save_execution_event(e)

        benchmarks = self.analytics_engine.compute_execution_rate_benchmarks("PRJ-NBG-2026")
        self.assertEqual(len(benchmarks), 1)
        self.assertEqual(benchmarks[0].benchmark_status, BenchmarkStatus.INSUFFICIENT_SAMPLE)

        # 2. Add 2 more events -> 4 events -> PROVISIONAL
        for i in range(2, 4):
            e = ExecutionEvent(
                event_id=f"EVT-A{i}",
                source_id=f"SRC-{i}",
                fragment_id=f"F{i}",
                event_type="PROGRESS",
                observed_timestamp="2026-09-04",
                source_timestamp="2026-09-04T10:00:00Z",
                extracted_statement="Excavation 10m",
                observed_activity_id="ACT-1010",
                observed_quantity=10.0
            )
            self.db.save_execution_event(e)

        benchmarks_prov = self.analytics_engine.compute_execution_rate_benchmarks("PRJ-NBG-2026")
        self.assertEqual(benchmarks_prov[0].benchmark_status, BenchmarkStatus.PROVISIONAL)

    def test_null_planned_rate_safety(self):
        """Missing quantity or duration returns planned_rate = None (not zero)."""
        act_map = {
            "ACT-1020": ActivityProgress(
                activity_id="ACT-1020",
                status="COMPLETED",
                calculation_policy="MILESTONE_BASED",
                calculation_status="CALCULATED",
                forecast_status="COMPLETED",
                unit="m",
                planned_quantity=0.0,  # Zero planned qty
                actual_quantity=10.0
            ).to_dict()
        }
        proj = ScheduleProjection(
            projection_id="PROJ-002",
            project_id="PRJ-NBG-2026",
            as_of_date="2026-09-04",
            activity_progress_map=act_map
        )
        self.db.save_schedule_projection(proj)

        benchmarks = self.analytics_engine.compute_execution_rate_benchmarks("PRJ-NBG-2026")
        self.assertEqual(len(benchmarks), 0)  # Planned qty 0 skipped per UOM rules

    def test_contractor_reporting_latency_calculation(self):
        """reporting_delay_days = t_reported - t_observed. Missing timestamps return None."""
        e1 = ExecutionEvent(
            event_id="EVT-C1",
            source_id="SRC-1",
            fragment_id="F1",
            event_type="PROGRESS",
            source_timestamp="2026-09-04T12:00:00Z",
            observed_timestamp="2026-09-02T12:00:00Z",  # 2 days latency
            extracted_statement="Contractor report",
            status_text="CONTRACTOR-ALPHA"
        )
        self.db.save_execution_event(e1)

        profiles = self.analytics_engine.compute_contractor_reporting_profiles("PRJ-NBG-2026")
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].contractor_id, "CONTRACTOR-ALPHA")
        self.assertEqual(profiles[0].verification_ratio, 1.0)
        self.assertAlmostEqual(profiles[0].avg_reporting_delay_days, 2.0, places=1)

    def test_acknowledged_vs_resolved_signal_separation(self):
        """Time Agent ACKNOWLEDGED status is tracked separately from physical RESOLVED conditions."""
        # Save validation decisions
        v1 = ValidationDecision(
            decision_id="DEC-001",
            event_id="EVT-001",
            planner_id="PLN-01",
            decision_type="VALIDATE",
            reviewed_trust_version=1,
            reviewed_match_result_id="MTH-1",
            reviewed_evidence_assessment_id="EVD-1",
            override_reason_category="QA_OVERRIDE"
        )
        self.db.save_validation_decision(v1)

        patterns = self.analytics_engine.compute_conflict_resolution_patterns("PRJ-NBG-2026")
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].conflict_or_signal_type, "QA_OVERRIDE")
        self.assertEqual(patterns[0].validated_count, 1)

if __name__ == "__main__":
    unittest.main()
