"""
SATYA Activity Fingerprinting Service Orchestrator
Coordinates schedule baseline loading, ActivityFingerprint generation, database caching,
and vocabulary export for downstream pipeline guardrails.
"""

import os
import json
import logging
from typing import List, Dict, Any, Set, Optional
from backend.models.domain_models import ActivityFingerprint
from backend.fingerprinting.fingerprint_generator import ActivityFingerprintGenerator
from backend.persistence.database_engine import DatabaseEngine

logger = logging.getLogger("SATYA.Fingerprinting")

class ActivityFingerprintService:
    """Service orchestrator for schedule fingerprinting and activity identity indexing."""

    def __init__(self, db_engine: Optional[DatabaseEngine] = None):
        self.db = db_engine if db_engine else DatabaseEngine(":memory:")
        self.generator = ActivityFingerprintGenerator()

    def process_schedule_file(self, schedule_file_path: str) -> List[ActivityFingerprint]:
        """
        Loads a baseline schedule JSON file, generates ActivityFingerprints,
        persists them to SQLite database, and returns the list of generated fingerprints.
        """
        if not os.path.exists(schedule_file_path):
            raise FileNotFoundError(f"Schedule file not found: {schedule_file_path}")

        with open(schedule_file_path, 'r', encoding='utf-8') as f:
            schedule_payload = json.load(f)

        project_id = schedule_payload.get("project", {}).get("project_id", "PRJ-UNKNOWN")
        logger.info(f"Generating ActivityFingerprints for project {project_id} from {os.path.basename(schedule_file_path)}")

        fingerprints = self.generator.generate_schedule_fingerprints(schedule_payload)

        # Persist to database
        for fp in fingerprints:
            self.db.save_activity_fingerprint(fp)

        logger.info(f"Successfully generated and persisted {len(fingerprints)} ActivityFingerprints for project {project_id}")
        return fingerprints

    def load_all_synthetic_schedules(self, schedules_dir: str) -> List[ActivityFingerprint]:
        """
        Scans schedules_dir for baseline schedule files and fingerprints 100% of baseline activities.
        """
        all_fingerprints: List[ActivityFingerprint] = []
        if not os.path.exists(schedules_dir):
            logger.warning(f"Schedules directory does not exist: {schedules_dir}")
            return all_fingerprints

        for fname in sorted(os.listdir(schedules_dir)):
            if fname.endswith(".json") and ("baseline" in fname or "schedule" in fname):
                fpath = os.path.join(schedules_dir, fname)
                fps = self.process_schedule_file(fpath)
                all_fingerprints.extend(fps)

        return all_fingerprints

    def get_valid_activity_vocabulary(self) -> Set[str]:
        """Returns set of all valid activity IDs present in the database index."""
        fps = self.db.get_all_fingerprints()
        return {fp["activity_id"].upper() for fp in fps if "activity_id" in fp}
