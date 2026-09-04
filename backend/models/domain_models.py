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
    outcome: str  # MatchOutcome enum: MATCHED, AMBIGUOUS, UNMATCHED
    selected_activity_id: Optional[str] = None
    selected_activity_name: Optional[str] = None
    confidence_score: float = 0.0
    top_candidate: Optional[CandidateMatch] = None
    candidate_matches: List[CandidateMatch] = field(default_factory=list)
    reasoning_trace: List[str] = field(default_factory=list)
    evaluated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.top_candidate:
            d["top_candidate"] = self.top_candidate.to_dict()
        d["candidate_matches"] = [c.to_dict() for c in self.candidate_matches]
        return d
