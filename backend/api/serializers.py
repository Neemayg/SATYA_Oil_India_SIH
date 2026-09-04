"""
SATYA API Transport Serializers (Phase 11)
Provides thin, non-mutating transport serialization of domain models for HTTP JSON responses.
"""

from typing import Dict, Any, List, Optional
from backend.models.domain_models import (
    SourceDocument, SourceFragment, ExecutionEvent, MatchResult,
    EvidenceAssessment, TrustAssessment, ValidationDecision,
    PlannerQueueItem, ActivityProgress, ScheduleProjection
)

def serialize_source_bounded(doc: SourceDocument, event_ids: List[str]) -> Dict[str, Any]:
    """
    Returns bounded source document metadata and extracted event IDs list.
    Avoids uncontrolled giant recursive tree serialization.
    """
    return {
        "source_id": doc.source_id,
        "project_id": doc.project_id,
        "source_type": doc.source_type,
        "file_name": doc.file_name,
        "sha256_hash": doc.sha256_hash,
        "submitted_at": doc.submitted_at,
        "received_at": doc.received_at,
        "author": doc.author,
        "reporting_period": doc.reporting_period,
        "extraction_status": doc.extraction_status,
        "extracted_event_ids": event_ids,
        "extracted_event_count": len(event_ids)
    }

def serialize_execution_event(ev: ExecutionEvent) -> Dict[str, Any]:
    """Serializes ExecutionEvent for HTTP response."""
    return ev.to_dict()

def serialize_match_result(mr: MatchResult) -> Dict[str, Any]:
    """Serializes MatchResult for HTTP response."""
    return mr.to_dict()

def serialize_trust_assessment(ta: TrustAssessment) -> Dict[str, Any]:
    """Serializes TrustAssessment for HTTP response."""
    return ta.to_dict()

def serialize_validation_decision(vd: ValidationDecision) -> Dict[str, Any]:
    """Serializes ValidationDecision for HTTP response."""
    return vd.to_dict()

def serialize_planner_queue_item(item: PlannerQueueItem) -> Dict[str, Any]:
    """Serializes PlannerQueueItem for HTTP response."""
    return item.to_dict()

def serialize_activity_progress(ap: ActivityProgress) -> Dict[str, Any]:
    """Serializes ActivityProgress for HTTP response."""
    return ap.to_dict()

def serialize_schedule_projection(sp: ScheduleProjection) -> Dict[str, Any]:
    """Serializes ScheduleProjection for HTTP response."""
    return sp.to_dict()

def serialize_temporal_warning_signal(sig: Any) -> Dict[str, Any]:
    """Serializes TemporalWarningSignal for HTTP response."""
    return sig.to_dict() if hasattr(sig, "to_dict") else dict(sig)

def serialize_monitoring_evaluation_run(run: Any) -> Dict[str, Any]:
    """Serializes MonitoringEvaluationRun for HTTP response."""
    return run.to_dict() if hasattr(run, "to_dict") else dict(run)

def serialize_memory_distillation_run(run: Any) -> Dict[str, Any]:
    """Serializes MemoryDistillationRun for HTTP response."""
    return run.to_dict() if hasattr(run, "to_dict") else dict(run)

def serialize_terminology_alias(alias: Any) -> Dict[str, Any]:
    """Serializes TerminologyAliasRecord for HTTP response."""
    return alias.to_dict() if hasattr(alias, "to_dict") else dict(alias)

def serialize_execution_rate_benchmark(bench: Any) -> Dict[str, Any]:
    """Serializes ExecutionRateBenchmark for HTTP response."""
    return bench.to_dict() if hasattr(bench, "to_dict") else dict(bench)

def serialize_contractor_reporting_profile(prof: Any) -> Dict[str, Any]:
    """Serializes ContractorReportingProfile for HTTP response."""
    return prof.to_dict() if hasattr(prof, "to_dict") else dict(prof)

def serialize_conflict_resolution_pattern(pat: Any) -> Dict[str, Any]:
    """Serializes ConflictResolutionPattern for HTTP response."""
    return pat.to_dict() if hasattr(pat, "to_dict") else dict(pat)

