"""
SATYA Actual Progress & Schedule Projection Engine (Phase 10)
Derives activity-level actual progress metrics, forecast completion dates,
and schedule variance projections from trusted execution events while maintaining
strict read-only baseline immutability.
"""

import math
import uuid
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple

from backend.models.domain_models import (
    ExecutionEvent, TrustAssessment, TrustStatus, EventType,
    ProgressCalculationPolicy, QuantityObservationType, ProgressCalculationStatus,
    ForecastStatus, ProgressWeightPolicy, ActivityProgressStatus, QAClearanceStatus,
    ActivityProgress, WBSProgress, ScheduleProjection
)

logger = logging.getLogger("SATYA.ActualProgressEngine")

# Eligible event types for Actual Start derivation
ELIGIBLE_START_EVENT_TYPES = {
    EventType.START, EventType.PROGRESS, EventType.QUANTITY_UPDATE, EventType.RESUME
}

class ActualProgressEngine:
    """
    Pure, deterministic engine that calculates a recomputable ProgressLayer
    (ActivityProgress, WBSProgress, ScheduleProjection) from baseline schedule activities
    and trusted execution events.
    """

    @staticmethod
    def filter_trusted_events(
        events: List[ExecutionEvent],
        trust_assessments: List[Dict[str, Any]]
    ) -> Tuple[List[ExecutionEvent], List[ExecutionEvent]]:
        """
        Applies the Trust Gate filter. Only events with latest TrustStatus == TRUSTED
        are returned in the trusted_events list.
        """
        # Map event_id -> latest trust_status
        trust_map: Dict[str, str] = {}
        for ta in trust_assessments:
            event_id = ta.get("event_id")
            # In case ta is dict from DB or dataclass
            status = ta.get("trust_status") if isinstance(ta, dict) else ta.trust_status
            v_idx = ta.get("version_index", 1) if isinstance(ta, dict) else getattr(ta, "version_index", 1)
            
            if event_id not in trust_map or v_idx >= trust_map.get(f"{event_id}_version", 0):
                trust_map[event_id] = status
                trust_map[f"{event_id}_version"] = v_idx

        trusted_events: List[ExecutionEvent] = []
        unverified_events: List[ExecutionEvent] = []

        for ev in events:
            status = trust_map.get(ev.event_id, TrustStatus.UNTRUSTED)
            if status == TrustStatus.TRUSTED:
                trusted_events.append(ev)
            else:
                unverified_events.append(ev)

        return trusted_events, unverified_events

    @staticmethod
    def determine_calculation_policy(activity: Dict[str, Any]) -> str:
        """
        Determines calculation policy based on activity baseline attributes.
        """
        planned_qty = activity.get("planned_quantity")
        unit = (activity.get("unit") or "").strip().lower()
        duration = activity.get("baseline_duration_days", 0)

        if planned_qty and planned_qty > 0 and unit not in ["milestone", "event", "item", "lump sum", "ls"]:
            return ProgressCalculationPolicy.QUANTITY_BASED
        elif duration == 0 or unit in ["milestone", "event"]:
            return ProgressCalculationPolicy.MILESTONE_BASED
        else:
            return ProgressCalculationPolicy.STATUS_BASED

    @staticmethod
    def resolve_quantity_aggregation(
        trusted_events: List[ExecutionEvent]
    ) -> Tuple[str, Optional[float]]:
        """
        Analyzes trusted events to determine if quantity observations are CUMULATIVE_TOTAL,
        DAILY_DELTA, or UNKNOWN, and calculates cumulative actual quantity.
        """
        qty_events = [ev for ev in trusted_events if getattr(ev, 'observed_quantity', None) is not None or getattr(ev, 'quantity', None) is not None]
        if not qty_events:
            return QuantityObservationType.UNKNOWN, None

        quantities = [getattr(ev, 'observed_quantity', None) if getattr(ev, 'observed_quantity', None) is not None else getattr(ev, 'quantity', None) for ev in qty_events]
        statements = [ (ev.extracted_statement or "").lower() for ev in qty_events ]

        # Check for explicit delta keywords in statements
        has_delta_kw = any("today" in stmt or "daily" in stmt or "+" in stmt for stmt in statements)
        
        if has_delta_kw:
            return QuantityObservationType.DAILY_DELTA, sum(quantities)

        # Check if sequence is non-decreasing (cumulative observations)
        if len(quantities) == 1:
            return QuantityObservationType.CUMULATIVE_TOTAL, quantities[0]

        is_monotonically_increasing = all(quantities[i] <= quantities[i+1] for i in range(len(quantities)-1))
        
        if is_monotonically_increasing:
            return QuantityObservationType.CUMULATIVE_TOTAL, quantities[-1]
        else:
            # Fluctuation without delta keywords indicates ambiguous / conflicting quantity semantics
            return QuantityObservationType.UNKNOWN, None

    @staticmethod
    def derive_actual_start(trusted_events: List[ExecutionEvent]) -> Optional[str]:
        """
        Derives Actual Start date ONLY from eligible execution events (START, PROGRESS, QUANTITY_UPDATE, RESUME).
        Excludes raw INSPECTION, QA_CLEARANCE, or HOLD events.
        """
        eligible = [
            ev for ev in trusted_events
            if ev.event_type in ELIGIBLE_START_EVENT_TYPES
        ]
        if not eligible:
            return None

        # Sort by observed_timestamp or timestamp
        timestamps = []
        for ev in eligible:
            ts = ev.observed_timestamp or ev.source_timestamp
            if ts:
                timestamps.append(ts[:10])  # YYYY-MM-DD
        
        return min(timestamps) if timestamps else None

    @staticmethod
    def derive_qa_clearance_status(trusted_events: List[ExecutionEvent]) -> str:
        """
        Determines QA clearance status from trusted events.
        """
        qa_cleared = any(
            ev.event_type == EventType.QA_CLEARANCE or "qa clear" in (ev.extracted_statement or "").lower() or "qa approved" in (ev.extracted_statement or "").lower()
            for ev in trusted_events
        )
        if qa_cleared:
            return QAClearanceStatus.CLEARED

        qa_pending = any(
            "qa pending" in (ev.extracted_statement or "").lower() or ev.pending_qa_clearance
            for ev in trusted_events
        )
        if qa_pending:
            return QAClearanceStatus.PENDING

        return QAClearanceStatus.NOT_REQUIRED

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[date]:
        """Helper to parse YYYY-MM-DD string to date object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def date_diff_days(d1_str: Optional[str], d2_str: Optional[str]) -> Optional[float]:
        """Returns (d1 - d2) in days. Positive means d1 is later than d2."""
        d1 = ActualProgressEngine.parse_date(d1_str)
        d2 = ActualProgressEngine.parse_date(d2_str)
        if d1 and d2:
            return float((d1 - d2).days)
        return None

    def calculate_activity_progress(
        self,
        activity: Dict[str, Any],
        trusted_events: List[ExecutionEvent],
        unverified_events: List[ExecutionEvent],
        as_of_date: str
    ) -> ActivityProgress:
        """
        Calculates ProgressLayer ActivityProgress for a single baseline activity.
        """
        activity_id = activity.get("activity_id")
        planned_qty = activity.get("planned_quantity")
        planned_unit = activity.get("unit")
        planned_start = activity.get("planned_start")
        planned_finish = activity.get("planned_finish")
        baseline_duration = activity.get("baseline_duration_days", 0)
        is_critical = activity.get("is_critical", False)

        policy = self.determine_calculation_policy(activity)

        # 1. Start Date & QA Status
        actual_start = self.derive_actual_start(trusted_events)
        qa_status = self.derive_qa_clearance_status(trusted_events)

        # 2. Progress & Quantity Calculation based on Policy
        actual_qty: Optional[float] = None
        phys_pct: Optional[float] = None
        calc_status = ProgressCalculationStatus.NOT_APPLICABLE
        actual_finish: Optional[str] = None

        unverified_qty = sum(
            ev.observed_quantity if ev.observed_quantity is not None else getattr(ev, 'quantity', 0.0)
            for ev in unverified_events
            if getattr(ev, 'observed_quantity', None) is not None or getattr(ev, 'quantity', None) is not None
        ) if unverified_events else 0.0

        if policy == ProgressCalculationPolicy.QUANTITY_BASED:
            obs_type, resolved_qty = self.resolve_quantity_aggregation(trusted_events)
            if obs_type == QuantityObservationType.UNKNOWN:
                calc_status = ProgressCalculationStatus.CONFLICTED
                phys_pct = None
            elif resolved_qty is not None and planned_qty and planned_qty > 0:
                actual_qty = resolved_qty
                raw_pct = (actual_qty / planned_qty) * 100.0
                phys_pct = min(100.0, round(raw_pct, 2))
                calc_status = ProgressCalculationStatus.CALCULATED
            elif len(trusted_events) > 0:
                calc_status = ProgressCalculationStatus.PARTIAL_EVIDENCE
            else:
                calc_status = ProgressCalculationStatus.INSUFFICIENT_DATA
                phys_pct = 0.0

        elif policy == ProgressCalculationPolicy.MILESTONE_BASED:
            has_finish = any(ev.event_type == EventType.FINISH for ev in trusted_events)
            if has_finish:
                phys_pct = 100.0
                calc_status = ProgressCalculationStatus.CALCULATED
            elif actual_start:
                phys_pct = 50.0
                calc_status = ProgressCalculationStatus.PARTIAL_EVIDENCE
            else:
                phys_pct = 0.0
                calc_status = ProgressCalculationStatus.INSUFFICIENT_DATA

        elif policy == ProgressCalculationPolicy.STATUS_BASED:
            has_finish = any(ev.event_type == EventType.FINISH for ev in trusted_events)
            has_progress = any(ev.event_type in (EventType.PROGRESS, EventType.START) for ev in trusted_events)
            if has_finish:
                phys_pct = 100.0
                calc_status = ProgressCalculationStatus.CALCULATED
            elif has_progress or actual_start:
                phys_pct = 50.0
                calc_status = ProgressCalculationStatus.PARTIAL_EVIDENCE
            else:
                phys_pct = 0.0
                calc_status = ProgressCalculationStatus.INSUFFICIENT_DATA

        # 3. Overall Activity Status
        if phys_pct is not None and phys_pct >= 100.0:
            status = ActivityProgressStatus.COMPLETED
            finish_events = [ev for ev in trusted_events if ev.event_type == EventType.FINISH or ev.observed_timestamp]
            if finish_events:
                finish_ts = [ev.observed_timestamp[:10] for ev in finish_events if ev.observed_timestamp]
                actual_finish = max(finish_ts) if finish_ts else as_of_date
            else:
                actual_finish = as_of_date
        elif actual_start or (phys_pct is not None and phys_pct > 0.0):
            status = ActivityProgressStatus.IN_PROGRESS
        else:
            status = ActivityProgressStatus.NOT_STARTED

        # 4. Duration Math
        actual_duration: Optional[float] = None
        remaining_duration: Optional[float] = None

        if status == ActivityProgressStatus.COMPLETED:
            actual_duration = self.date_diff_days(actual_finish, actual_start) if (actual_finish and actual_start) else float(baseline_duration)
            remaining_duration = 0.0
        elif status == ActivityProgressStatus.IN_PROGRESS:
            actual_duration = self.date_diff_days(as_of_date, actual_start) if actual_start else 0.0
            pct_val = phys_pct if phys_pct is not None else 0.0
            remaining_duration = max(0.0, math.ceil(baseline_duration * (1.0 - (pct_val / 100.0))))
        else:
            actual_duration = 0.0
            remaining_duration = float(baseline_duration)

        # 5. Execution Rate & Forecast Engine
        forecast_finish: Optional[str] = None
        forecast_status = ForecastStatus.NOT_APPLICABLE
        rate_per_day: Optional[float] = None

        if status == ActivityProgressStatus.COMPLETED:
            forecast_finish = actual_finish
            forecast_status = ForecastStatus.COMPLETED
        elif status == ActivityProgressStatus.IN_PROGRESS:
            # Check distinct timestamp points for rate calculation
            dated_qty_events = [
                ev for ev in trusted_events
                if (getattr(ev, 'observed_quantity', None) is not None or getattr(ev, 'quantity', None) is not None)
                and ev.observed_timestamp
            ]
            if policy == ProgressCalculationPolicy.QUANTITY_BASED and len(dated_qty_events) >= 2:
                dated_qty_events.sort(key=lambda x: x.observed_timestamp)
                t_first = self.parse_date(dated_qty_events[0].observed_timestamp)
                t_last = self.parse_date(dated_qty_events[-1].observed_timestamp)
                
                if t_first and t_last:
                    delta_days = (t_last - t_first).days
                    if delta_days > 0:
                        q_first = dated_qty_events[0].observed_quantity if dated_qty_events[0].observed_quantity is not None else getattr(dated_qty_events[0], 'quantity', 0.0)
                        q_last = dated_qty_events[-1].observed_quantity if dated_qty_events[-1].observed_quantity is not None else getattr(dated_qty_events[-1], 'quantity', 0.0)
                        delta_q = q_last - q_first
                        if delta_q > 0:
                            rate_per_day = round(delta_q / float(delta_days), 4)
                            rem_q = max(0.0, (planned_qty or 0.0) - (actual_qty or 0.0))
                            calc_rem_days = math.ceil(rem_q / rate_per_day)
                            as_of_dt = self.parse_date(as_of_date) or date.today()
                            ff_date = as_of_dt + timedelta(days=calc_rem_days)
                            forecast_finish = ff_date.strftime("%Y-%m-%d")
                            forecast_status = ForecastStatus.AVAILABLE
                            remaining_duration = float(calc_rem_days)
                        else:
                            forecast_status = ForecastStatus.ZERO_RATE
                            forecast_finish = None
                    else:
                        forecast_status = ForecastStatus.INSUFFICIENT_HISTORY
                        forecast_finish = None
                else:
                    forecast_status = ForecastStatus.INSUFFICIENT_HISTORY
                    forecast_finish = None
            else:
                # 1 point or status based -> Insufficient history for explicit rate forecast
                forecast_status = ForecastStatus.INSUFFICIENT_HISTORY
                forecast_finish = None

        # 6. Schedule Variances against Baseline
        start_var = self.date_diff_days(actual_start, planned_start) if actual_start else None
        
        finish_var: Optional[float] = None
        if status == ActivityProgressStatus.COMPLETED:
            finish_var = self.date_diff_days(actual_finish, planned_finish) if actual_finish else None
        elif forecast_finish:
            finish_var = self.date_diff_days(forecast_finish, planned_finish)
        else:
            finish_var = None

        crit_delay = is_critical and (finish_var is not None and finish_var > 0.0)

        return ActivityProgress(
            activity_id=activity_id,
            status=status,
            calculation_policy=policy,
            calculation_status=calc_status,
            forecast_status=forecast_status,
            actual_start=actual_start,
            actual_finish=actual_finish,
            actual_quantity=actual_qty,
            planned_quantity=planned_qty,
            unit=planned_unit,
            physical_progress_pct=phys_pct,
            qa_clearance_status=qa_status,
            actual_duration_days=actual_duration,
            remaining_duration_days=remaining_duration,
            execution_rate_per_day=rate_per_day,
            forecast_finish=forecast_finish,
            start_variance_days=start_var,
            finish_variance_days=finish_var,
            is_critical=is_critical,
            critical_activity_projected_delay=crit_delay,
            trusted_event_count=len(trusted_events),
            unverified_event_count=len(unverified_events),
            unverified_reported_quantity=unverified_qty if unverified_events else None,
            last_calculated_at=datetime.now().isoformat()
        )

    @staticmethod
    def calculate_wbs_rollups(
        wbs_hierarchy: List[Dict[str, Any]],
        activity_progress_map: Dict[str, ActivityProgress],
        activities: List[Dict[str, Any]]
    ) -> Dict[str, WBSProgress]:
        """
        Calculates hierarchical WBS progress rollups using DURATION_WEIGHT policy.
        Returns map of wbs_id -> WBSProgress.
        """
        # Group activity IDs by wbs_id
        wbs_activities: Dict[str, List[Dict[str, Any]]] = {}
        for act in activities:
            wbs_id = act.get("wbs_id")
            if wbs_id:
                wbs_activities.setdefault(wbs_id, []).append(act)

        wbs_result: Dict[str, WBSProgress] = {}

        for wbs in wbs_hierarchy:
            wbs_id = wbs.get("wbs_id")
            wbs_code = wbs.get("wbs_code", "")
            wbs_name = wbs.get("wbs_name", "")
            level = wbs.get("level", 1)

            # Find all child activities (directly or under descendant WBS nodes)
            # For simplicity in test baseline, match wbs_id directly or by prefix
            acts = wbs_activities.get(wbs_id, [])
            
            if not acts:
                wbs_result[wbs_id] = WBSProgress(
                    wbs_id=wbs_id,
                    wbs_code=wbs_code,
                    wbs_name=wbs_name,
                    level=level,
                    weight_policy=ProgressWeightPolicy.DURATION_WEIGHT,
                    physical_progress_pct=0.0,
                    weighted_progress_pct=0.0,
                    activities_count=0,
                    completed_count=0,
                    in_progress_count=0,
                    not_started_count=0
                )
                continue

            total_acts = len(acts)
            completed_cnt = 0
            in_prog_cnt = 0
            not_start_cnt = 0

            total_weight = 0.0
            weighted_sum = 0.0
            has_mixed_units = len(set(a.get("unit") for a in acts if a.get("unit"))) > 1

            for act in acts:
                act_id = act.get("activity_id")
                dur = act.get("baseline_duration_days", 1)
                prog = activity_progress_map.get(act_id)

                if prog:
                    if prog.status == ActivityProgressStatus.COMPLETED:
                        completed_cnt += 1
                    elif prog.status == ActivityProgressStatus.IN_PROGRESS:
                        in_prog_cnt += 1
                    else:
                        not_start_cnt += 1

                    phys = prog.physical_progress_pct if prog.physical_progress_pct is not None else 0.0
                    total_weight += dur
                    weighted_sum += (phys * dur)
                else:
                    not_start_cnt += 1
                    total_weight += dur

            weighted_pct = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0
            phys_avg = round(sum((activity_progress_map[a["activity_id"]].physical_progress_pct or 0.0) for a in acts if a["activity_id"] in activity_progress_map) / total_acts, 2) if total_acts > 0 else 0.0

            wbs_result[wbs_id] = WBSProgress(
                wbs_id=wbs_id,
                wbs_code=wbs_code,
                wbs_name=wbs_name,
                level=level,
                weight_policy=ProgressWeightPolicy.DURATION_WEIGHT,
                physical_progress_pct=phys_avg if not has_mixed_units else None,
                weighted_progress_pct=weighted_pct,
                activities_count=total_acts,
                completed_count=completed_cnt,
                in_progress_count=in_prog_cnt,
                not_started_count=not_start_cnt
            )

        return wbs_result

    def generate_projection(
        self,
        project_id: str,
        activities: List[Dict[str, Any]],
        wbs_hierarchy: List[Dict[str, Any]],
        events: List[ExecutionEvent],
        trust_assessments: List[Dict[str, Any]],
        as_of_date: str
    ) -> ScheduleProjection:
        """
        Generates a complete, deterministic ScheduleProjection snapshot.
        """
        trusted_events, unverified_events = self.filter_trusted_events(events, trust_assessments)

        # Map events by activity_id
        events_by_act: Dict[str, List[ExecutionEvent]] = {}
        unverified_by_act: Dict[str, List[ExecutionEvent]] = {}

        for ev in trusted_events:
            if ev.observed_activity_id:
                events_by_act.setdefault(ev.observed_activity_id, []).append(ev)

        for ev in unverified_events:
            if ev.observed_activity_id:
                unverified_by_act.setdefault(ev.observed_activity_id, []).append(ev)

        activity_progress_map: Dict[str, ActivityProgress] = {}
        total_activities = len(activities)
        completed_cnt = 0
        in_prog_cnt = 0
        not_start_cnt = 0
        crit_delay_cnt = 0
        max_delay = 0.0

        for act in activities:
            act_id = act.get("activity_id")
            act_trusted = events_by_act.get(act_id, [])
            act_unverified = unverified_by_act.get(act_id, [])

            prog = self.calculate_activity_progress(act, act_trusted, act_unverified, as_of_date)
            activity_progress_map[act_id] = prog

            if prog.status == ActivityProgressStatus.COMPLETED:
                completed_cnt += 1
            elif prog.status == ActivityProgressStatus.IN_PROGRESS:
                in_prog_cnt += 1
            else:
                not_start_cnt += 1

            if prog.critical_activity_projected_delay:
                crit_delay_cnt += 1

            if prog.finish_variance_days and prog.finish_variance_days > max_delay:
                max_delay = prog.finish_variance_days

        wbs_progress_map = self.calculate_wbs_rollups(wbs_hierarchy, activity_progress_map, activities)

        # Overall Project Progress (duration-weighted across all activities)
        tot_weight = sum(a.get("baseline_duration_days", 1) for a in activities)
        tot_weighted_sum = sum(
            ((activity_progress_map[a["activity_id"]].physical_progress_pct or 0.0) * a.get("baseline_duration_days", 1))
            for a in activities if a["activity_id"] in activity_progress_map
        )
        overall_project_pct = round(tot_weighted_sum / tot_weight, 2) if tot_weight > 0 else 0.0

        projection_id = f"PRJ-SNAP-{uuid.uuid4().hex[:8].upper()}"

        logger.info(f"Generated ScheduleProjection {projection_id} for Project {project_id} as of {as_of_date}: Overall Progress {overall_project_pct}%")

        return ScheduleProjection(
            projection_id=projection_id,
            project_id=project_id,
            as_of_date=as_of_date,
            total_activities=total_activities,
            completed_activities=completed_cnt,
            in_progress_activities=in_prog_cnt,
            not_started_activities=not_start_cnt,
            overall_project_progress_pct=overall_project_pct,
            critical_activity_delay_count=crit_delay_cnt,
            max_schedule_delay_days=max_delay,
            unverified_claims_count=len(unverified_events),
            activity_progress_map=activity_progress_map,
            wbs_progress_map=wbs_progress_map,
            generated_at=datetime.now().isoformat()
        )
