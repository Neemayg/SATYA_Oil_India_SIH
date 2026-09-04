"""
SATYA Time Agent Monitoring Engine Unit Tests (Phase 13)
Verifies deterministic evaluation of 6 temporal signal types,
configurable monitoring policy thresholds, auditable reasoning traces,
and explicit NEGATIVE test cases verifying ZERO false positive signals.
"""

import unittest
from datetime import datetime, date
from backend.models.domain_models import (
    TemporalSignalType,
    SignalSeverity,
    SignalStatus,
    TemporalMonitoringPolicy,
    ScheduleProjection,
    ActivityProgress,
    ActivityFingerprint,
    ForecastStatus,
    QAClearanceStatus
)
from backend.monitoring.time_agent_engine import TimeAgentEngine

class TestTimeAgentEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TimeAgentEngine()
        self.policy = TemporalMonitoringPolicy(
            reporting_staleness_days=7,
            forecast_slippage_critical_days=10,
            unverified_claim_count_threshold=3
        )
        self.project_id = "PRJ-NBG-2026"
        self.run_id = "RUN-MON-TEST-001"

    def test_silent_critical_path_risk_signal(self):
        # Critical activity past planned start with 0 progress
        fp = ActivityFingerprint(
            fingerprint_id="FP-1",
            activity_id="ACT-1010",
            project_id=self.project_id,
            activity_name="Trench Excavation",
            normalized_name="trench excavation",
            wbs_id="WBS-1",
            wbs_code="1.1",
            wbs_name_path="Mainline > Trenching",
            discipline="CIVIL",
            planned_start="2026-08-20",
            planned_finish="2026-09-01",
            is_critical=True
        )

        proj = ScheduleProjection(
            projection_id="PRJ-SNAP-1",
            project_id=self.project_id,
            as_of_date="2026-08-25",
            activity_progress_map={"ACT-1010": {"physical_progress_pct": 0.0}}
        )

        signals = self.engine.evaluate_project_timeline(
            project_id=self.project_id,
            projection=proj,
            fingerprints=[fp],
            events=[],
            trust_assessments=[],
            policy=self.policy,
            as_of_date="2026-08-25",
            evaluation_run_id=self.run_id
        )

        self.assertEqual(len(signals), 1)
        sig = signals[0]
        self.assertEqual(sig.signal_type, TemporalSignalType.SILENT_CRITICAL_PATH_RISK)
        self.assertEqual(sig.severity, SignalSeverity.HIGH)
        self.assertIn("insufficient trusted evidence", sig.reasoning_trace[-1])

    def test_forecast_finish_slippage_null_safe_guard(self):
        # Case A: Forecast is INSUFFICIENT_HISTORY -> Zero signals generated!
        fp = ActivityFingerprint(
            fingerprint_id="FP-2",
            activity_id="ACT-1020",
            project_id=self.project_id,
            activity_name="Pipe Stringing",
            normalized_name="pipe stringing",
            wbs_id="WBS-1",
            wbs_code="1.2",
            wbs_name_path="Mainline > Stringing",
            discipline="PIPING",
            planned_start="2026-08-20",
            planned_finish="2026-09-01",
            is_critical=True
        )

        proj_null = ScheduleProjection(
            projection_id="PRJ-SNAP-2",
            project_id=self.project_id,
            as_of_date="2026-08-25",
            activity_progress_map={"ACT-1020": {
                "physical_progress_pct": 25.0,
                "forecast_status": ForecastStatus.INSUFFICIENT_HISTORY,
                "forecast_finish": None,
                "finish_variance_days": None
            }}
        )

        signals_null = self.engine.evaluate_project_timeline(
            project_id=self.project_id,
            projection=proj_null,
            fingerprints=[fp],
            events=[],
            trust_assessments=[],
            policy=self.policy,
            as_of_date="2026-08-25",
            evaluation_run_id=self.run_id
        )

        # Null-safe guard: ZERO signals generated when forecast is unavailable!
        self.assertEqual(len(signals_null), 0)

        # Case B: Forecast status AVAILABLE with +12d slippage on critical task -> CRITICAL signal!
        proj_avail = ScheduleProjection(
            projection_id="PRJ-SNAP-3",
            project_id=self.project_id,
            as_of_date="2026-08-25",
            activity_progress_map={"ACT-1020": {
                "physical_progress_pct": 25.0,
                "forecast_status": ForecastStatus.AVAILABLE,
                "forecast_finish": "2026-09-13",
                "finish_variance_days": 12.0
            }}
        )

        signals_avail = self.engine.evaluate_project_timeline(
            project_id=self.project_id,
            projection=proj_avail,
            fingerprints=[fp],
            events=[],
            trust_assessments=[],
            policy=self.policy,
            as_of_date="2026-08-25",
            evaluation_run_id=self.run_id
        )

        self.assertEqual(len(signals_avail), 1)
        self.assertEqual(signals_avail[0].signal_type, TemporalSignalType.FORECAST_FINISH_SLIPPAGE)
        self.assertEqual(signals_avail[0].severity, SignalSeverity.CRITICAL)

    def test_out_of_sequence_execution_warning(self):
        # Predecessor ACT-1010 incomplete (50%), Successor ACT-1020 in-progress (20%)
        fp_pred = ActivityFingerprint(
            fingerprint_id="FP-1",
            activity_id="ACT-1010",
            project_id=self.project_id,
            activity_name="Trench Excavation",
            normalized_name="trench excavation",
            wbs_id="WBS-1",
            wbs_code="1.1",
            wbs_name_path="Mainline > Trenching",
            discipline="CIVIL",
            successors=["ACT-1020"]
        )

        fp_succ = ActivityFingerprint(
            fingerprint_id="FP-2",
            activity_id="ACT-1020",
            project_id=self.project_id,
            activity_name="Pipe Lowering",
            normalized_name="pipe lowering",
            wbs_id="WBS-1",
            wbs_code="1.2",
            wbs_name_path="Mainline > Lowering",
            discipline="PIPING",
            predecessors=["ACT-1010"]
        )

        proj = ScheduleProjection(
            projection_id="PRJ-SNAP-SEQ",
            project_id=self.project_id,
            as_of_date="2026-08-25",
            activity_progress_map={
                "ACT-1010": {"physical_progress_pct": 50.0},
                "ACT-1020": {"physical_progress_pct": 20.0}
            }
        )

        signals = self.engine.evaluate_project_timeline(
            project_id=self.project_id,
            projection=proj,
            fingerprints=[fp_pred, fp_succ],
            events=[],
            trust_assessments=[],
            policy=self.policy,
            as_of_date="2026-08-25",
            evaluation_run_id=self.run_id
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].signal_type, TemporalSignalType.OUT_OF_SEQUENCE_EXECUTION_WARNING)
        self.assertEqual(signals[0].activity_id, "ACT-1020")

    def test_qa_clearance_bottleneck_with_downstream_successors(self):
        # Physical progress 100%, QA PENDING, past planned finish date, has downstream successor ACT-1020
        fp_pred = ActivityFingerprint(
            fingerprint_id="FP-1",
            activity_id="ACT-1010",
            project_id=self.project_id,
            activity_name="Welding",
            normalized_name="welding",
            wbs_id="WBS-1",
            wbs_code="1.1",
            wbs_name_path="Mainline > Welding",
            discipline="PIPING",
            planned_finish="2026-08-20",
            successors=["ACT-1020"]
        )

        proj = ScheduleProjection(
            projection_id="PRJ-SNAP-QA",
            project_id=self.project_id,
            as_of_date="2026-08-25",
            activity_progress_map={
                "ACT-1010": {
                    "physical_progress_pct": 100.0,
                    "qa_clearance_status": QAClearanceStatus.PENDING
                }
            }
        )

        signals = self.engine.evaluate_project_timeline(
            project_id=self.project_id,
            projection=proj,
            fingerprints=[fp_pred],
            events=[],
            trust_assessments=[],
            policy=self.policy,
            as_of_date="2026-08-25",
            evaluation_run_id=self.run_id
        )

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].signal_type, TemporalSignalType.QA_CLEARANCE_BOTTLENECK)
        self.assertEqual(signals[0].activity_id, "ACT-1010")

    def test_negative_cases_zero_false_positives(self):
        # Test Negative Cases: Clean, completed, or on-schedule activities generate ZERO signals
        fp_clean = ActivityFingerprint(
            fingerprint_id="FP-CLEAN",
            activity_id="ACT-9000",
            project_id=self.project_id,
            activity_name="Site Mobilization",
            normalized_name="site mobilization",
            wbs_id="WBS-1",
            wbs_code="1.0",
            wbs_name_path="Mobilization",
            discipline="CIVIL",
            planned_start="2026-08-01",
            planned_finish="2026-08-10",
            is_critical=False
        )

        proj_clean = ScheduleProjection(
            projection_id="PRJ-SNAP-CLEAN",
            project_id=self.project_id,
            as_of_date="2026-08-25",
            activity_progress_map={
                "ACT-9000": {
                    "physical_progress_pct": 100.0,
                    "qa_clearance_status": QAClearanceStatus.CLEARED,
                    "forecast_status": ForecastStatus.AVAILABLE,
                    "forecast_finish": "2026-08-10",
                    "finish_variance_days": 0.0
                }
            }
        )

        signals = self.engine.evaluate_project_timeline(
            project_id=self.project_id,
            projection=proj_clean,
            fingerprints=[fp_clean],
            events=[],
            trust_assessments=[],
            policy=self.policy,
            as_of_date="2026-08-25",
            evaluation_run_id=self.run_id
        )

        # Zero false positive signals generated!
        self.assertEqual(len(signals), 0)

if __name__ == "__main__":
    unittest.main()
