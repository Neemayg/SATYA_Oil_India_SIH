"""
SATYA Time Agent Service (Phase 13)
Orchestrates monitoring evaluation runs, signal deduplication, lifecycle resolution, and SQLite persistence.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.persistence.database_engine import DatabaseEngine
from backend.monitoring.time_agent_engine import TimeAgentEngine
from backend.models.domain_models import (
    TemporalMonitoringPolicy,
    MonitoringEvaluationRun,
    TemporalWarningSignal,
    SignalStatus,
    ScheduleProjection,
    ActivityFingerprint
)

logger = logging.getLogger("SATYA.TimeAgentService")

class TimeAgentService:

    def __init__(self, db_engine: DatabaseEngine):
        self.db = db_engine
        self.engine = TimeAgentEngine()

    def run_monitoring_evaluation(
        self,
        project_id: str,
        as_of_date: Optional[str] = None,
        policy: Optional[TemporalMonitoringPolicy] = None
    ) -> Dict[str, Any]:
        """
        Executes a temporal monitoring evaluation run for a project.
        Manages signal lifecycle, updates active signals via signal_key deduplication,
        resolves obsolete signals, and persists run metrics to SQLite.
        """
        if not as_of_date:
            as_of_date = datetime.now().strftime("%Y-%m-%d")

        if not policy:
            policy = TemporalMonitoringPolicy()

        run_id = f"RUN-MON-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        # 1. Fetch latest ScheduleProjection
        proj_dict = self.db.get_latest_schedule_projection(project_id)
        if not proj_dict:
            logger.warning(f"No schedule projection found for project {project_id}. Generating projection...")
            # Fallback mock/empty projection structure if not available
            projection = ScheduleProjection(
                projection_id=f"PRJ-SNAP-EMPTY",
                project_id=project_id,
                as_of_date=as_of_date
            )
        else:
            # Reconstruct ScheduleProjection object
            projection = ScheduleProjection(
                projection_id=proj_dict["projection_id"],
                project_id=proj_dict["project_id"],
                as_of_date=proj_dict["as_of_date"],
                total_activities=proj_dict["total_activities"],
                completed_activities=proj_dict["completed_activities"],
                in_progress_activities=proj_dict["in_progress_activities"],
                not_started_activities=proj_dict["not_started_activities"],
                overall_project_progress_pct=proj_dict.get("overall_project_progress_pct"),
                critical_activity_delay_count=proj_dict.get("critical_activity_delay_count", 0),
                max_schedule_delay_days=proj_dict.get("max_schedule_delay_days", 0.0),
                unverified_claims_count=proj_dict.get("unverified_claims_count", 0),
                activity_progress_map=proj_dict.get("activity_progress_map", {}),
                wbs_progress_map=proj_dict.get("wbs_progress_map", {}),
                generated_at=proj_dict.get("generated_at", "")
            )

        # 2. Fetch Activity Fingerprints for project
        fp_dicts = self.db.get_fingerprints_by_project(project_id)
        fingerprints = []
        for d in fp_dicts:
            fp = ActivityFingerprint(
                fingerprint_id=d["fingerprint_id"],
                activity_id=d["activity_id"],
                project_id=d["project_id"],
                activity_name=d["activity_name"],
                normalized_name=d["normalized_name"],
                wbs_id=d["wbs_id"],
                wbs_code=d["wbs_code"],
                wbs_name_path=d["wbs_name_path"],
                discipline=d["discipline"],
                area_location=d.get("area_location"),
                equipment_tag=d.get("equipment_tag"),
                line_number=d.get("line_number"),
                start_km=d.get("start_km"),
                end_km=d.get("end_km"),
                planned_start=d.get("planned_start"),
                planned_finish=d.get("planned_finish"),
                baseline_duration_days=d.get("baseline_duration_days", 0),
                planned_quantity=d.get("planned_quantity"),
                unit_of_measure=d.get("unit_of_measure"),
                is_critical=bool(d.get("is_critical", 0)),
                predecessors=d.get("predecessors", []),
                successors=d.get("successors", [])
            )
            fingerprints.append(fp)

        # 3. Fetch all events and trust assessments for project
        source_ids = []
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT source_id FROM source_documents WHERE project_id = ?", (project_id,))
            source_ids = [r["source_id"] for r in cursor.fetchall()]

        all_events = []
        for sid in source_ids:
            all_events.extend(self.db.get_events_by_source(sid))

        all_trust = []
        for ev in all_events:
            tas = self.db.get_trust_assessments_by_event(ev["event_id"])
            if tas:
                all_trust.append(tas[-1])

        # 4. Execute Time Agent Engine evaluation
        detected_signals = self.engine.evaluate_project_timeline(
            project_id=project_id,
            projection=projection,
            fingerprints=fingerprints,
            events=all_events,
            trust_assessments=all_trust,
            policy=policy,
            as_of_date=as_of_date,
            evaluation_run_id=run_id
        )

        # 5. Signal Lifecycle Management & Deduplication via signal_key
        existing_active_signals = self.db.get_active_signals_by_project(project_id)
        existing_key_map = {sig["signal_key"]: sig for sig in existing_active_signals}

        now_iso = datetime.utcnow().isoformat() + "Z"
        new_active_keys = set()

        for sig in detected_signals:
            new_active_keys.add(sig.signal_key)
            if sig.signal_key in existing_key_map:
                # Update existing active signal (preserve original first_detected_at)
                existing = existing_key_map[sig.signal_key]
                sig.signal_id = existing["signal_id"]
                sig.first_detected_at = existing["first_detected_at"]
                sig.last_detected_at = now_iso
            else:
                sig.first_detected_at = now_iso
                sig.last_detected_at = now_iso

            self.db.save_temporal_warning_signal(sig)

        # Resolve obsolete signals no longer detected in current run
        for key, sig_dict in existing_key_map.items():
            if key not in new_active_keys:
                sig_dict["status"] = SignalStatus.RESOLVED
                sig_dict["last_detected_at"] = now_iso
                # Reconstruct object to save
                res_sig = TemporalWarningSignal(
                    signal_id=sig_dict["signal_id"],
                    signal_key=sig_dict["signal_key"],
                    evaluation_run_id=run_id,
                    project_id=sig_dict["project_id"],
                    activity_id=sig_dict["activity_id"],
                    signal_type=sig_dict["signal_type"],
                    severity=sig_dict["severity"],
                    status=SignalStatus.RESOLVED,
                    as_of_date=as_of_date,
                    summary=sig_dict["summary"],
                    reasoning_trace=sig_dict["reasoning_trace"],
                    recommended_action=sig_dict["recommended_action"],
                    involved_event_ids=sig_dict["involved_event_ids"],
                    involved_evidence_ids=sig_dict["involved_evidence_ids"],
                    first_detected_at=sig_dict["first_detected_at"],
                    last_detected_at=now_iso
                )
                self.db.save_temporal_warning_signal(res_sig)

        # 6. Save Monitoring Evaluation Run metrics
        eval_run = MonitoringEvaluationRun(
            evaluation_run_id=run_id,
            project_id=project_id,
            as_of_date=as_of_date,
            policy_version=policy.policy_version,
            evaluated_at=now_iso,
            total_signals_detected=len(detected_signals),
            active_signal_count=len(new_active_keys)
        )
        self.db.save_monitoring_evaluation_run(eval_run)

        logger.info(f"[TimeAgentService] Completed evaluation run {run_id} for project {project_id}: {len(detected_signals)} active signals.")

        return {
            "evaluation_run": eval_run.to_dict(),
            "signals": [sig.to_dict() for sig in detected_signals]
        }
