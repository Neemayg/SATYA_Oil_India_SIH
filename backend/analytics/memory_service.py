"""
SATYA Institutional Memory Service (Phase 14)
Distills human planner corrections (CHANGE_MATCH decisions) into versioned,
project-scoped terminology aliases. Applies strict promotion lifecycle
(CANDIDATE -> VALIDATED -> ACTIVE -> SUPERSEDED) and deterministic confidence math.
"""

import uuid
from datetime import datetime, timezone
import math
from typing import List, Dict, Any, Optional
from backend.models.domain_models import (
    InstitutionalMemoryPolicy, MemoryDistillationRun,
    TerminologyAliasRecord, AliasStatus, ValidationDecisionType
)
from backend.persistence.database_engine import DatabaseEngine

class InstitutionalMemoryService:
    def __init__(self, db: DatabaseEngine, policy: Optional[InstitutionalMemoryPolicy] = None):
        self.db = db
        self.policy = policy or InstitutionalMemoryPolicy()

    def calculate_alias_confidence(
        self,
        distinct_planner_count: int,
        distinct_source_count: int,
        reoverride_count: int,
        last_validated_iso: str,
        as_of_iso: str
    ) -> float:
        """
        Calculates deterministic alias confidence score:
        C_alias = clamp(
            w_plan * N_planners + w_src * N_sources + Recency(dt) - w_over * N_reoverrides,
            0.0, 1.0
        )
        """
        # Recency term calculation (exponential decay based on days elapsed)
        recency_term = 0.5  # Base recency
        if last_validated_iso and as_of_iso:
            try:
                t_val = datetime.fromisoformat(last_validated_iso.replace("Z", "+00:00"))
                t_asof = datetime.fromisoformat(as_of_iso.replace("Z", "+00:00"))
                days_elapsed = max(0.0, (t_asof - t_val).total_seconds() / 86400.0)
                half_life = max(1.0, self.policy.recency_half_life_days)
                recency_term = math.exp(-0.693 * (days_elapsed / half_life))
            except Exception:
                recency_term = 0.5

        raw_score = (
            (self.policy.w_plan * distinct_planner_count) +
            (self.policy.w_src * distinct_source_count) +
            (0.2 * recency_term) -
            (self.policy.w_over * reoverride_count)
        )
        return max(0.0, min(1.0, round(raw_score, 4)))

    def distill_planner_corrections(
        self,
        project_id: str,
        as_of_date: Optional[str] = None
    ) -> MemoryDistillationRun:
        """
        Scans planner corrections and validation decisions for project_id,
        extracts phrase aliases, applies promotion gates, and saves distillation audit run.
        """
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        as_of_iso = as_of_date or now_iso

        # 1. Fetch planner corrections for project
        corrections = self.db.get_planner_corrections()
        # Filter corrections for this project by fetching associated execution events
        project_corrections = []
        for corr in corrections:
            event = self.db.get_execution_event(corr.get("event_id", ""))
            if event:
                source = self.db.get_source_document(event.get("source_id", ""))
                ev_proj = event.get("project_id") or (source.project_id if source else None)
                if not ev_proj or ev_proj == project_id:
                    project_corrections.append((corr, event))

        # 2. Fetch existing aliases for project
        existing_alias_rows = self.db.get_terminology_aliases_by_project(project_id)
        existing_aliases: Dict[str, Dict[str, Any]] = {
            f"{r['alias_phrase'].lower()}|{r['target_activity_id']}": r for r in existing_alias_rows
        }

        # 3. Group corrections by phrase + target activity ID
        grouped_phrases: Dict[str, List[Tuple[Dict[str, Any], Dict[str, Any]]]] = {}
        for corr, event in project_corrections:
            phrase = (event.get("raw_snippet") or event.get("extracted_statement") or "").strip()
            if not phrase:
                continue
            target_act = corr.get("corrected_activity_id")
            if not target_act:
                continue
            key = f"{phrase.lower()}|{target_act}"
            if key not in grouped_phrases:
                grouped_phrases[key] = []
            grouped_phrases[key].append((corr, event))

        candidates_created = 0
        promoted_aliases = 0
        superseded_aliases = 0

        # 4. Process groups and update / create alias records
        for key, items in grouped_phrases.items():
            first_corr, first_evt = items[0]
            phrase = (first_evt.get("raw_snippet") or first_evt.get("extracted_statement") or "").strip()
            target_act = first_corr.get("corrected_activity_id")

            planner_set = {c.get("planner_id") for c, _ in items if c.get("planner_id")}
            source_set = {e.get("source_id") for _, e in items if e.get("source_id")}
            confirmation_count = len(items)
            distinct_planners = len(planner_set)
            distinct_sources = len(source_set)
            last_val = items[-1][0].get("created_at") or now_iso

            confidence = self.calculate_alias_confidence(
                distinct_planner_count=distinct_planners,
                distinct_source_count=distinct_sources,
                reoverride_count=0,
                last_validated_iso=last_val,
                as_of_iso=as_of_iso
            )

            # Determine promotion status
            if distinct_planners >= 2 and confirmation_count >= 3:
                status = AliasStatus.ACTIVE
            elif confirmation_count >= self.policy.min_candidate_confirmations or distinct_planners >= 2:
                status = AliasStatus.VALIDATED
            else:
                status = AliasStatus.CANDIDATE

            if key in existing_aliases:
                ext = existing_aliases[key]
                prev_status = ext.get("status")
                if prev_status != status and status in (AliasStatus.VALIDATED, AliasStatus.ACTIVE):
                    promoted_aliases += 1

                updated_alias = TerminologyAliasRecord(
                    alias_id=ext["alias_id"],
                    project_id=project_id,
                    version=ext["version"] + 1,
                    alias_phrase=phrase,
                    target_activity_id=target_act,
                    status=status,
                    confidence_weight=confidence,
                    confirmation_count=confirmation_count,
                    distinct_planner_count=distinct_planners,
                    distinct_source_count=distinct_sources,
                    reoverride_count=ext.get("reoverride_count", 0),
                    supersedes_alias_id=ext.get("supersedes_alias_id"),
                    last_validated_at=last_val,
                    created_at=ext.get("created_at", now_iso)
                )
                self.db.save_terminology_alias(updated_alias)
            else:
                if status == AliasStatus.CANDIDATE:
                    candidates_created += 1
                elif status in (AliasStatus.VALIDATED, AliasStatus.ACTIVE):
                    promoted_aliases += 1

                new_alias = TerminologyAliasRecord(
                    alias_id=f"ALIAS-{uuid.uuid4().hex[:8].upper()}",
                    project_id=project_id,
                    version=1,
                    alias_phrase=phrase,
                    target_activity_id=target_act,
                    status=status,
                    confidence_weight=confidence,
                    confirmation_count=confirmation_count,
                    distinct_planner_count=distinct_planners,
                    distinct_source_count=distinct_sources,
                    reoverride_count=0,
                    supersedes_alias_id=None,
                    last_validated_at=last_val,
                    created_at=now_iso
                )
                self.db.save_terminology_alias(new_alias)

        # 5. Create distillation run audit record
        run_id = f"DISTILL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        run = MemoryDistillationRun(
            distillation_run_id=run_id,
            project_id=project_id,
            as_of_date=as_of_iso,
            policy_version=self.policy.policy_version,
            input_corrections_count=len(project_corrections),
            candidates_created_count=candidates_created,
            promoted_aliases_count=promoted_aliases,
            superseded_aliases_count=superseded_aliases,
            executed_at=now_iso
        )
        self.db.save_memory_distillation_run(run)
        return run

    def get_candidate_alias_scores(self, project_id: str, raw_text: str) -> Dict[str, float]:
        """
        Queries active & validated aliases for project_id and matches raw_text.
        Returns map of {activity_id: alias_confidence_score}.
        """
        if not raw_text:
            return {}
        text_lower = raw_text.lower()
        active_aliases = self.db.get_terminology_aliases_by_project(project_id)
        scores: Dict[str, float] = {}

        for alias in active_aliases:
            if alias["status"] not in (AliasStatus.ACTIVE, AliasStatus.VALIDATED):
                continue
            phrase = alias["alias_phrase"].lower()
            if phrase in text_lower or text_lower in phrase:
                act_id = alias["target_activity_id"]
                weight = float(alias["confidence_weight"])
                # Keep highest score if multiple aliases hit same activity
                if act_id not in scores or weight > scores[act_id]:
                    scores[act_id] = weight

        return scores
