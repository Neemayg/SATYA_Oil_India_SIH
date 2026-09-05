"""
SATYA Backend Application API Router (Phase 11)
HTTP application router handling request parsing, route dispatching,
CORS header injection, error mapping, and service layer orchestration.
"""

import os
import json
import uuid
import logging
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Tuple, Optional

from backend.persistence.database_engine import DatabaseEngine
from backend.services.pipeline_service import ExecutionEventPipelineService
from backend.services.fingerprint_service import ActivityFingerprintService
from backend.services.matching_service import ScheduleMatchingService
from backend.services.trust_evaluator_service import TrustEvaluatorService
from backend.hitl.queue_manager import PlannerQueueManager
from backend.hitl.validation_service import ValidationService
from backend.projection.projection_service import ScheduleProjectionService

from backend.api.errors import SATYAError
from backend.projection.projection_service import ScheduleProjectionService
from backend.monitoring.time_agent_service import TimeAgentService
from backend.api.openapi import generate_openapi_schema
from backend.api.routes_ingestion import IngestionRouteHandler
from backend.api.routes_fingerprints import FingerprintsRouteHandler
from backend.api.routes_matching import MatchingRouteHandler
from backend.api.routes_evidence import EvidenceRouteHandler
from backend.api.routes_hitl import HITLRouteHandler
from backend.api.routes_projections import ProjectionsRouteHandler
from backend.api.routes_monitoring import MonitoringRouteHandler
from backend.api.routes_analytics import AnalyticsRouteHandler
from backend.api.routes_audit import AuditRouteHandler

logger = logging.getLogger("SATYA.API")

