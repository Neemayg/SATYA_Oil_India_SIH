"""
SATYA Execution Event Pipeline Domain Models
Defines immutable/versioned data structures for sources, fragments, events, provenance, and quarantine.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime

# ---------------------------------------------------------
# ENUMERATED CONSTANTS
# ---------------------------------------------------------

class SourceType:
    JSON_SYNTHETIC = "JSON_SYNTHETIC"
    TEXT_DOCUMENT = "TEXT_DOCUMENT"
    DPR_EXCEL = "DPR_EXCEL"
    DPR_PDF = "DPR_PDF"
    SITE_DIARY = "SITE_DIARY"
    SUPERVISOR_NOTE = "SUPERVISOR_NOTE"
    VOICE_TRANSCRIPT = "VOICE_TRANSCRIPT"
    QA_REPORT = "QA_REPORT"
    UNKNOWN = "UNKNOWN"

class EventType:
    START = "START"
    PROGRESS = "PROGRESS"
    FINISH = "FINISH"
    STATUS_CHANGE = "STATUS_CHANGE"
    QUANTITY_UPDATE = "QUANTITY_UPDATE"
    INSPECTION = "INSPECTION"
    QA_CLEARANCE = "QA_CLEARANCE"
    HOLD = "HOLD"
    RESUME = "RESUME"
    UNKNOWN = "UNKNOWN"

class PipelineState:
    INGESTED = "INGESTED"
    NORMALIZED = "NORMALIZED"
    EXTRACTED = "EXTRACTED"
    VALIDATED = "VALIDATED"
    QUARANTINED = "QUARANTINED"

# ---------------------------------------------------------
# DOMAIN MODELS
# ---------------------------------------------------------

@dataclass
class SourceDocument:
    source_id: str
    project_id: str
    source_type: str
    file_name: str
    sha256_hash: str
    raw_content: str
    submitted_at: str
    received_at: str
    author: str = "Unknown"
    reporting_period: Optional[str] = None
    extraction_status: str = PipelineState.INGESTED
    metadata_json: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SourceFragment:
    fragment_id: str
    source_id: str
    fragment_index: int
    raw_text: str
    normalized_text: str
    locator_type: str  # e.g., "EXCEL_CELL", "PDF_LINE", "TEXT_SPAN", "TRANSCRIPT_TIMESTAMP"
    locator_value: str  # e.g., "Sheet1!R12", "Line 4", "Chars 120-180", "01:14"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ProvenanceRecord:
    provenance_id: str
    event_id: str
    source_id: str
    source_type: str
    locator_type: str
    locator_value: str
    raw_text_snippet: str
    field_provenance_map: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # e.g. {"quantity": {"start_char": 10, "end_char": 14, "snippet": "400m"}}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ExecutionEvent:
    event_id: str
    source_id: str
    fragment_id: str
    event_type: str  # EventType enum
    observed_timestamp: Optional[str]  # e.g., "2026-09-02" or None if unresolved
    source_timestamp: str  # Ingestion/Submission time
    extracted_statement: str
    raw_observed_activity_id: Optional[str] = None  # Preserves raw text string e.g. "PIP-9999" or "ACT-1010"
    observed_activity_id: Optional[str] = None  # Validated schedule Activity ID or None
    activity_id_validation_status: str = "NO_EXPLICIT_REFERENCE"  # VALID_SCHEDULE_ID, INVALID_EXPLICIT_REFERENCE, NO_EXPLICIT_REFERENCE
    temporal_resolution_status: str = "EXPLICIT_DATE"  # EXPLICIT_DATE, RESOLVED_RELATIVE_DATE, UNRESOLVED_RELATIVE_DATE, FALLBACK_SUBMISSION_DATE
    temporal_resolution_basis: Optional[str] = None
    discipline: str = "UNKNOWN"
    area_location: Optional[str] = None
    equipment_tag: Optional[str] = None
    line_number: Optional[str] = None
    observed_quantity: Optional[float] = None
    unit_of_measure: Optional[str] = None
    progress_percent: Optional[float] = None
    status_text: Optional[str] = None
    extraction_confidence: float = 0.0
    lifecycle_state: str = PipelineState.EXTRACTED
    
    # Real-World Inspired Fields (Phase 4.5)
    shift_context: Optional[str] = None  # e.g., "DAY_SHIFT", "NIGHT_SHIFT", "SHIFT_2" [OPTIONAL]
    pending_qa_clearance: bool = False  # e.g., NDT/TPIA clearance pending [SOURCE-SPECIFIC]
    remaining_quantity: Optional[float] = None  # e.g., "balance 150m pending" [OPTIONAL]
    work_front_tag: Optional[str] = None  # e.g., "Front B", "Well-Pad 14" [OPTIONAL]

    provenance: Optional[ProvenanceRecord] = None
    quarantine_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.provenance:
            d["provenance"] = self.provenance.to_dict()
        return d

@dataclass
class QuarantineRecord:
    quarantine_id: str
    source_id: str
    event_id: Optional[str]
    failure_stage: str
    quarantine_reasons: List[str]
    raw_payload: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PipelineRunResult:
    pipeline_run_id: str
    source_id: str
    events_extracted: List[ExecutionEvent]
    quarantine_records: List[QuarantineRecord]
    total_fragments_processed: int
    status: str
    execution_time_ms: float

# ---------------------------------------------------------
# ACTIVITY FINGERPRINT DOMAIN MODEL (PHASE 6)
# ---------------------------------------------------------

@dataclass
class ActivityFingerprint:
    fingerprint_id: str
    activity_id: str
    project_id: str
    activity_name: str
    normalized_name: str
    wbs_id: str
    wbs_code: str
    wbs_name_path: str  # e.g., "North Basin Expansion > Mainline Pipeline > Section 1"
    discipline: str
    area_location: Optional[str] = None
    equipment_tag: Optional[str] = None
    line_number: Optional[str] = None
    start_km: Optional[float] = None
    end_km: Optional[float] = None
    planned_start: Optional[str] = None
    planned_finish: Optional[str] = None
    baseline_duration_days: int = 0
    planned_quantity: Optional[float] = None
    unit_of_measure: Optional[str] = None
    is_critical: bool = False
    predecessors: List[str] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)

    # Semantic & Terminology Intelligence (Phase 6)
    action_verbs: List[str] = field(default_factory=list)
    entity_nouns: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    field_aliases: List[str] = field(default_factory=list)
    search_tokens: List[str] = field(default_factory=list)
    fingerprint_version: str = "v1.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ---------------------------------------------------------
# MATCHING ENGINE DOMAIN MODELS (PHASE 7)
# ---------------------------------------------------------

class MatchOutcome:
    MATCHED = "MATCHED"
    AMBIGUOUS = "AMBIGUOUS"
    UNMATCHED = "UNMATCHED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

@dataclass
class MatchFactorScores:
    exact_identifier_score: float = 0.0      # 1.0 if explicit Activity ID matches valid schedule fingerprint
    line_equipment_score: float = 0.0        # Line / Equipment tag match
    spatial_chainage_score: float = 0.0       # Area / location / start_km / end_km overlap
    wbs_structural_score: float = 0.0         # WBS path & level alignment
    discipline_score: float = 0.0             # Engineering discipline match
    terminology_action_score: float = 0.0     # Action verbs, entity nouns & synonyms match
    temporal_window_score: float = 0.0        # Event time falls within or near planned baseline start/finish window
    overall_confidence_score: float = 0.0     # Weighted aggregate score [0.0, 1.0]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CandidateMatch:
    activity_id: str
    activity_name: str
    project_id: str
    wbs_name_path: str
    scores: MatchFactorScores
    match_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["scores"] = self.scores.to_dict()
        return d

@dataclass
class MatchResult:
    match_id: str
    event_id: str
    source_id: str
    outcome: str  # MatchOutcome enum: MATCHED, AMBIGUOUS, UNMATCHED, INSUFFICIENT_EVIDENCE
    selected_activity_id: Optional[str] = None
    selected_activity_name: Optional[str] = None
    confidence_score: float = 0.0
    top_candidate: Optional[CandidateMatch] = None
    candidate_matches: List[CandidateMatch] = field(default_factory=list)
    missing_discriminators: List[str] = field(default_factory=list)
    reasoning_trace: List[str] = field(default_factory=list)
    evaluated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.top_candidate:
            d["top_candidate"] = self.top_candidate.to_dict()
        d["candidate_matches"] = [c.to_dict() for c in self.candidate_matches]
        return d

# ---------------------------------------------------------
# EVIDENCE, CONFIDENCE & CONFLICT DOMAIN MODELS (PHASE 8)
# ---------------------------------------------------------

class SourceReliabilityTier:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ClaimType:
    STATUS_CLAIM = "STATUS_CLAIM"
    QUANTITY_CLAIM = "QUANTITY_CLAIM"
    PROGRESS_CLAIM = "PROGRESS_CLAIM"
    QA_CLAIM = "QA_CLAIM"
    LOCATION_CLAIM = "LOCATION_CLAIM"
    TEMPORAL_CLAIM = "TEMPORAL_CLAIM"

class CorroborationStatus:
    UNCORROBORATED = "UNCORROBORATED"
    CORROBORATED_SAME_ORIGIN = "CORROBORATED_SAME_ORIGIN"
    CORROBORATED_INDEPENDENT = "CORROBORATED_INDEPENDENT"

class ConflictType:
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    STATUS_CONFLICT = "STATUS_CONFLICT"
    QUANTITY_CONFLICT = "QUANTITY_CONFLICT"
    QA_CONFLICT = "QA_CONFLICT"
    SCHEDULE_CONFLICT = "SCHEDULE_CONFLICT"  # Out-of-sequence execution
    LOCATION_CONFLICT = "LOCATION_CONFLICT"
    DUPLICATE_CONFLICT = "DUPLICATE_CONFLICT"
    DUPLICATE_EVIDENCE = "DUPLICATE_EVIDENCE"  # Benign duplicate evidence submission

class ConflictSeverity:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TrustStatus:
    TRUSTED = "TRUSTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNTRUSTED = "UNTRUSTED"

@dataclass
class Evidence:
    evidence_id: str
    event_id: str
    source_id: str
    fragment_id: str
    locator_type: str
    locator_value: str
    source_type: str
    origin_group_id: str  # Tracks original source lineage to prevent re-quoted duplication credit
    raw_text_snippet: str
    observed_timestamp: Optional[str] = None
    provenance_map: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class EvidenceClaim:
    claim_id: str
    evidence_id: str
    event_id: str
    claim_type: str  # ClaimType enum
    raw_statement: str
    claim_value: Any
    unit: Optional[str] = None
    normalized_value: Optional[float] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class EvidenceReliabilityAssessment:
    reliability_id: str
    evidence_id: str
    authority_score: float = 0.5            # Source authority score [0.0, 1.0]
    verification_status_score: float = 0.5   # Verified vs unverified observation
    provenance_completeness_score: float = 0.5  # Precise locator & span availability
    timestamp_quality_score: float = 0.5     # Explicit date vs relative/fallback timestamp
    consistency_score: float = 0.5           # Historical consistency with prior logs
    overall_reliability_score: float = 0.5   # Multi-factor weighted aggregate score [0.0, 1.0]
    reliability_tier: str = SourceReliabilityTier.MEDIUM
    reasoning_trace: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ConflictFlag:
    conflict_id: str
    conflict_type: str  # ConflictType enum
    severity: str        # ConflictSeverity enum
    involved_event_ids: List[str]
    involved_claim_ids: List[str]
    involved_evidence_ids: List[str]
    description: str
    snippet_comparison: Dict[str, str]
    version_index: int = 1
    resolution_status: str = "UNRESOLVED"  # UNRESOLVED, PLANNER_OVERRIDDEN, RESOLVED
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class EvidenceAssessment:
    assessment_id: str
    event_id: str
    evidence_ids: List[str]
    claim_ids: List[str]
    corroboration_status: str  # CorroborationStatus enum
    unique_origin_count: int
    evidence_support_score: float  # [0.0, 1.0]
    reliability_assessments: List[EvidenceReliabilityAssessment] = field(default_factory=list)
    evidence_gaps: List[str] = field(default_factory=list)
    reasoning_trace: List[str] = field(default_factory=list)
    evaluated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["reliability_assessments"] = [r.to_dict() for r in self.reliability_assessments]
        return d

@dataclass
class TrustAssessment:
    assessment_id: str
    event_id: str
    version_index: int  # Append-only versioning (v1, v2, etc.)
    match_confidence: float
    evidence_support: float
    trust_status: str  # TrustStatus enum: TRUSTED, REVIEW_REQUIRED, UNTRUSTED
    gating_trigger: str  # Explanation of which gating rule fired
    rationale_breakdown: Dict[str, Any]
    has_critical_conflict: bool = False
    has_evidence_gaps: bool = False
    evaluated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ---------------------------------------------------------
# HUMAN VALIDATION (HITL) WORKFLOW DOMAIN MODELS (PHASE 9)
# ---------------------------------------------------------

class ValidationDecisionType:
    VALIDATE = "VALIDATE"            # Concur with SATYA recommendation & match
    CHANGE_MATCH = "CHANGE_MATCH"    # Re-map event to a different baseline Activity ID
    REJECT = "REJECT"                # Reject reported execution claim
    REQUEST_EVIDENCE = "REQUEST_EVIDENCE"  # Request additional field locators / QA proof
    DEFER = "DEFER"                  # Hold in review queue for shift handoff / senior review

class OverrideReasonCategory:
    TERMINOLOGY_ALIAS = "TERMINOLOGY_ALIAS"
    SPATIAL_CHAINAGE_RECURRENCE = "SPATIAL_CHAINAGE_RECURRENCE"
    WBS_LEVEL_MISMATCH = "WBS_LEVEL_MISMATCH"
    INCORRECT_EXTRACTION = "INCORRECT_EXTRACTION"
    QA_OVERRIDE = "QA_OVERRIDE"
    SCOPE_EXCLUSION = "SCOPE_EXCLUSION"
    OTHER = "OTHER"

class QueuePriority:
    P1_CRITICAL = "P1_CRITICAL"  # Critical Conflict Flag (e.g. QA_CONFLICT)
    P2_HIGH = "P2_HIGH"          # High Conflict Flag / AMBIGUOUS Match Outcome
    P3_MEDIUM = "P3_MEDIUM"      # INSUFFICIENT_EVIDENCE Outcome / Mandatory Evidence Gap
    P4_LOW = "P4_LOW"            # Match confidence below threshold

@dataclass
class ValidationDecision:
    decision_id: str
    event_id: str
    planner_id: str
    decision_type: str  # ValidationDecisionType enum
    reviewed_trust_version: int  # Locks exact trust version presented for review
    reviewed_match_result_id: str  # Locks exact match result presented for review
    reviewed_evidence_assessment_id: str  # Locks exact evidence assessment presented
    selected_activity_id: Optional[str] = None  # Selected Activity ID for VALIDATE or CHANGE_MATCH
    previous_trust_version: int = 1
    resulting_trust_version: int = 2
    resulting_trust_status: str = "TRUSTED"  # TrustStatus enum
    override_reason_category: Optional[str] = None  # OverrideReasonCategory enum
    reason_notes: str = ""
    evidence_reviewed_ids: List[str] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PlannerCorrectionRecord:
    correction_id: str
    event_id: str
    original_activity_id: Optional[str]
    corrected_activity_id: str
    original_match_result_id: str
    validation_decision_id: str
    reason_category: str
    reason_notes: str
    planner_id: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PlannerQueueItem:
    queue_item_id: str
    event_id: str
    project_id: str
    priority: str  # QueuePriority enum
    trigger_reason: str
    match_confidence: float
    evidence_support: float
    latest_trust_version: int
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ---------------------------------------------------------
# PHASE 10: ACTUAL PROGRESS & SCHEDULE PROJECTION MODELS
# ---------------------------------------------------------

class ProgressCalculationPolicy:
    QUANTITY_BASED = "QUANTITY_BASED"
    MILESTONE_BASED = "MILESTONE_BASED"
    STATUS_BASED = "STATUS_BASED"

class QuantityObservationType:
    DAILY_DELTA = "DAILY_DELTA"
    CUMULATIVE_TOTAL = "CUMULATIVE_TOTAL"
    UNKNOWN = "UNKNOWN"

class ProgressCalculationStatus:
    CALCULATED = "CALCULATED"
    PARTIAL_EVIDENCE = "PARTIAL_EVIDENCE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    CONFLICTED = "CONFLICTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class ForecastStatus:
    AVAILABLE = "AVAILABLE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    ZERO_RATE = "ZERO_RATE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class ProgressWeightPolicy:
    DURATION_WEIGHT = "DURATION_WEIGHT"
    QUANTITY_WEIGHT = "QUANTITY_WEIGHT"
    MANUAL_WEIGHT = "MANUAL_WEIGHT"

class ActivityProgressStatus:
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class QAClearanceStatus:
    CLEARED = "CLEARED"
    PENDING = "PENDING"
    NOT_REQUIRED = "NOT_REQUIRED"

@dataclass
class ActivityProgress:
    activity_id: str
    status: str  # ActivityProgressStatus
    calculation_policy: str  # ProgressCalculationPolicy
    calculation_status: str  # ProgressCalculationStatus
    forecast_status: str  # ForecastStatus
    actual_start: Optional[str] = None
    actual_finish: Optional[str] = None
    actual_quantity: Optional[float] = None
    planned_quantity: Optional[float] = None
    unit: Optional[str] = None
    physical_progress_pct: Optional[float] = None
    qa_clearance_status: str = QAClearanceStatus.NOT_REQUIRED
    actual_duration_days: Optional[float] = None
    remaining_duration_days: Optional[float] = None
    execution_rate_per_day: Optional[float] = None
    forecast_finish: Optional[str] = None
    start_variance_days: Optional[float] = None
    finish_variance_days: Optional[float] = None
    is_critical: bool = False
    critical_activity_projected_delay: bool = False
    trusted_event_count: int = 0
    unverified_event_count: int = 0
    unverified_reported_quantity: Optional[float] = None
    last_calculated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class WBSProgress:
    wbs_id: str
    wbs_code: str
    wbs_name: str
    level: int
    weight_policy: str  # ProgressWeightPolicy
    physical_progress_pct: Optional[float] = None
    weighted_progress_pct: Optional[float] = None
    activities_count: int = 0
    completed_count: int = 0
    in_progress_count: int = 0
    not_started_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ScheduleProjection:
    projection_id: str
    project_id: str
    as_of_date: str
    total_activities: int = 0
    completed_activities: int = 0
    in_progress_activities: int = 0
    not_started_activities: int = 0
    overall_project_progress_pct: Optional[float] = None
    critical_activity_delay_count: int = 0
    max_schedule_delay_days: float = 0.0
    unverified_claims_count: int = 0
    activity_progress_map: Dict[str, Any] = field(default_factory=dict)
    wbs_progress_map: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ---------------------------------------------------------
# TIME AGENT PROACTIVE MONITORING DOMAIN MODELS (PHASE 13)
# ---------------------------------------------------------

class TemporalSignalType:
    SILENT_CRITICAL_PATH_RISK = "SILENT_CRITICAL_PATH_RISK"
    REPORTING_LATENCY_STALENESS = "REPORTING_LATENCY_STALENESS"
    FORECAST_FINISH_SLIPPAGE = "FORECAST_FINISH_SLIPPAGE"
    UNVERIFIED_CLAIM_TEMPORAL_DRIFT = "UNVERIFIED_CLAIM_TEMPORAL_DRIFT"
    OUT_OF_SEQUENCE_EXECUTION_WARNING = "OUT_OF_SEQUENCE_EXECUTION_WARNING"
    QA_CLEARANCE_BOTTLENECK = "QA_CLEARANCE_BOTTLENECK"

class SignalSeverity:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class SignalStatus:
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    SUPERSEDED = "SUPERSEDED"
    ACKNOWLEDGED = "ACKNOWLEDGED"

@dataclass
class TemporalMonitoringPolicy:
    policy_version: str = "v1.0"
    reporting_staleness_days: int = 7
    forecast_slippage_low_days: int = 1
    forecast_slippage_medium_days: int = 3
    forecast_slippage_high_days: int = 6
    forecast_slippage_critical_days: int = 10
    unverified_claim_count_threshold: int = 3
    unverified_claim_age_days: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class MonitoringEvaluationRun:
    evaluation_run_id: str
    project_id: str
    as_of_date: str
    policy_version: str = "v1.0"
    evaluated_at: str = ""
    total_signals_detected: int = 0
    active_signal_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TemporalWarningSignal:
    signal_id: str
    signal_key: str  # {project_id}|{activity_id}|{signal_type}
    evaluation_run_id: str
    project_id: str
    activity_id: str
    signal_type: str  # TemporalSignalType enum
    severity: str     # SignalSeverity enum
    status: str       # SignalStatus enum
    as_of_date: str
    summary: str
    reasoning_trace: List[str] = field(default_factory=list)
    recommended_action: str = ""
    involved_event_ids: List[str] = field(default_factory=list)
    involved_evidence_ids: List[str] = field(default_factory=list)
    first_detected_at: str = ""
    last_detected_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------
# ANALYTICS & INSTITUTIONAL MEMORY DOMAIN MODELS (PHASE 14)
# ---------------------------------------------------------

class AliasStatus:
    CANDIDATE = "CANDIDATE"      # Single observation; ineligible for candidate retrieval
    VALIDATED = "VALIDATED"      # Multi-planner confirmation; provisional candidate scoring
    ACTIVE = "ACTIVE"            # Active signal in candidate retrieval scoring
    SUPERSEDED = "SUPERSEDED"    # Replaced by newer version or demoted due to re-overrides

class BenchmarkStatus:
    INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"  # Sample size below minimum provisional threshold
    PROVISIONAL = "PROVISIONAL"                  # Low sample size (e.g. 3-9 samples)
    VALIDATED = "VALIDATED"                      # Statistically eligible for P50/P90 analytics (>=10 samples)

@dataclass
class InstitutionalMemoryPolicy:
    policy_version: str = "v1.0"
    w_plan: float = 0.3              # Weight per distinct human planner confirmation
    w_src: float = 0.2               # Weight per independent source document origin
    w_over: float = 0.4              # Penalty weight per subsequent re-override
    recency_half_life_days: float = 90.0  # Recency decay half-life
    min_candidate_confirmations: int = 2
    min_provisional_sample: int = 3
    min_validated_sample: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class MemoryDistillationRun:
    distillation_run_id: str
    project_id: str
    as_of_date: str
    policy_version: str = "v1.0"
    input_corrections_count: int = 0
    candidates_created_count: int = 0
    promoted_aliases_count: int = 0
    superseded_aliases_count: int = 0
    executed_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TerminologyAliasRecord:
    alias_id: str
    project_id: str
    version: int
    alias_phrase: str
    target_activity_id: str
    status: str                         # AliasStatus enum
    confidence_weight: float            # Clamped [0.0, 1.0]
    confirmation_count: int = 1
    distinct_planner_count: int = 1
    distinct_source_count: int = 1
    reoverride_count: int = 0
    supersedes_alias_id: Optional[str] = None
    last_validated_at: str = ""
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ExecutionRateBenchmark:
    benchmark_id: str
    project_id: str
    wbs_id: str
    activity_type: str
    unit_of_measure: str
    quantity_basis: str                 # CUMULATIVE_TOTAL, DAILY_DELTA, etc.
    planned_rate: Optional[float]       # Planned quantity / Planned duration (None if missing)
    mean_actual_rate: float
    p50_rate: float
    p90_rate: float
    sample_count: int
    benchmark_status: str               # BenchmarkStatus enum
    last_calculated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ContractorReportingProfile:
    profile_id: str
    project_id: str
    contractor_id: Optional[str]        # Nullable if unknown in source
    total_events: int
    trusted_events: int
    untrusted_events: int
    verification_ratio: float           # Trusted / Total
    avg_reporting_delay_days: Optional[float] # Reported_at - Observed_at (None if missing)
    last_updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ConflictResolutionPattern:
    pattern_id: str
    project_id: str
    conflict_or_signal_type: str        # QA_CONFLICT, SILENT_CRITICAL_PATH_RISK, etc.
    total_occurrences: int
    validated_count: int
    remapped_count: int
    rejected_count: int
    acknowledged_count: int             # Time Agent acknowledgments (separated from resolved)
    resolved_count: int                 # Physical condition resolutions
    avg_resolution_hours: float
    last_updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)





