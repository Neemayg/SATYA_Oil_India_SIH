"""
SATYA Schedule Projections API Router Handler (Phase 11)
Delegates baseline-immutable schedule progress calculation and snapshot generation to ScheduleProjectionService.
"""

from typing import Dict, Any, Optional
from backend.projection.projection_service import ScheduleProjectionService
from backend.api.errors import SATYAError
from backend.api.serializers import serialize_schedule_projection, serialize_activity_progress

class ProjectionsRouteHandler:

    def __init__(self, projection_service: ScheduleProjectionService):
        self.projection_service = projection_service

    def handle_generate_projection(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/projections/generate
        Payload: {project_id, as_of_date}
        """
        project_id = payload.get("project_id")
        as_of_date = payload.get("as_of_date")

        if not project_id:
            raise SATYAError(
                code="INVALID_PAYLOAD",
                message="Missing required field: project_id.",
                status_code=400
            )

        try:
            projection = self.projection_service.generate_projection_for_project(
                project_id=project_id,
                as_of_date=as_of_date
            )
        except Exception as ex:
            raise SATYAError(
                code="PROJECTION_GENERATION_FAILED",
                message=str(ex),
                status_code=400
            )

        return serialize_schedule_projection(projection)

    def handle_get_latest_projection(self, project_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/projections/projects/{project_id}/latest
        """
        proj_dict = self.projection_service.db.get_latest_schedule_projection(project_id)
        if not proj_dict:
            raise SATYAError(
                code="PROJECTION_NOT_FOUND",
                message=f"No schedule projection snapshots found for project '{project_id}'.",
                status_code=404
            )
        return proj_dict

    def handle_get_activity_progress(self, project_id: str, activity_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/projections/projects/{project_id}/activities/{activity_id}
        """
        proj_dict = self.projection_service.db.get_latest_schedule_projection(project_id)
        if not proj_dict:
            raise SATYAError(
                code="PROJECTION_NOT_FOUND",
                message=f"No schedule projection snapshots found for project '{project_id}'.",
                status_code=404
            )

        act_map = proj_dict.get("activity_progress_map", {})
        act_prog = act_map.get(activity_id)

        if not act_prog:
            raise SATYAError(
                code="ACTIVITY_PROGRESS_NOT_FOUND",
                message=f"Activity progress for '{activity_id}' not found in project '{project_id}'.",
                status_code=404
            )

        return {
            "project_id": project_id,
            "activity_id": activity_id,
            "as_of_date": proj_dict.get("as_of_date"),
            "activity_progress": act_prog
        }
