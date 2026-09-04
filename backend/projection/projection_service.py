"""
SATYA Schedule Projection Service (Phase 10)
Orchestrates baseline schedule indexing, trusted event querying,
progress calculation, and snapshot persistence.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from backend.persistence.database_engine import DatabaseEngine
from backend.models.domain_models import ScheduleProjection, ExecutionEvent
from backend.projection.actual_progress_engine import ActualProgressEngine

logger = logging.getLogger("SATYA.ProjectionService")

class ScheduleProjectionService:
    """
    Service layer orchestrating the generation and persistence of reproducible
    ScheduleProjection snapshots for a project.
    """

    def __init__(self, db_engine: DatabaseEngine):
        self.db = db_engine
        self.engine = ActualProgressEngine()

    def _find_baseline_schedule_file(self, project_id: str) -> str:
        """Finds baseline schedule JSON file path for a project ID."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schedules_dir = os.path.join(base_dir, "data", "synthetic", "schedules")
        
        if project_id == "PRJ-SCP-2026":
            return os.path.join(schedules_dir, "project2_baseline_schedule.json")
        return os.path.join(schedules_dir, "baseline_schedule.json")

    def generate_projection_for_project(
        self,
        project_id: str,
        as_of_date: Optional[str] = None,
        schedule_json_path: Optional[str] = None
    ) -> ScheduleProjection:
        """
        Queries immutable source state (baseline schedule, execution events, trust assessments)
        and derives a new, reproducible ScheduleProjection snapshot.
        """
        if not as_of_date:
            as_of_date = datetime.now().strftime("%Y-%m-%d")

        if not schedule_json_path:
            schedule_json_path = self._find_baseline_schedule_file(project_id)

        if not os.path.exists(schedule_json_path):
            raise FileNotFoundError(f"Baseline schedule JSON file not found: {schedule_json_path}")

        with open(schedule_json_path, "r", encoding="utf-8") as f:
            sched_data = json.load(f)

        activities = sched_data.get("activities", [])
        wbs_hierarchy = sched_data.get("wbs_hierarchy", [])

        # Fetch all execution events and trust assessments for project
        all_events_dicts = self.db.get_all_execution_events()
        
        # Filter events for target project
        project_events: List[ExecutionEvent] = []
        project_trust_assessments: List[Dict[str, Any]] = []

        for ev_dict in all_events_dicts:
            event_id = ev_dict.get("event_id")
            # We fetch source document to check project_id if needed, or filter by event
            # For efficiency, re-construct ExecutionEvent object
            ev = ExecutionEvent(
                event_id=ev_dict["event_id"],
                source_id=ev_dict["source_id"],
                fragment_id=ev_dict["fragment_id"],
                event_type=ev_dict["event_type"],
                observed_timestamp=ev_dict.get("observed_timestamp"),
                source_timestamp=ev_dict.get("source_timestamp", datetime.now().isoformat()),
                extracted_statement=ev_dict.get("extracted_statement", ""),
                raw_observed_activity_id=ev_dict.get("raw_observed_activity_id"),
                observed_activity_id=ev_dict.get("observed_activity_id"),
                discipline=ev_dict.get("discipline", "UNKNOWN"),
                observed_quantity=ev_dict.get("observed_quantity"),
                unit_of_measure=ev_dict.get("unit_of_measure"),
                progress_percent=ev_dict.get("progress_percent"),
                status_text=ev_dict.get("status_text"),
                pending_qa_clearance=bool(ev_dict.get("pending_qa_clearance", False))
            )
            project_events.append(ev)

            # Get trust history for this event
            trust_history = self.db.get_trust_assessments_by_event(event_id)
            if trust_history:
                latest_ta = trust_history[-1]  # Latest version
                project_trust_assessments.append(latest_ta)

        # Generate projection
        projection = self.engine.generate_projection(
            project_id=project_id,
            activities=activities,
            wbs_hierarchy=wbs_hierarchy,
            events=project_events,
            trust_assessments=project_trust_assessments,
            as_of_date=as_of_date
        )

        # Save to database
        self.db.save_schedule_projection(projection)
        logger.info(f"Persisted ScheduleProjection {projection.projection_id} for Project {project_id}")

        return projection