class SATYAApplicationAPI:
    """
    HTTP Application Router wrapping established SATYA service layers.
    Can be run via standard library http.server, WSGI, or invoked directly in unit tests.
    """

    def __init__(self, db_engine: Optional[DatabaseEngine] = None):
        self.db = db_engine or DatabaseEngine(":memory:")

        # Initialize established service layer
        self.pipeline_service = ExecutionEventPipelineService(self.db)
        self.fingerprint_service = ActivityFingerprintService(self.db)
        self.matching_service = ScheduleMatchingService(self.db)
        self.trust_service = TrustEvaluatorService(self.db)
        self.queue_manager = PlannerQueueManager(self.db)
        self.validation_service = ValidationService(self.db)
        self.projection_service = ScheduleProjectionService(self.db)
        self.monitoring_service = TimeAgentService(self.db)

        # Initialize route handlers
        self.ingestion_handler = IngestionRouteHandler(self.pipeline_service)
        self.fingerprints_handler = FingerprintsRouteHandler(self.fingerprint_service)
        self.matching_handler = MatchingRouteHandler(self.matching_service)
        self.evidence_handler = EvidenceRouteHandler(self.trust_service)
        self.hitl_handler = HITLRouteHandler(self.queue_manager, self.validation_service)
        self.projections_handler = ProjectionsRouteHandler(self.projection_service)
        self.monitoring_handler = MonitoringRouteHandler(self.monitoring_service)
        self.analytics_handler = AnalyticsRouteHandler(self.db)
        self.audit_handler = AuditRouteHandler(self.db)

        # Configurable CORS origins
        allowed_origins_raw = os.environ.get(
            "SATYA_ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
        )
        self.allowed_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]

    def get_cors_headers(self, request_origin: Optional[str] = None) -> Dict[str, str]:
        """Returns restrictive CORS headers based on configured origins."""
        origin = request_origin if (request_origin and request_origin in self.allowed_origins) else self.allowed_origins[0]
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID",
            "Content-Type": "application/json"
        }

    def dispatch(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        request_origin: Optional[str] = None
    ) -> Tuple[int, Dict[str, str], Dict[str, Any]]:
        """
        Dispatches HTTP request to appropriate route handler and catches errors.
        Returns Tuple[status_code, headers_dict, body_json_dict].
        """
        headers = self.get_cors_headers(request_origin)
        params = params or {}
        body = body or {}

        if method.upper() == "OPTIONS":
            return 200, headers, {"status": "CORS_OK"}

        try:
            # 1. Health & OpenAPI Routes
            if method == "GET" and path == "/api/v1/health":
                return 200, headers, {
                    "status": "healthy",
                    "service": "satya-api",
                    "database": "healthy",
                    "api_version": "v1"
                }
            elif method == "GET" and path == "/api/v1/openapi.json":
                return 200, headers, generate_openapi_schema()

            # 2. Ingestion Routes
            elif method == "POST" and path == "/api/v1/ingestion/upload":
                res = self.ingestion_handler.handle_upload(body)
                return 201, headers, res
            elif method == "GET" and path.startswith("/api/v1/ingestion/sources/"):
                source_id = path.replace("/api/v1/ingestion/sources/", "").strip()
                res = self.ingestion_handler.handle_get_source(source_id)
                return 200, headers, res
            elif method == "GET" and path.startswith("/api/v1/ingestion/events/"):
                event_id = path.replace("/api/v1/ingestion/events/", "").strip()
                res = self.ingestion_handler.handle_get_event(event_id)
                return 200, headers, res

            # 3. Fingerprints Routes
            elif method == "POST" and path == "/api/v1/fingerprints/index":
                res = self.fingerprints_handler.handle_index_schedule(body)
                return 200, headers, res
            elif method == "GET" and path.startswith("/api/v1/fingerprints/projects/"):
                project_id = path.replace("/api/v1/fingerprints/projects/", "").strip()
                res = self.fingerprints_handler.handle_get_project_fingerprints(project_id)
                return 200, headers, res
            elif method == "GET" and path == "/api/v1/fingerprints/search":
                q = params.get("q", "")
                disc = params.get("discipline")
                res = self.fingerprints_handler.handle_search_fingerprints(q, disc)
                return 200, headers, res

            # 4. Matching Routes
            elif method == "POST" and path == "/api/v1/matching/match":
                res = self.matching_handler.handle_match_event(body)
                return 200, headers, res
            elif method == "GET" and path.startswith("/api/v1/matching/events/"):
                event_id = path.replace("/api/v1/matching/events/", "").strip()
                res = self.matching_handler.handle_get_event_matches(event_id)
                return 200, headers, res

            # 5. Evidence & Trust Routes
            elif method == "POST" and path == "/api/v1/evidence/evaluate":
                res = self.evidence_handler.handle_evaluate_trust(body)
                return 200, headers, res
            elif method == "GET" and path.endswith("/trust") and path.startswith("/api/v1/evidence/events/"):
                parts = path.split("/")
                event_id = parts[-2]
                res = self.evidence_handler.handle_get_event_trust(event_id)
                return 200, headers, res
            elif method == "GET" and path.endswith("/conflicts") and path.startswith("/api/v1/evidence/events/"):
                parts = path.split("/")
                event_id = parts[-2]
                res = self.evidence_handler.handle_get_event_conflicts(event_id)
                return 200, headers, res
            elif method == "GET" and path.endswith("/trace") and path.startswith("/api/v1/evidence/events/"):
                parts = path.split("/")
                event_id = parts[-2]
                res = self.evidence_handler.handle_get_event_trace(event_id)
                return 200, headers, res

            # 6. HITL Queue & Decisions Routes
            elif method == "GET" and path == "/api/v1/hitl/queue":
                proj_id = params.get("project_id")
                prio = params.get("priority")
                res = self.hitl_handler.handle_get_queue(project_id=proj_id, priority=prio)
                return 200, headers, res
            elif method == "POST" and path == "/api/v1/hitl/decisions":
                res = self.hitl_handler.handle_submit_decision(body)
                return 200, headers, res

            # 7. Schedule Projections Routes
            elif method == "POST" and path == "/api/v1/projections/generate":
                res = self.projections_handler.handle_generate_projection(body)
                return 200, headers, res
            elif method == "GET" and path.endswith("/latest") and path.startswith("/api/v1/projections/projects/"):
                parts = path.split("/")
                project_id = parts[-2]
                res = self.projections_handler.handle_get_latest_projection(project_id)
                return 200, headers, res
            elif method == "GET" and "/activities/" in path and path.startswith("/api/v1/projections/projects/"):
                # Format: /api/v1/projections/projects/{project_id}/activities/{activity_id}
                parts = path.split("/")
                project_id = parts[5]
                activity_id = parts[7]
                res = self.projections_handler.handle_get_activity_progress(project_id, activity_id)
                return 200, headers, res

            # 8. Time Agent Monitoring Routes
            elif method == "POST" and path == "/api/v1/monitoring/evaluate":
                res = self.monitoring_handler.handle_evaluate_monitoring(body)
                return 200, headers, res
            elif method == "GET" and path.endswith("/signals") and path.startswith("/api/v1/monitoring/projects/"):
                parts = path.split("/")
                project_id = parts[-2]
                sev = params.get("severity")
                res = self.monitoring_handler.handle_get_active_signals(project_id, severity=sev)
                return 200, headers, res
            elif method == "GET" and path.startswith("/api/v1/monitoring/signals/"):
                signal_id = path.replace("/api/v1/monitoring/signals/", "").strip()
                res = self.monitoring_handler.handle_get_signal_details(signal_id)
                return 200, headers, res

            # 9. Institutional Memory & Analytics Routes (Phase 14)
            elif method == "POST" and path.endswith("/distill") and path.startswith("/api/v1/memory/projects/"):
                parts = path.split("/")
                project_id = parts[-2]
                as_of = body.get("as_of_date") if body else None
                res = self.analytics_handler.distill_memory(project_id, as_of_date=as_of)
                return 200, headers, res
            elif method == "GET" and path.endswith("/aliases") and path.startswith("/api/v1/memory/projects/"):
                parts = path.split("/")
                project_id = parts[-2]
                st = params.get("status")
                res = self.analytics_handler.get_aliases(project_id, status_filter=st)
                return 200, headers, res
            elif method == "GET" and path.endswith("/productivity") and path.startswith("/api/v1/analytics/projects/"):
                parts = path.split("/")
                project_id = parts[-2]
                res = self.analytics_handler.get_productivity_benchmarks(project_id)
                return 200, headers, res
            elif method == "GET" and path.endswith("/contractors") and path.startswith("/api/v1/analytics/projects/"):
                parts = path.split("/")
                project_id = parts[-2]
                res = self.analytics_handler.get_contractor_profiles(project_id)
                return 200, headers, res
            elif method == "GET" and path.endswith("/conflicts") and path.startswith("/api/v1/analytics/projects/"):
                parts = path.split("/")
                project_id = parts[-2]
                res = self.analytics_handler.get_conflict_patterns(project_id)
                return 200, headers, res

            # --- Manager audit report ---
            elif method == "GET" and path.startswith("/api/v1/audit/projects/"):
                project_id = path.replace("/api/v1/audit/projects/", "").strip("/")
                res = self.audit_handler.get_project_audit(project_id)
                return 200, headers, res

            else:
                raise SATYAError(
                    code="ROUTE_NOT_FOUND",
                    message=f"Endpoint path '{path}' with method '{method}' not found.",
                    status_code=404
                )

        except SATYAError as err:
            logger.warning(f"API Error {err.status_code} [{err.code}]: {err.message}")
            return err.status_code, headers, err.to_dict()
        except Exception as ex:
            logger.error(f"Unhandled Server Error on {method} {path}: {str(ex)}", exc_info=True)
            err = SATYAError(
                code="INTERNAL_SERVER_ERROR",
                message=f"An internal error occurred: {str(ex)}",
                status_code=500
            )
            return 500, headers, err.to_dict()
