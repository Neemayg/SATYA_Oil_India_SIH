"""
SATYA Schedule-Aware Activity Matching Engine
Aligns extracted ExecutionEvents to baseline ActivityFingerprints using multi-factor
structural, spatial, temporal, discipline, and terminology compatibility scoring.
"""

import uuid
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from backend.models.domain_models import (
    ExecutionEvent, ActivityFingerprint, MatchResult, CandidateMatch,
    MatchFactorScores, MatchOutcome, PipelineState
)

class ScheduleAwareMatchingEngine:
    """Schedule-aware activity matching engine with explicit reasoning traces."""

    def __init__(
        self,
        theta_match: float = 0.80,
        theta_unmatched: float = 0.45,
        ambiguity_margin: float = 0.08
    ):
        self.theta_match = theta_match
        self.theta_unmatched = theta_unmatched
        self.ambiguity_margin = ambiguity_margin

    def calculate_temporal_score(self, event_date_str: Optional[str], plan_start_str: Optional[str], plan_finish_str: Optional[str]) -> float:
        """Evaluates temporal compatibility between event date and planned schedule window."""
        if not event_date_str or not plan_start_str:
            return 0.50  # Neutral score if temporal data missing

        try:
            event_dt = datetime.strptime(event_date_str[:10], "%Y-%m-%d")
            start_dt = datetime.strptime(plan_start_str[:10], "%Y-%m-%d")
            finish_dt = datetime.strptime(plan_finish_str[:10], "%Y-%m-%d") if plan_finish_str else start_dt + timedelta(days=7)

            # Within planned window (with 7-day buffer)
            if (start_dt - timedelta(days=7)) <= event_dt <= (finish_dt + timedelta(days=7)):
                return 1.0
            # Within 30-day window
            elif (start_dt - timedelta(days=30)) <= event_dt <= (finish_dt + timedelta(days=30)):
                return 0.50
            else:
                return 0.10
        except Exception:
            return 0.50

    def evaluate_candidate(self, event: ExecutionEvent, fp: ActivityFingerprint) -> CandidateMatch:
        """Computes multi-factor match score breakdown for a candidate activity fingerprint."""
        reasons: List[str] = []

        # 1. Exact Identifier Score
        exact_id_score = 0.0
        if event.observed_activity_id and event.observed_activity_id.upper() == fp.activity_id.upper():
            exact_id_score = 1.0
            reasons.append(f"+ Explicit Activity ID '{fp.activity_id}' matches baseline schedule activity {fp.activity_id}")
        elif event.raw_observed_activity_id and event.raw_observed_activity_id.upper() == fp.activity_id.upper():
            exact_id_score = 1.0
            reasons.append(f"+ Raw explicit reference '{fp.activity_id}' matches baseline schedule activity {fp.activity_id}")

        # 2. Line / Equipment Tag Score
        line_eq_score = 0.0
        if event.line_number and fp.line_number and event.line_number.lower() == fp.line_number.lower():
            line_eq_score += 0.6
            reasons.append(f"+ Line number '{event.line_number}' matches activity line reference")
        if event.equipment_tag and fp.equipment_tag and event.equipment_tag.lower() == fp.equipment_tag.lower():
            line_eq_score += 0.4
            reasons.append(f"+ Equipment tag '{event.equipment_tag}' matches activity equipment tag")
        line_eq_score = min(1.0, line_eq_score)

        # 3. Spatial / Chainage Score
        spatial_score = 0.0
        if event.area_location and fp.area_location:
            ev_loc = event.area_location.lower()
            fp_loc = fp.area_location.lower()
            if ev_loc in fp_loc or fp_loc in ev_loc:
                spatial_score = 1.0
                reasons.append(f"+ Location area '{event.area_location}' matches activity zone '{fp.area_location}'")

        # 4. WBS Structural Score
        wbs_score = 0.0
        if event.area_location and event.area_location.lower() in fp.wbs_name_path.lower():
            wbs_score = 0.80
            reasons.append(f"+ Location '{event.area_location}' aligns with WBS path '{fp.wbs_name_path}'")
        elif fp.wbs_code:
            wbs_score = 0.50

        # 5. Discipline Score
        disc_score = 0.0
        if event.discipline != "UNKNOWN" and fp.discipline != "UNKNOWN":
            if event.discipline.upper() == fp.discipline.upper():
                disc_score = 1.0
                reasons.append(f"+ Discipline '{event.discipline}' matches activity discipline '{fp.discipline}'")
            elif {event.discipline.upper(), fp.discipline.upper()} <= {"CIVIL", "PIPING"}:
                disc_score = 0.40

        # 6. Terminology & Action Verbs Score
        term_score = 0.0
        stmt_lower = event.extracted_statement.lower()
        
        # Check action verb matches
        matched_actions = [v for v in fp.action_verbs if v in stmt_lower]
        if matched_actions:
            term_score += 0.50
            reasons.append(f"+ Action verb(s) {matched_actions} match activity action verb(s)")

        # Check entity noun / synonym matches
        matched_nouns = [n for n in fp.entity_nouns if n in stmt_lower]
        matched_syns = [s for s in fp.synonyms if s in stmt_lower]
        if matched_nouns or matched_syns:
            term_score += 0.50
            reasons.append(f"+ Technical entities/synonyms match activity vocabulary")
        term_score = min(1.0, term_score)

        # 7. Temporal Window Score
        temp_score = self.calculate_temporal_score(event.observed_timestamp, fp.planned_start, fp.planned_finish)
        if temp_score >= 0.80:
            reasons.append(f"+ Event date '{event.observed_timestamp}' falls within planned baseline window ({fp.planned_start} to {fp.planned_finish})")

        # 8. Multi-Factor Weighted Aggregation
        non_id_score = (
            0.25 * line_eq_score +
            0.25 * spatial_score +
            0.15 * wbs_score +
            0.15 * disc_score +
            0.15 * term_score +
            0.05 * temp_score
        )

        if exact_id_score == 1.0:
            overall = min(1.0, 0.70 + 0.30 * non_id_score)
        else:
            overall = non_id_score

        overall = round(min(1.0, max(0.0, overall)), 2)

        scores = MatchFactorScores(
            exact_identifier_score=round(exact_id_score, 2),
            line_equipment_score=round(line_eq_score, 2),
            spatial_chainage_score=round(spatial_score, 2),
            wbs_structural_score=round(wbs_score, 2),
            discipline_score=round(disc_score, 2),
            terminology_action_score=round(term_score, 2),
            temporal_window_score=round(temp_score, 2),
            overall_confidence_score=overall
        )

        return CandidateMatch(
            activity_id=fp.activity_id,
            activity_name=fp.activity_name,
            project_id=fp.project_id,
            wbs_name_path=fp.wbs_name_path,
            scores=scores,
            match_reasons=reasons
        )

    def match_event_to_fingerprints(
        self,
        event: ExecutionEvent,
        fingerprints: List[ActivityFingerprint]
    ) -> MatchResult:
        """
        Executes candidate generation, multi-factor scoring, outcome classification,
        and reasoning trace construction.
        """
        from datetime import timezone
        match_id = f"MTH-{uuid.uuid4().hex[:8].upper()}"
        evaluated_at = datetime.now(timezone.utc).isoformat()

        if not fingerprints:
            return MatchResult(
                match_id=match_id,
                event_id=event.event_id,
                source_id=event.source_id,
                outcome=MatchOutcome.UNMATCHED,
                confidence_score=0.0,
                reasoning_trace=["No baseline schedule activity fingerprints available for candidate search."],
                evaluated_at=evaluated_at
            )

        # Stage 1: Candidate Scoring
        candidates: List[CandidateMatch] = []
        for fp in fingerprints:
            cand = self.evaluate_candidate(event, fp)
            if cand.scores.overall_confidence_score > 0.15:
                candidates.append(cand)

        # Sort candidates by overall confidence score descending
        candidates.sort(key=lambda c: c.scores.overall_confidence_score, reverse=True)

        # Stage 2: Outcome Classification
        if not candidates:
            return MatchResult(
                match_id=match_id,
                event_id=event.event_id,
                source_id=event.source_id,
                outcome=MatchOutcome.UNMATCHED,
                confidence_score=0.0,
                reasoning_trace=["No baseline activity exceeded minimum matching threshold (0.15)."],
                evaluated_at=evaluated_at
            )

        top = candidates[0]
        top_score = top.scores.overall_confidence_score
        second_score = candidates[1].scores.overall_confidence_score if len(candidates) > 1 else 0.0
        score_margin = round(top_score - second_score, 2)

        # Determine Outcome
        if top_score >= self.theta_match and score_margin > self.ambiguity_margin:
            outcome = MatchOutcome.MATCHED
            selected_act_id = top.activity_id
            selected_act_name = top.activity_name
            trace = [
                f"Status: MATCHED (Activity: {top.activity_id}, Confidence: {top_score})",
                f"Selected Top Candidate: {top.activity_id} - {top.activity_name}"
            ] + top.match_reasons
        elif top_score >= self.theta_unmatched or (len(candidates) > 1 and score_margin <= self.ambiguity_margin):
            outcome = MatchOutcome.AMBIGUOUS
            selected_act_id = None
            selected_act_name = None
            trace = [
                f"Status: AMBIGUOUS (Top Confidence: {top_score}, Margin to 2nd: {score_margin})",
                f"Multiple viable activity candidates found. Flagged for Human Planner (HITL) review."
            ]
            for idx, c in enumerate(candidates[:3]):
                trace.append(f"  Candidate {idx+1}: {c.activity_id} - {c.activity_name} (Score: {c.scores.overall_confidence_score})")
        else:
            outcome = MatchOutcome.UNMATCHED
            selected_act_id = None
            selected_act_name = None
            trace = [
                f"Status: UNMATCHED (Top Confidence: {top_score} < Threshold {self.theta_unmatched})",
                "No candidate activity reached required matching confidence threshold."
            ]

        return MatchResult(
            match_id=match_id,
            event_id=event.event_id,
            source_id=event.source_id,
            outcome=outcome,
            selected_activity_id=selected_act_id,
            selected_activity_name=selected_act_name,
            confidence_score=top_score,
            top_candidate=top,
            candidate_matches=candidates[:5],  # Keep top 5 candidates
            reasoning_trace=trace,
            evaluated_at=evaluated_at
        )
