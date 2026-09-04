"""
SATYA Activity Fingerprinting Engine
Generates multi-dimensional ActivityFingerprints (structural + semantic + spatial + temporal + terminology)
from Primavera P6 / MS Project baseline schedule data.
"""

import uuid
import re
from typing import List, Dict, Any, Optional, Set
from backend.models.domain_models import ActivityFingerprint
from backend.fingerprinting.terminology_engine import TerminologyIntelligenceEngine

class ActivityFingerprintGenerator:
    """Computes rich searchable ActivityFingerprints from schedule baseline data."""

    def __init__(self):
        self.term_engine = TerminologyIntelligenceEngine()

    def build_wbs_lookup(self, wbs_hierarchy: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Maps WBS ID to WBS record for rapid parent lookup."""
        lookup = {}
        for wbs in wbs_hierarchy:
            if isinstance(wbs, dict) and "wbs_id" in wbs:
                lookup[wbs["wbs_id"]] = wbs
        return lookup

    def get_wbs_name_path(self, wbs_id: str, wbs_lookup: Dict[str, Dict[str, Any]]) -> str:
        """Traverses WBS tree to construct topological human-readable path (e.g. Project > Piping > Section 1)."""
        path_names = []
        curr_id = wbs_id
        visited: Set[str] = set()

        while curr_id and curr_id in wbs_lookup and curr_id not in visited:
            visited.add(curr_id)
            wbs_item = wbs_lookup[curr_id]
            name = wbs_item.get("wbs_name", wbs_item.get("wbs_code", curr_id))
            path_names.insert(0, name)
            curr_id = wbs_item.get("parent_id")

        return " > ".join(path_names) if path_names else wbs_id

    def generate_fingerprint(
        self,
        activity: Dict[str, Any],
        project_id: str,
        wbs_lookup: Dict[str, Dict[str, Any]]
    ) -> ActivityFingerprint:
        """Generates single ActivityFingerprint from raw activity dictionary and WBS lookup."""
        act_id = activity.get("activity_id", f"ACT-{uuid.uuid4().hex[:6].upper()}")
        act_name = activity.get("activity_name", "Unspecified Activity")
        wbs_id = activity.get("wbs_id", "WBS-000")
        wbs_code = activity.get("wbs_path", activity.get("wbs_code", wbs_id))

        # WBS Topological Path
        wbs_name_path = self.get_wbs_name_path(wbs_id, wbs_lookup)

        # Normalize Name
        normalized_name = re.sub(r'[ \t]+', ' ', act_name.strip())

        # Semantic & Terminology Extraction
        action_verbs = self.term_engine.extract_action_verbs(act_name)
        entity_nouns = self.term_engine.extract_entity_nouns(act_name + " " + wbs_name_path)
        synonyms, field_aliases = self.term_engine.generate_synonyms_and_aliases(act_name)
        discipline = activity.get("discipline", "UNKNOWN")
        search_tokens = self.term_engine.generate_search_tokens(act_name, wbs_name_path, discipline)

        # Predecessors & Successors
        preds = []
        if activity.get("predecessor_id"):
            preds.append(str(activity["predecessor_id"]))
        succs = []
        if activity.get("successor_id"):
            succs.append(str(activity["successor_id"]))

        fingerprint_id = f"FPT-{act_id}"

        return ActivityFingerprint(
            fingerprint_id=fingerprint_id,
            activity_id=act_id,
            project_id=project_id,
            activity_name=act_name,
            normalized_name=normalized_name,
            wbs_id=wbs_id,
            wbs_code=wbs_code,
            wbs_name_path=wbs_name_path,
            discipline=discipline,
            area_location=activity.get("area"),
            equipment_tag=activity.get("equipment_tag"),
            line_number=activity.get("line_number"),
            start_km=activity.get("start_km"),
            end_km=activity.get("end_km"),
            planned_start=activity.get("planned_start"),
            planned_finish=activity.get("planned_finish"),
            baseline_duration_days=activity.get("baseline_duration_days", 0),
            planned_quantity=activity.get("planned_quantity"),
            unit_of_measure=activity.get("unit"),
            is_critical=activity.get("is_critical", False),
            predecessors=preds,
            successors=succs,
            action_verbs=action_verbs,
            entity_nouns=entity_nouns,
            synonyms=synonyms,
            field_aliases=field_aliases,
            search_tokens=search_tokens,
            fingerprint_version="v1.0"
        )

    def generate_schedule_fingerprints(self, schedule_payload: Dict[str, Any]) -> List[ActivityFingerprint]:
        """Generates ActivityFingerprints for 100% of activities in a baseline schedule payload."""
        project_data = schedule_payload.get("project", {})
        project_id = project_data.get("project_id", "PRJ-UNKNOWN")
        wbs_hierarchy = schedule_payload.get("wbs_hierarchy", [])
        activities = schedule_payload.get("activities", [])

        wbs_lookup = self.build_wbs_lookup(wbs_hierarchy)
        fingerprints: List[ActivityFingerprint] = []

        for act in activities:
            if isinstance(act, dict) and "activity_id" in act:
                fp = self.generate_fingerprint(act, project_id, wbs_lookup)
                fingerprints.append(fp)

        return fingerprints
