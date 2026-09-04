"""
SATYA Fingerprints API Router Handler (Phase 11)
Delegates schedule activity fingerprinting and lookup to ActivityFingerprintService.
"""

from typing import Dict, Any, List, Optional
from backend.services.fingerprint_service import ActivityFingerprintService
from backend.api.errors import SATYAError

class FingerprintsRouteHandler:

    def __init__(self, fingerprint_service: ActivityFingerprintService):
        self.fingerprint_service = fingerprint_service

    def handle_index_schedule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/fingerprints/index
        Payload: {project_id, schedule_path}
        """
        project_id = payload.get("project_id")
        schedule_path = payload.get("schedule_path")

        if not project_id and not schedule_path:
            raise SATYAError(
                code="INVALID_PAYLOAD",
                message="project_id or schedule_path is required.",
                status_code=400
            )

        fps = self.fingerprint_service.process_schedule_file(schedule_path)
        return {
            "status": "SUCCESS",
            "project_id": project_id or (fps[0].project_id if fps else "UNKNOWN"),
            "indexed_fingerprints_count": len(fps)
        }

    def handle_get_project_fingerprints(self, project_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/fingerprints/projects/{project_id}
        """
        fps_dicts = self.fingerprint_service.db.get_fingerprints_by_project(project_id)
        if not fps_dicts:
            raise SATYAError(
                code="PROJECT_NOT_FOUND",
                message=f"No activity fingerprints found for project '{project_id}'.",
                status_code=404
            )
        return {
            "project_id": project_id,
            "count": len(fps_dicts),
            "fingerprints": fps_dicts
        }

    def handle_search_fingerprints(self, query: str, discipline: Optional[str] = None) -> Dict[str, Any]:
        """
        GET /api/v1/fingerprints/search?q=...&discipline=...
        Explicitly positioned as human/system lookup of indexed schedule activities.
        """
        fps_dicts = self.fingerprint_service.db.get_all_fingerprints()
        q_lower = (query or "").strip().lower()
        disc_lower = (discipline or "").strip().lower()

        results = []
        for fp in fps_dicts:
            name = (fp.get("activity_name") or "").lower()
            code = (fp.get("activity_id") or "").lower()
            disc = (fp.get("discipline") or "").lower()

            match_q = not q_lower or (q_lower in name or q_lower in code)
            match_disc = not disc_lower or (disc_lower in disc)

            if match_q and match_disc:
                results.append(fp)

        return {
            "query": query,
            "discipline": discipline,
            "count": len(results),
            "results": results
        }
