"""
SATYA Analytics & Institutional Memory Route Handler (Phase 14)
Provides HTTP REST endpoints for memory distillation, terminology aliases,
productivity rate benchmarks, contractor reporting scorecards, and conflict resolution patterns.
"""

from typing import Dict, Any, List, Optional
from backend.analytics.memory_service import InstitutionalMemoryService
from backend.analytics.analytics_engine import ExecutionAnalyticsEngine
from backend.persistence.database_engine import DatabaseEngine
from backend.api.serializers import (
    serialize_memory_distillation_run, serialize_terminology_alias,
    serialize_execution_rate_benchmark, serialize_contractor_reporting_profile,
    serialize_conflict_resolution_pattern
)

class AnalyticsRouteHandler:
    def __init__(self, db: DatabaseEngine):
        self.db = db
        self.memory_service = InstitutionalMemoryService(db)
        self.analytics_engine = ExecutionAnalyticsEngine(db)

    def distill_memory(self, project_id: str, as_of_date: Optional[str] = None) -> Dict[str, Any]:
        """POST /api/v1/memory/projects/{project_id}/distill"""
        run = self.memory_service.distill_planner_corrections(project_id, as_of_date)
        return {
            "status": "success",
            "project_id": project_id,
            "distillation_run": serialize_memory_distillation_run(run)
        }

    def get_aliases(self, project_id: str, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """GET /api/v1/memory/projects/{project_id}/aliases"""
        aliases = self.db.get_terminology_aliases_by_project(project_id, status_filter)
        return {
            "project_id": project_id,
            "total_count": len(aliases),
            "aliases": [serialize_terminology_alias(a) for a in aliases]
        }

    def get_productivity_benchmarks(self, project_id: str) -> Dict[str, Any]:
        """GET /api/v1/analytics/projects/{project_id}/productivity"""
        benchmarks = self.analytics_engine.compute_execution_rate_benchmarks(project_id)
        return {
            "project_id": project_id,
            "total_count": len(benchmarks),
            "benchmarks": [serialize_execution_rate_benchmark(b) for b in benchmarks]
        }

    def get_contractor_profiles(self, project_id: str) -> Dict[str, Any]:
        """GET /api/v1/analytics/projects/{project_id}/contractors"""
        profiles = self.analytics_engine.compute_contractor_reporting_profiles(project_id)
        return {
            "project_id": project_id,
            "total_count": len(profiles),
            "disclaimer": "This profile describes historical reporting and evidence completeness characteristics; it is NOT a contractor performance, compliance, or contractual quality score.",
            "profiles": [serialize_contractor_reporting_profile(p) for p in profiles]
        }

    def get_conflict_patterns(self, project_id: str) -> Dict[str, Any]:
        """GET /api/v1/analytics/projects/{project_id}/conflicts"""
        patterns = self.analytics_engine.compute_conflict_resolution_patterns(project_id)
        return {
            "project_id": project_id,
            "total_count": len(patterns),
            "patterns": [serialize_conflict_resolution_pattern(p) for p in patterns]
        }
