"""
SATYA Schedule Projection & Actual Progress Engine Unit Tests (Phase 10)
Verifies calculation policies, cumulative vs delta quantities, null-safe forecasting,
WBS weighting, baseline immutability, and deterministic recomputation.
"""

import os
import json
import hashlib
import unittest
from datetime import datetime

from backend.models.domain_models import (
    ExecutionEvent, TrustAssessment, TrustStatus, EventType,
    ProgressCalculationPolicy, QuantityObservationType, ProgressCalculationStatus,
    ForecastStatus, ProgressWeightPolicy, ActivityProgressStatus, QAClearanceStatus,
    ActivityProgress, WBSProgress, ScheduleProjection
)
from backend.projection.actual_progress_engine import ActualProgressEngine

class TestScheduleProjectionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ActualProgressEngine()
        self.as_of_date = "2026-09-10"

        # Baseline schedule activity template
        self.base_activity = {
            "activity_id": "ACT-1010",
            "activity_name": "Mainline ROW Clearing & Grading Sec 1",
            "wbs_id": "WBS-310",
            "discipline": "CIVIL",
            "planned_start": "2026-09-01",
            "planned_finish": "2026-09-05",
            "baseline_duration_days": 4,
            "planned_quantity": 2000.0,
            "unit": "Meters",
            "is_critical": True
        }

    def test_cumulative_vs_delta_quantity_aggregation(self):
        # Case A: Cumulative Total sequence (200m -> 350m -> 500m)
        ev_cum1 = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Completed 200m total", observed_quantity=200.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-02T10:00:00"
        )
        ev_cum2 = ExecutionEvent(
            event_id="EVT-02", source_id="SRC-2", fragment_id="FRG-2",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-03T10:00:00",
            extracted_statement="Completed 350m total", observed_quantity=350.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-03T10:00:00"
        )
        ev_cum3 = ExecutionEvent(
            event_id="EVT-03", source_id="SRC-3", fragment_id="FRG-3",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-04T10:00:00",
            extracted_statement="Completed 500m total", observed_quantity=500.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-04T10:00:00"
        )

        obs_type, total_qty = self.engine.resolve_quantity_aggregation([ev_cum1, ev_cum2, ev_cum3])
        self.assertEqual(obs_type, QuantityObservationType.CUMULATIVE_TOTAL)
        self.assertEqual(total_qty, 500.0)

        # Case B: Daily Delta sequence (+200m, +150m, +150m)
        ev_del1 = ExecutionEvent(
            event_id="EVT-11", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Daily progress 200m today", observed_quantity=200.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-02T10:00:00"
        )
        ev_del2 = ExecutionEvent(
            event_id="EVT-12", source_id="SRC-2", fragment_id="FRG-2",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-03T10:00:00",
            extracted_statement="Daily progress 150m today", observed_quantity=150.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-03T10:00:00"
        )
        ev_del3 = ExecutionEvent(
            event_id="EVT-13", source_id="SRC-3", fragment_id="FRG-3",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-04T10:00:00",
            extracted_statement="Daily progress 150m today", observed_quantity=150.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-04T10:00:00"
        )

        obs_type, total_qty = self.engine.resolve_quantity_aggregation([ev_del1, ev_del2, ev_del3])
        self.assertEqual(obs_type, QuantityObservationType.DAILY_DELTA)
        self.assertEqual(total_qty, 500.0)

    def test_duplicate_cumulative_observations(self):
        ev1 = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-04T10:00:00",
            extracted_statement="Completed 500m total", observed_quantity=500.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-04T10:00:00"
        )
        ev2 = ExecutionEvent(
            event_id="EVT-02", source_id="SRC-2", fragment_id="FRG-2",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-05T10:00:00",
            extracted_statement="Completed 500m total", observed_quantity=500.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-05T10:00:00"
        )
        obs_type, total_qty = self.engine.resolve_quantity_aggregation([ev1, ev2])
        self.assertEqual(obs_type, QuantityObservationType.CUMULATIVE_TOTAL)
        self.assertEqual(total_qty, 500.0)

    def test_unit_mismatch_handling(self):
        # Fluctuating quantities without explicit delta keywords -> UNKNOWN
        ev1 = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Report 500m", observed_quantity=500.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-02T10:00:00"
        )
        ev2 = ExecutionEvent(
            event_id="EVT-02", source_id="SRC-2", fragment_id="FRG-2",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-03T10:00:00",
            extracted_statement="Report 300m", observed_quantity=300.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-03T10:00:00"
        )
        obs_type, total_qty = self.engine.resolve_quantity_aggregation([ev1, ev2])
        self.assertEqual(obs_type, QuantityObservationType.UNKNOWN)
        self.assertIsNone(total_qty)

    def test_zero_planned_quantity_handling(self):
        activity = dict(self.base_activity, planned_quantity=0.0, unit="Milestone")
        policy = self.engine.determine_calculation_policy(activity)
        self.assertEqual(policy, ProgressCalculationPolicy.MILESTONE_BASED)

    def test_zero_execution_rate_forecast_null(self):
        ev1 = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Progress 200m", observed_quantity=200.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-02T10:00:00"
        )
        ev2 = ExecutionEvent(
            event_id="EVT-02", source_id="SRC-2", fragment_id="FRG-2",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-05T10:00:00",
            extracted_statement="Progress 200m", observed_quantity=200.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-05T10:00:00"
        )
        prog = self.engine.calculate_activity_progress(self.base_activity, [ev1, ev2], [], self.as_of_date)
        self.assertEqual(prog.forecast_status, ForecastStatus.ZERO_RATE)
        self.assertIsNone(prog.forecast_finish)

    def test_one_point_forecast_history_insufficient(self):
        ev1 = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Progress 500m", observed_quantity=500.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-02T10:00:00"
        )
        prog = self.engine.calculate_activity_progress(self.base_activity, [ev1], [], self.as_of_date)
        self.assertEqual(prog.forecast_status, ForecastStatus.INSUFFICIENT_HISTORY)
        self.assertIsNone(prog.forecast_finish)

    def test_insufficient_forecast_history_null_forecast(self):
        # No timestamps attached -> cannot compute rate
        ev1 = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Progress 200m", observed_quantity=200.0,
            observed_activity_id="ACT-1010", observed_timestamp=None
        )
        ev2 = ExecutionEvent(
            event_id="EVT-02", source_id="SRC-2", fragment_id="FRG-2",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-03T10:00:00",
            extracted_statement="Progress 400m", observed_quantity=400.0,
            observed_activity_id="ACT-1010", observed_timestamp=None
        )
        prog = self.engine.calculate_activity_progress(self.base_activity, [ev1, ev2], [], self.as_of_date)
        self.assertEqual(prog.forecast_status, ForecastStatus.INSUFFICIENT_HISTORY)
        self.assertIsNone(prog.forecast_finish)

    def test_paused_held_activity_forecast(self):
        ev_start = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.START, source_timestamp="2026-09-01T10:00:00",
            extracted_statement="Start ROW clearing", observed_quantity=100.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-01T10:00:00"
        )
        prog = self.engine.calculate_activity_progress(self.base_activity, [ev_start], [], self.as_of_date)
        self.assertEqual(prog.status, ActivityProgressStatus.IN_PROGRESS)
        self.assertEqual(prog.forecast_status, ForecastStatus.INSUFFICIENT_HISTORY)
        self.assertIsNone(prog.forecast_finish)

    def test_completion_with_pending_qa_clearance(self):
        ev_finish = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.FINISH, source_timestamp="2026-09-04T10:00:00",
            extracted_statement="Mainline ROW clearing 2000m completed. QA pending.",
            observed_quantity=2000.0, observed_activity_id="ACT-1010",
            observed_timestamp="2026-09-04T10:00:00", pending_qa_clearance=True
        )
        prog = self.engine.calculate_activity_progress(self.base_activity, [ev_finish], [], self.as_of_date)
        self.assertEqual(prog.physical_progress_pct, 100.0)
        self.assertEqual(prog.status, ActivityProgressStatus.COMPLETED)
        self.assertEqual(prog.qa_clearance_status, QAClearanceStatus.PENDING)

    def test_non_quantity_milestone_status_activity(self):
        ms_activity = {
            "activity_id": "ACT-MS-01",
            "activity_name": "Site Handover Milestone",
            "wbs_id": "WBS-100",
            "discipline": "CIVIL",
            "planned_start": "2026-09-01",
            "planned_finish": "2026-09-01",
            "baseline_duration_days": 0,
            "planned_quantity": None,
            "unit": "Milestone",
            "is_critical": True
        }
        ev_finish = ExecutionEvent(
            event_id="EVT-MS", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.FINISH, source_timestamp="2026-09-01T10:00:00",
            extracted_statement="Site Handover Milestone achieved",
            observed_activity_id="ACT-MS-01", observed_timestamp="2026-09-01T10:00:00"
        )
        prog = self.engine.calculate_activity_progress(ms_activity, [ev_finish], [], self.as_of_date)
        self.assertEqual(prog.calculation_policy, ProgressCalculationPolicy.MILESTONE_BASED)
        self.assertEqual(prog.physical_progress_pct, 100.0)
        self.assertEqual(prog.status, ActivityProgressStatus.COMPLETED)

    def test_mixed_unit_wbs_rollup(self):
        wbs_hierarchy = [{"wbs_id": "WBS-310", "wbs_code": "NBG.PL.SEC1", "wbs_name": "Section 1", "level": 3}]
        activities = [
            dict(self.base_activity, activity_id="ACT-1", unit="Meters", baseline_duration_days=4),
            dict(self.base_activity, activity_id="ACT-2", unit="Joints", baseline_duration_days=6)
        ]
        prog1 = ActivityProgress(
            activity_id="ACT-1", status=ActivityProgressStatus.COMPLETED,
            calculation_policy=ProgressCalculationPolicy.QUANTITY_BASED,
            calculation_status=ProgressCalculationStatus.CALCULATED,
            forecast_status=ForecastStatus.COMPLETED, physical_progress_pct=100.0
        )
        prog2 = ActivityProgress(
            activity_id="ACT-2", status=ActivityProgressStatus.IN_PROGRESS,
            calculation_policy=ProgressCalculationPolicy.QUANTITY_BASED,
            calculation_status=ProgressCalculationStatus.CALCULATED,
            forecast_status=ForecastStatus.AVAILABLE, physical_progress_pct=50.0
        )
        wbs_map = self.engine.calculate_wbs_rollups(wbs_hierarchy, {"ACT-1": prog1, "ACT-2": prog2}, activities)
        wbs_res = wbs_map["WBS-310"]
        self.assertIsNone(wbs_res.physical_progress_pct)  # Mixed units -> physical avg is None
        # Weighted progress: (100 * 4 + 50 * 6) / 10 = 70.0%
        self.assertEqual(wbs_res.weighted_progress_pct, 70.0)

    def test_missing_weighting_basis_null_wbs_progress(self):
        wbs_hierarchy = [{"wbs_id": "WBS-EMPTY", "wbs_code": "EMPTY", "wbs_name": "Empty Node", "level": 1}]
        wbs_map = self.engine.calculate_wbs_rollups(wbs_hierarchy, {}, [])
        self.assertEqual(wbs_map["WBS-EMPTY"].weighted_progress_pct, 0.0)
        self.assertEqual(wbs_map["WBS-EMPTY"].activities_count, 0)

    def test_incomplete_activity_unavailable_forecast_null_finish_variance(self):
        ev1 = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.START, source_timestamp="2026-09-01T10:00:00",
            extracted_statement="Start ROW clearing", observed_quantity=100.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-01T10:00:00"
        )
        prog = self.engine.calculate_activity_progress(self.base_activity, [ev1], [], self.as_of_date)
        self.assertEqual(prog.status, ActivityProgressStatus.IN_PROGRESS)
        self.assertIsNone(prog.forecast_finish)
        self.assertIsNone(prog.finish_variance_days)

    def test_critical_activity_projected_delay(self):
        # Baseline finish 2026-09-05. Forecast finish 2026-09-20 (15 days delay)
        ev1 = ExecutionEvent(
            event_id="EVT-01", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-01T10:00:00",
            extracted_statement="Daily progress 100m", observed_quantity=100.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-01T10:00:00"
        )
        ev2 = ExecutionEvent(
            event_id="EVT-02", source_id="SRC-2", fragment_id="FRG-2",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-03T10:00:00",
            extracted_statement="Daily progress 200m", observed_quantity=300.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-03T10:00:00"
        )
        prog = self.engine.calculate_activity_progress(self.base_activity, [ev1, ev2], [], "2026-09-03")
        self.assertTrue(prog.is_critical)
        self.assertTrue(prog.critical_activity_projected_delay)
        self.assertGreater(prog.finish_variance_days, 0.0)

    def test_untrusted_event_exclusion(self):
        ev_trusted = ExecutionEvent(
            event_id="EVT-T", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Trusted 500m completed", observed_quantity=500.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-02T10:00:00"
        )
        ev_untrusted = ExecutionEvent(
            event_id="EVT-U", source_id="SRC-2", fragment_id="FRG-2",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-03T10:00:00",
            extracted_statement="Unverified claim 1500m completed", observed_quantity=1500.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-03T10:00:00"
        )
        trust_assessments = [
            {"event_id": "EVT-T", "trust_status": TrustStatus.TRUSTED, "version_index": 1},
            {"event_id": "EVT-U", "trust_status": TrustStatus.UNTRUSTED, "version_index": 1}
        ]
        trusted, unverified = self.engine.filter_trusted_events([ev_trusted, ev_untrusted], trust_assessments)
        self.assertEqual(len(trusted), 1)
        self.assertEqual(trusted[0].event_id, "EVT-T")
        self.assertEqual(len(unverified), 1)
        self.assertEqual(unverified[0].event_id, "EVT-U")

        prog = self.engine.calculate_activity_progress(self.base_activity, trusted, unverified, self.as_of_date)
        self.assertEqual(prog.actual_quantity, 500.0)
        self.assertEqual(prog.unverified_event_count, 1)
        self.assertEqual(prog.unverified_reported_quantity, 1500.0)

    def test_baseline_file_content_hash_unchanged(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedule_path = os.path.join(base_dir, "data", "synthetic", "schedules", "baseline_schedule.json")
        
        with open(schedule_path, "rb") as f:
            hash_before = hashlib.sha256(f.read()).hexdigest()

        with open(schedule_path, "r", encoding="utf-8") as f:
            sched_data = json.load(f)

        # Run projection engine
        self.engine.generate_projection(
            project_id=sched_data["project"]["project_id"],
            activities=sched_data["activities"],
            wbs_hierarchy=sched_data["wbs_hierarchy"],
            events=[], trust_assessments=[], as_of_date=self.as_of_date
        )

        with open(schedule_path, "rb") as f:
            hash_after = hashlib.sha256(f.read()).hexdigest()

        self.assertEqual(hash_before, hash_after)

    def test_projection_recomputation_deterministic(self):
        ev = ExecutionEvent(
            event_id="EVT-DET", source_id="SRC-1", fragment_id="FRG-1",
            event_type=EventType.PROGRESS, source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Daily 500m completed", observed_quantity=500.0,
            observed_activity_id="ACT-1010", observed_timestamp="2026-09-02T10:00:00"
        )
        trust_assessments = [{"event_id": "EVT-DET", "trust_status": TrustStatus.TRUSTED, "version_index": 1}]

        p1 = self.engine.generate_projection(
            project_id="PRJ-NBG-2026", activities=[self.base_activity],
            wbs_hierarchy=[{"wbs_id": "WBS-310", "wbs_code": "NBG.PL.SEC1", "wbs_name": "Sec 1", "level": 3}],
            events=[ev], trust_assessments=trust_assessments, as_of_date=self.as_of_date
        )

        p2 = self.engine.generate_projection(
            project_id="PRJ-NBG-2026", activities=[self.base_activity],
            wbs_hierarchy=[{"wbs_id": "WBS-310", "wbs_code": "NBG.PL.SEC1", "wbs_name": "Sec 1", "level": 3}],
            events=[ev], trust_assessments=trust_assessments, as_of_date=self.as_of_date
        )

        self.assertEqual(p1.overall_project_progress_pct, p2.overall_project_progress_pct)
        self.assertEqual(p1.completed_activities, p2.completed_activities)
        self.assertEqual(p1.in_progress_activities, p2.in_progress_activities)
        self.assertEqual(p1.activity_progress_map["ACT-1010"].physical_progress_pct, p2.activity_progress_map["ACT-1010"].physical_progress_pct)

if __name__ == "__main__":
    unittest.main()
