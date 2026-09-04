"""
SATYA Time Agent Monitoring API Router Handler (Phase 13)
Delegates proactive temporal monitoring evaluations, early-warning signal queries,
and trace details to TimeAgentService.
"""

from typing import Dict, Any, Optional
from backend.monitoring.time_agent_service import TimeAgentService
from backend.models.domain_models import TemporalMonitoringPolicy
from backend.api.errors import SATYAError
from backend.api.serializers import serialize_temporal_warning_signal, serialize_monitoring_evaluation_run

class MonitoringRouteHandler:

    def __init__(self, monitoring_service: TimeAgentService):
        self.monitoring_service = monitoring_service

    def handle_evaluate_monitoring(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/v1/monitoring/evaluate
        Payload: {project_id, as_of_date, policy}
        Runs Time Agent temporal evaluation and saves auditable signals.
        """
        project_id = payload.get("project_id")
        as_of_date = payload.get("as_of_date")

        if not project_id:
            raise SATYAError(
                code="INVALID_PAYLOAD",
                message="Missing required field: project_id is required.",
                status_code=400
            )

        res = self.monitoring_service.run_monitoring_evaluation(
            project_id=project_id,
            as_of_date=as_of_date
        )
        return res

    def handle_get_active_signals(
        self,
        project_id: str,
        severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        GET /api/v1/monitoring/projects/{project_id}/signals?severity=...
        Returns active temporal warning signals for a project.
        """
        signals = self.monitoring_service.db.get_active_signals_by_project(project_id, severity_filter=severity)
        return {
            "project_id": project_id,
            "severity_filter": severity,
            "signal_count": len(signals),
            "signals": signals
        }

    def handle_get_signal_details(self, signal_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/monitoring/signals/{signal_id}
        Returns detailed TemporalWarningSignal trace and reasoning.
        """
        sig = self.monitoring_service.db.get_signal_by_id(signal_id)
        if not sig:
            raise SATYAError(
                code="SIGNAL_NOT_FOUND",
                message=f"Temporal warning signal with ID '{signal_id}' not found.",
                status_code=404
            )
        return sig
