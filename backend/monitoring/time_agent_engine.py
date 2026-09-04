"""
SATYA Time Agent Core Engine (Phase 13)
Deterministic Temporal Monitoring Engine evaluating temporal conditions, schedule relationships,
and evidence status under a configurable TemporalMonitoringPolicy.
Enforces strict as_of_date temporal bounding and generates auditable TemporalWarningSignals.
"""

import uuid
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from backend.models.domain_models import (
    TemporalSignalType,
    SignalSeverity,
    SignalStatus,
    TemporalMonitoringPolicy,
    TemporalWarningSignal,
    ScheduleProjection,
    ActivityFingerprint,
    ForecastStatus,
    QAClearanceStatus
)

logger = logging.getLogger("SATYA.TimeAgentEngine")

class TimeAgentEngine:
    """
    Deterministic Temporal Monitoring Engine.
    Evaluates 6 temporal signal rules against schedule projections, fingerprints, and evidence records.
    """

    def evaluate_project_timeline(
        self,
        project_id: str,
        projection: ScheduleProjection,
        fingerprints: List[ActivityFingerprint],
        events: List[Dict[str, Any]],
        trust_assessments: List[Dict[str, Any]],
        policy: TemporalMonitoringPolicy,
        as_of_date: str,
        evaluation_run_id: str
    ) -> List[TemporalWarningSignal]:
        """
        Evaluates project timeline and returns a list of auditable TemporalWarningSignals.
        Enforces strict as_of_date temporal bounding (events after as_of_date are excluded).
        """
        dt_as_of = datetime.strptime(as_of_date, "%Y-%m-%d").date()
        signals: List[TemporalWarningSignal] = []

        # 1. Strictly bound events to as_of_date
        bounded_events = []
        for ev in events:
            obs_ts = ev.get("observed_timestamp") or ev.get("source_timestamp", "")
            if obs_ts:
                try:
                    dt_obs = datetime.strptime(obs_ts.split("T")[0], "%Y-%m-%d").date()
                    if dt_obs <= dt_as_of:
                        bounded_events.append(ev)
                except ValueError:
                    bounded_events.append(ev)

        # Build activity progress lookup map
        act_prog_map = projection.activity_progress_map or {}
        fp_map = {fp.activity_id: fp for fp in fingerprints}

        # Build predecessor / successor graph lookup
        predecessors_map: Dict[str, List[str]] = {fp.activity_id: fp.predecessors for fp in fingerprints}
        successors_map: Dict[str, List[str]] = {fp.activity_id: fp.successors for fp in fingerprints}

        # Group bounded events by activity ID
        events_by_act: Dict[str, List[Dict[str, Any]]] = {}
        for ev in bounded_events:
            act_id = ev.get("observed_activity_id") or ev.get("raw_observed_activity_id")
            if act_id:
                if act_id not in events_by_act:
                    events_by_act[act_id] = []
                events_by_act[act_id].append(ev)

        # Evaluate each activity fingerprint against policy rules
        for fp in fingerprints:
            act_id = fp.activity_id
            prog_dict = act_prog_map.get(act_id, {})

            phys_pct = prog_dict.get("physical_progress_pct") if prog_dict.get("physical_progress_pct") is not None else 0.0
            qa_status = prog_dict.get("qa_clearance_status")
            forecast_status = prog_dict.get("forecast_status")
            forecast_finish = prog_dict.get("forecast_finish")
            finish_variance_days = prog_dict.get("finish_variance_days")
            is_critical = fp.is_critical

            dt_planned_start = datetime.strptime(fp.planned_start, "%Y-%m-%d").date() if fp.planned_start else None
            dt_planned_finish = datetime.strptime(fp.planned_finish, "%Y-%m-%d").date() if fp.planned_finish else None

            act_events = events_by_act.get(act_id, [])
            unverified_count = prog_dict.get("unverified_event_count", 0)

            # -------------------------------------------------------------
            # RULE 1: SILENT_CRITICAL_PATH_RISK
            # Critical activity past planned start with 0 progress or no trusted evidence
            # -------------------------------------------------------------
            if is_critical and dt_planned_start and dt_as_of > dt_planned_start and phys_pct == 0.0:
                sig_key = f"{project_id}|{act_id}|{TemporalSignalType.SILENT_CRITICAL_PATH_RISK}"
                sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"

                trace = [
                    f"✓ Critical Activity '{act_id}' ({fp.activity_name}) planned start was {fp.planned_start}.",
                    f"⚠ Evaluation date {as_of_date} is past planned start date.",
                    f"⚠ No trusted execution progress (0.0%) observed as of {as_of_date}.",
                    f"ℹ This signal indicates insufficient trusted evidence, NOT proven site work stoppage."
                ]

                sig = TemporalWarningSignal(
                    signal_id=sig_id,
                    signal_key=sig_key,
                    evaluation_run_id=evaluation_run_id,
                    project_id=project_id,
                    activity_id=act_id,
                    signal_type=TemporalSignalType.SILENT_CRITICAL_PATH_RISK,
                    severity=SignalSeverity.HIGH,
                    status=SignalStatus.ACTIVE,
                    as_of_date=as_of_date,
                    summary=f"Critical path activity '{act_id}' has 0% trusted progress past planned start ({fp.planned_start}).",
                    reasoning_trace=trace,
                    recommended_action="Request Daily Progress Report (DPR) update from field supervisor or verify site mobilization.",
                    involved_event_ids=[ev["event_id"] for ev in act_events],
                    first_detected_at=datetime.utcnow().isoformat() + "Z",
                    last_detected_at=datetime.utcnow().isoformat() + "Z"
                )
                signals.append(sig)

            # -------------------------------------------------------------
            # RULE 2: REPORTING_LATENCY_STALENESS
            # In-progress activity with no updated field reports for >= N days
            # -------------------------------------------------------------
            if phys_pct > 0.0 and phys_pct < 100.0 and act_events:
                # Find latest observed timestamp for activity
                latest_obs_dt = None
                for ev in act_events:
                    obs_str = ev.get("observed_timestamp") or ev.get("source_timestamp", "")
                    if obs_str:
                        try:
                            d = datetime.strptime(obs_str.split("T")[0], "%Y-%m-%d").date()
                            if latest_obs_dt is None or d > latest_obs_dt:
                                latest_obs_dt = d
                        except ValueError:
                            pass

                if latest_obs_dt:
                    days_since_report = (dt_as_of - latest_obs_dt).days
                    if days_since_report >= policy.reporting_staleness_days:
                        sig_key = f"{project_id}|{act_id}|{TemporalSignalType.REPORTING_LATENCY_STALENESS}"
                        sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"

                        trace = [
                            f"✓ Activity '{act_id}' is active in-progress ({phys_pct:.1f}% complete).",
                            f"⚠ Latest field observation was recorded on {latest_obs_dt} ({days_since_report} days ago).",
                            f"⚠ Reporting staleness exceeds policy threshold ({policy.reporting_staleness_days} days).",
                            f"ℹ Distinguishes reporting latency from site work stoppage."
                        ]

                        sig = TemporalWarningSignal(
                            signal_id=sig_id,
                            signal_key=sig_key,
                            evaluation_run_id=evaluation_run_id,
                            project_id=project_id,
                            activity_id=act_id,
                            signal_type=TemporalSignalType.REPORTING_LATENCY_STALENESS,
                            severity=SignalSeverity.MEDIUM,
                            status=SignalStatus.ACTIVE,
                            as_of_date=as_of_date,
                            summary=f"In-progress activity '{act_id}' has had zero field observations for {days_since_report} days.",
                            reasoning_trace=trace,
                            recommended_action=f"Prompt contractor to submit updated progress report for reporting window.",
                            involved_event_ids=[ev["event_id"] for ev in act_events],
                            first_detected_at=datetime.utcnow().isoformat() + "Z",
                            last_detected_at=datetime.utcnow().isoformat() + "Z"
                        )
                        signals.append(sig)

            # -------------------------------------------------------------
            # RULE 3: FORECAST_FINISH_SLIPPAGE (Null-Safe Guard)
            # Generated ONLY if forecast_status == ForecastStatus.AVAILABLE
            # -------------------------------------------------------------
            if forecast_status == ForecastStatus.AVAILABLE and forecast_finish and dt_planned_finish and finish_variance_days is not None:
                if finish_variance_days > 0:
                    dt_forecast = datetime.strptime(forecast_finish, "%Y-%m-%d").date()
                    if dt_forecast > dt_planned_finish:
                        # Deterministic Severity Policy Math
                        severity = SignalSeverity.LOW
                        if finish_variance_days >= policy.forecast_slippage_critical_days and is_critical:
                            severity = SignalSeverity.CRITICAL
                        elif finish_variance_days >= policy.forecast_slippage_high_days:
                            severity = SignalSeverity.HIGH
                        elif finish_variance_days >= policy.forecast_slippage_medium_days:
                            severity = SignalSeverity.MEDIUM

                        sig_key = f"{project_id}|{act_id}|{TemporalSignalType.FORECAST_FINISH_SLIPPAGE}"
                        sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"

                        trace = [
                            f"✓ Forecast derived from historical execution rate basis (status: AVAILABLE).",
                            f"✓ Baseline planned finish date: {fp.planned_finish}.",
                            f"⚠ Current calculated forecast finish: {forecast_finish} (+{finish_variance_days:.1f} days variance).",
                            f"⚠ Activity is critical: {is_critical}."
                        ]

                        sig = TemporalWarningSignal(
                            signal_id=sig_id,
                            signal_key=sig_key,
                            evaluation_run_id=evaluation_run_id,
                            project_id=project_id,
                            activity_id=act_id,
                            signal_type=TemporalSignalType.FORECAST_FINISH_SLIPPAGE,
                            severity=severity,
                            status=SignalStatus.ACTIVE,
                            as_of_date=as_of_date,
                            summary=f"Forecast finish date ({forecast_finish}) projects +{finish_variance_days:.0f}-day slippage past baseline finish ({fp.planned_finish}).",
                            reasoning_trace=trace,
                            recommended_action="Review contractor execution rate and issue schedule recovery mitigation plan.",
                            involved_event_ids=[ev["event_id"] for ev in act_events],
                            first_detected_at=datetime.utcnow().isoformat() + "Z",
                            last_detected_at=datetime.utcnow().isoformat() + "Z"
                        )
                        signals.append(sig)

            # -------------------------------------------------------------
            # RULE 4: UNVERIFIED_CLAIM_TEMPORAL_DRIFT
            # High volume of unverified claims past planned finish date
            # -------------------------------------------------------------
            if dt_planned_finish and dt_as_of > dt_planned_finish and phys_pct < 100.0 and unverified_count >= policy.unverified_claim_count_threshold:
                sig_key = f"{project_id}|{act_id}|{TemporalSignalType.UNVERIFIED_CLAIM_TEMPORAL_DRIFT}"
                sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"

                days_past_finish = (dt_as_of - dt_planned_finish).days
                trace = [
                    f"✓ Baseline planned finish date was {fp.planned_finish} ({days_past_finish} days ago).",
                    f"⚠ Activity has {unverified_count} unverified progress claims without trusted evidence.",
                    f"⚠ Physical progress remains incomplete ({phys_pct:.1f}%).",
                    f"ℹ High volume of reported claims unsupported by verified evidence."
                ]

                sig = TemporalWarningSignal(
                    signal_id=sig_id,
                    signal_key=sig_key,
                    evaluation_run_id=evaluation_run_id,
                    project_id=project_id,
                    activity_id=act_id,
                    signal_type=TemporalSignalType.UNVERIFIED_CLAIM_TEMPORAL_DRIFT,
                    severity=SignalSeverity.HIGH,
                    status=SignalStatus.ACTIVE,
                    as_of_date=as_of_date,
                    summary=f"Activity '{act_id}' has {unverified_count} unverified claims past planned finish ({fp.planned_finish}).",
                    reasoning_trace=trace,
                    recommended_action="Request contractor to submit supporting inspection evidence or NDT clearance records.",
                    involved_event_ids=[ev["event_id"] for ev in act_events],
                    first_detected_at=datetime.utcnow().isoformat() + "Z",
                    last_detected_at=datetime.utcnow().isoformat() + "Z"
                )
                signals.append(sig)

            # -------------------------------------------------------------
            # RULE 5: OUT_OF_SEQUENCE_EXECUTION_WARNING
            # Successor physical execution while Finish-to-Start predecessor incomplete
            # -------------------------------------------------------------
            if phys_pct > 0.0:
                pred_ids = predecessors_map.get(act_id, [])
                for pred_id in pred_ids:
                    pred_prog = act_prog_map.get(pred_id, {})
                    pred_phys = pred_prog.get("physical_progress_pct", 0.0)
                    if pred_phys < 100.0:
                        sig_key = f"{project_id}|{act_id}|{TemporalSignalType.OUT_OF_SEQUENCE_EXECUTION_WARNING}"
                        sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"

                        trace = [
                            f"✓ Activity '{act_id}' has recorded physical progress ({phys_pct:.1f}%).",
                            f"⚠ Baseline Finish-to-Start predecessor '{pred_id}' is incomplete ({pred_phys:.1f}%).",
                            f"⚠ Schedule relationship indicates successor should follow predecessor completion.",
                            f"ℹ Out-of-sequence execution flags a topological sequence anomaly, not a false report."
                        ]

                        sig = TemporalWarningSignal(
                            signal_id=sig_id,
                            signal_key=sig_key,
                            evaluation_run_id=evaluation_run_id,
                            project_id=project_id,
                            activity_id=act_id,
                            signal_type=TemporalSignalType.OUT_OF_SEQUENCE_EXECUTION_WARNING,
                            severity=SignalSeverity.MEDIUM,
                            status=SignalStatus.ACTIVE,
                            as_of_date=as_of_date,
                            summary=f"Successor '{act_id}' started ({phys_pct:.0f}%) while predecessor '{pred_id}' is incomplete ({pred_phys:.0f}%).",
                            reasoning_trace=trace,
                            recommended_action="Inspect field work order to confirm technical validity of out-of-sequence execution.",
                            involved_event_ids=[ev["event_id"] for ev in act_events],
                            first_detected_at=datetime.utcnow().isoformat() + "Z",
                            last_detected_at=datetime.utcnow().isoformat() + "Z"
                        )
                        signals.append(sig)
                        break  # One sequence signal per activity

            # -------------------------------------------------------------
            # RULE 6: QA_CLEARANCE_BOTTLENECK
            # Physical work 100% complete, QA status PENDING, downstream dependent activities exist
            # -------------------------------------------------------------
            if phys_pct == 100.0 and qa_status == QAClearanceStatus.PENDING and dt_planned_finish and dt_as_of > dt_planned_finish:
                succ_ids = successors_map.get(act_id, [])
                if succ_ids:  # Downstream dependent activities exist
                    sig_key = f"{project_id}|{act_id}|{TemporalSignalType.QA_CLEARANCE_BOTTLENECK}"
                    sig_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"

                    trace = [
                        f"✓ Physical execution is 100% complete for activity '{act_id}'.",
                        f"⚠ QA/NDT clearance status remains PENDING past planned finish ({fp.planned_finish}).",
                        f"⚠ Activity has {len(succ_ids)} downstream dependent successor activities ({', '.join(succ_ids[:3])}).",
                        f"ℹ QA bottleneck prevents formal schedule completion and successor release."
                    ]

                    sig = TemporalWarningSignal(
                        signal_id=sig_id,
                        signal_key=sig_key,
                        evaluation_run_id=evaluation_run_id,
                        project_id=project_id,
                        activity_id=act_id,
                        signal_type=TemporalSignalType.QA_CLEARANCE_BOTTLENECK,
                        severity=SignalSeverity.HIGH,
                        status=SignalStatus.ACTIVE,
                        as_of_date=as_of_date,
                        summary=f"Physical work 100% complete on '{act_id}', but QA clearance remains PENDING, blocking {len(succ_ids)} successors.",
                        reasoning_trace=trace,
                        recommended_action="Expedite QA/NDT inspection report submission and clear pending quality documentation.",
                        involved_event_ids=[ev["event_id"] for ev in act_events],
                        first_detected_at=datetime.utcnow().isoformat() + "Z",
                        last_detected_at=datetime.utcnow().isoformat() + "Z"
                    )
                    signals.append(sig)

        logger.info(f"[TimeAgentEngine] Generated {len(signals)} temporal warning signals for project {project_id} as of {as_of_date}")
        return signals
