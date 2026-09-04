"""
SATYA Execution Analytics Engine (Phase 14)
Computes empirical execution rate benchmarks, contractor reporting profiles,
and conflict & warning resolution patterns cleanly separated from baseline schedule state.
"""

import uuid
from datetime import datetime, timezone
import numpy as np
from typing import List, Dict, Any, Optional
from backend.models.domain_models import (
    InstitutionalMemoryPolicy, ExecutionRateBenchmark, BenchmarkStatus,
    ContractorReportingProfile, ConflictResolutionPattern, TrustStatus
)
from backend.persistence.database_engine import DatabaseEngine

class ExecutionAnalyticsEngine:
    def __init__(self, db: DatabaseEngine, policy: Optional[InstitutionalMemoryPolicy] = None):
        self.db = db
        self.policy = policy or InstitutionalMemoryPolicy()

    def compute_execution_rate_benchmarks(
        self,
        project_id: str,
        as_of_date: Optional[str] = None
    ) -> List[ExecutionRateBenchmark]:
        """
        Calculates empirical actual physical work rates (Rate = delta_Q / delta_t)
        grouped strictly by (project_id, wbs_id, activity_type, unit_of_measure, quantity_basis).
        Assigns BenchmarkStatus based on sample_count thresholds.
        """
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Fetch latest schedule projection for actual activity rates
        projection_dict = self.db.get_latest_schedule_projection(project_id)
        if not projection_dict or "activity_progress_map" not in projection_dict:
            return []

        act_progress_map = projection_dict["activity_progress_map"]

        # Fetch trusted execution events for observed rates
        events = self.db.get_execution_events_by_project(project_id)
        # If project events is empty, fallback to all events
        if not events:
            events = self.db.get_all_execution_events()

        trusted_events = [
            e for e in events
            if e.get("trust_status") in (TrustStatus.TRUSTED, "TRUSTED") or e.get("resulting_trust_status") in (TrustStatus.TRUSTED, "TRUSTED") or e.get("lifecycle_state") in ("TRUSTED", "EXTRACTED")
        ]

        # Group observations by (wbs_id, activity_type, discipline, unit_of_measure, quantity_basis)
        grouped_rates: Dict[str, Dict[str, Any]] = {}

        for act_id, act_data in act_progress_map.items():
            uom = act_data.get("unit") or act_data.get("unit_of_measure", "").strip()
            qty_basis = act_data.get("quantity_observation_type") or act_data.get("calculation_policy", "").strip()
            planned_qty = float(act_data.get("planned_quantity", 0.0) or 0.0)
            actual_qty = float(act_data.get("actual_quantity", 0.0) or 0.0)
            wbs_id = act_data.get("wbs_id", "WBS-UNSPECIFIED")
            act_type = act_data.get("activity_type", "GENERAL")
            discipline = act_data.get("discipline", "GENERAL")
            planned_dur = float(act_data.get("planned_duration_days", 0.0) or act_data.get("actual_duration_days", 0.0) or 0.0)

            # Skip unquantified or unknown quantity basis
            if not uom or qty_basis in ("UNKNOWN", "", "NONE") or planned_qty <= 0:
                continue

            group_key = f"{wbs_id}|{act_type}|{discipline}|{uom}|{qty_basis}"

            # Calculate planned rate (None if duration or quantity missing)
            planned_rate = (planned_qty / planned_dur) if planned_dur > 0 else None

            # Collect actual rates from trusted events for this activity
            act_events = [e for e in trusted_events if e.get("matched_activity_id") == act_id or e.get("observed_activity_id") == act_id or e.get("explicit_activity_id") == act_id]
            rates = []
            for evt in act_events:
                q_val = float(evt.get("observed_quantity") or evt.get("quantity", 0.0) or 0.0)
                dur_days = float(evt.get("work_duration_days", 1.0) or 1.0)
                if q_val > 0 and dur_days > 0:
                    rates.append(q_val / dur_days)

            # Fallback to total actual_qty over estimated duration if no direct event rates
            if not rates and actual_qty > 0 and planned_dur > 0:
                rates.append(actual_qty / planned_dur)

            if group_key not in grouped_rates:
                grouped_rates[group_key] = {
                    "wbs_id": wbs_id,
                    "activity_type": act_type,
                    "discipline": discipline,
                    "unit_of_measure": uom,
                    "quantity_basis": qty_basis,
                    "planned_rates": [],
                    "rates": []
                }
            if planned_rate is not None:
                grouped_rates[group_key]["planned_rates"].append(planned_rate)
            grouped_rates[group_key]["rates"].extend(rates)

        benchmarks: List[ExecutionRateBenchmark] = []

        for key, data in grouped_rates.items():
            rates = data["rates"]
            sample_count = len(rates)

            # Determine BenchmarkStatus
            if sample_count < self.policy.min_provisional_sample:
                status = BenchmarkStatus.INSUFFICIENT_SAMPLE
            elif sample_count < self.policy.min_validated_sample:
                status = BenchmarkStatus.PROVISIONAL
            else:
                status = BenchmarkStatus.VALIDATED

            mean_rate = float(np.mean(rates)) if rates else 0.0
            p50 = float(np.median(rates)) if rates else 0.0
            p90 = float(np.percentile(rates, 90)) if rates else 0.0

            planned_rates = data["planned_rates"]
            avg_planned = float(np.mean(planned_rates)) if planned_rates else None

            bench = ExecutionRateBenchmark(
                benchmark_id=f"BENCH-{uuid.uuid4().hex[:8].upper()}",
                project_id=project_id,
                wbs_id=data["wbs_id"],
                activity_type=data["activity_type"],
                discipline=data["discipline"],
                unit_of_measure=data["unit_of_measure"],
                quantity_basis=data["quantity_basis"],
                planned_rate=round(avg_planned, 4) if avg_planned is not None else None,
                mean_actual_rate=round(mean_rate, 4),
                p50_rate=round(p50, 4),
                p90_rate=round(p90, 4),
                sample_count=sample_count,
                benchmark_status=status,
                last_calculated_at=now_iso
            )
            self.db.save_execution_rate_benchmark(bench)
            benchmarks.append(bench)

        return benchmarks

    def compute_contractor_reporting_profiles(
        self,
        project_id: str
    ) -> List[ContractorReportingProfile]:
        """
        Computes historical reporting frequency, verification ratio, and reporting latency per contractor.
        Explicitly Framed: Describes historical reporting completeness, NOT contractual performance score.
        """
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        events = self.db.get_execution_events_by_project(project_id)
        if not events:
            events = self.db.get_all_execution_events()

        grouped_contractors: Dict[str, List[Dict[str, Any]]] = {}

        for evt in events:
            # Check source metadata, status_text, or author for contractor ID
            contractor_id = evt.get("contractor_id") or evt.get("status_text") or evt.get("author") or "UNKNOWN"
            if contractor_id not in grouped_contractors:
                grouped_contractors[contractor_id] = []
            grouped_contractors[contractor_id].append(evt)

        profiles: List[ContractorReportingProfile] = []

        for contractor_id, contractor_events in grouped_contractors.items():
            total = len(contractor_events)
            trusted = 0
            untrusted = 0
            delays_days = []

            for evt in contractor_events:
                status = evt.get("trust_status") or evt.get("resulting_trust_status") or "UNTRUSTED"
                if status in (TrustStatus.TRUSTED, "TRUSTED") or evt.get("lifecycle_state") in ("TRUSTED", "EXTRACTED"):
                    trusted += 1
                else:
                    untrusted += 1

                # Calculate reporting latency: reported_at - observed_at
                reported_at = evt.get("source_timestamp") or evt.get("ingested_at") or evt.get("source_submitted_at")
                observed_at = evt.get("observed_timestamp")
                if reported_at and observed_at:
                    try:
                        t_rep = datetime.fromisoformat(reported_at.replace("Z", "+00:00"))
                        t_obs = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
                        diff_days = (t_rep - t_obs).total_seconds() / 86400.0
                        if diff_days >= 0:
                            delays_days.append(diff_days)
                    except Exception:
                        pass

            verification_ratio = round(trusted / total, 4) if total > 0 else 0.0
            avg_delay = round(float(np.mean(delays_days)), 2) if delays_days else None

            prof = ContractorReportingProfile(
                profile_id=f"PROF-{uuid.uuid4().hex[:8].upper()}",
                project_id=project_id,
                contractor_id=contractor_id if contractor_id != "UNKNOWN" else None,
                total_events=total,
                trusted_events=trusted,
                untrusted_events=untrusted,
                verification_ratio=verification_ratio,
                avg_reporting_delay_days=avg_delay,
                last_updated_at=now_iso
            )
            self.db.save_contractor_reporting_profile(prof)
            profiles.append(prof)

        return profiles

    def compute_conflict_resolution_patterns(
        self,
        project_id: str
    ) -> List[ConflictResolutionPattern]:
        """
        Analyzes historical resolution pathways for machine conflict flags and Time Agent warnings,
        cleanly separating Time Agent ACKNOWLEDGED from physical RESOLVED conditions.
        """
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # 1. Fetch HITL validation decisions for conflict resolutions
        decisions = self.db.get_validation_decisions_by_project(project_id)
        # 2. Fetch Time Agent warning signals
        signals = self.db.get_active_signals_by_project(project_id)

        grouped_patterns: Dict[str, Dict[str, Any]] = {}

        for dec in decisions:
            ctype = dec.get("override_reason_category") or "GENERAL_HITL_REVIEW"
            if ctype not in grouped_patterns:
                grouped_patterns[ctype] = {
                    "total": 0, "validated": 0, "remapped": 0, "rejected": 0,
                    "acknowledged": 0, "resolved": 0, "durations": []
                }
            g = grouped_patterns[ctype]
            g["total"] += 1
            dtype = dec.get("decision_type")
            if dtype == "VALIDATE":
                g["validated"] += 1
            elif dtype == "CHANGE_MATCH":
                g["remapped"] += 1
            elif dtype == "REJECT":
                g["rejected"] += 1

        # Process Time Agent signals
        for sig in signals:
            stype = sig.get("signal_type", "GENERAL_SIGNAL")
            if stype not in grouped_patterns:
                grouped_patterns[stype] = {
                    "total": 0, "validated": 0, "remapped": 0, "rejected": 0,
                    "acknowledged": 0, "resolved": 0, "durations": []
                }
            g = grouped_patterns[stype]
            g["total"] += 1
            sstatus = sig.get("status")
            if sstatus == "ACKNOWLEDGED":
                g["acknowledged"] += 1
            elif sstatus == "RESOLVED":
                g["resolved"] += 1

        patterns: List[ConflictResolutionPattern] = []

        for ctype, g in grouped_patterns.items():
            durations = g["durations"]
            avg_hours = round(float(np.mean(durations)), 2) if durations else 0.0

            pat = ConflictResolutionPattern(
                pattern_id=f"PAT-{uuid.uuid4().hex[:8].upper()}",
                project_id=project_id,
                conflict_or_signal_type=ctype,
                total_occurrences=g["total"],
                validated_count=g["validated"],
                remapped_count=g["remapped"],
                rejected_count=g["rejected"],
                acknowledged_count=g["acknowledged"],
                resolved_count=g["resolved"],
                avg_resolution_hours=avg_hours,
                last_updated_at=now_iso
            )
            self.db.save_conflict_resolution_pattern(pat)
            patterns.append(pat)

        return patterns
