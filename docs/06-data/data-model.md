# Conceptual Data Model & Entity Specifications

> **Document Type:** Conceptual Data Model Specification  
> **Governance Status:** Phase 3 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Entity-Relationship Overview

The SATYA data model spans 19 core conceptual entities organized into 4 logical domains:

```
[SCHEDULE DOMAIN]                  [SOURCE & EVENT DOMAIN]             [MATCHING & EVIDENCE DOMAIN]
- Project                          - SourceDocument                    - CandidateMatch
- Schedule                         - SourceFragment                    - Evidence
- WBSNode                          - ExecutionObservation              - ProvenanceRecord
- Activity                         - ExecutionEvent                    - ConfidenceAssessment
- ActivityRelationship                                                 - Conflict
- ActivityFingerprint                                                  - ValidationDecision

[PROJECTION & INTELLIGENCE DOMAIN]
- ScheduleProjection
- InstitutionalMemoryEntry
- AuditRecord
```

---

## 2. Conceptual Entity Catalog

### 1. `Project`
* **Purpose:** Represents an Oil India capital infrastructure project (e.g., Cross-Country Gas Pipeline Phase 2).
* **Key Attributes:** `project_id`, `project_name`, `asset_location`, `owner_department`, `created_at`.
* **Mutability:** `MUTABLE` | **Source of Truth:** System Administrator / PMO.

### 2. `Schedule`
* **Purpose:** Represents a specific imported baseline schedule version (e.g., Revision B Baseline).
* **Key Attributes:** `schedule_id`, `project_id`, `version_label`, `baseline_date`, `is_active_baseline`.
* **Mutability:** `READ-ONLY` | **Source of Truth:** Primavera P6 File Export.

### 3. `WBSNode`
* **Purpose:** Represents a node in the Work Breakdown Structure tree (L1 through L6).
* **Key Attributes:** `wbs_id`, `schedule_id`, `parent_wbs_id`, `wbs_code`, `wbs_name`, `level_number`.
* **Mutability:** `READ-ONLY` | **Source of Truth:** Primavera P6 File Export.

### 4. `Activity`
* **Purpose:** Represents a discrete L5/L6 baseline schedule activity container.
* **Key Attributes:** `activity_id`, `schedule_id`, `wbs_id`, `activity_name`, `discipline`, `planned_start`, `planned_finish`, `planned_quantity`, `unit_of_measure`.
* **Mutability:** `READ-ONLY` | **Source of Truth:** Primavera P6 File Export.

### 5. `ActivityRelationship`
* **Purpose:** Represents a CPM logical tie between two activities.
* **Key Attributes:** `relationship_id`, `predecessor_activity_id`, `successor_activity_id`, `tie_type` (`FS`, `SS`, `FF`, `SF`), `lag_duration`.
* **Mutability:** `READ-ONLY` | **Source of Truth:** Primavera P6 File Export.

### 6. `ActivityFingerprint`
* **Purpose:** Multi-vector context signature for matching.
* **Key Attributes:** `fingerprint_id`, `activity_id`, `semantic_embedding_vector`, `wbs_path_string`, `spatial_chainage_interval`, `temporal_window_bounds`.
* **Mutability:** `MUTABLE (RE-COMPUTABLE)` | **Source of Truth:** Fingerprint Engine.

### 7. `SourceDocument`
* **Purpose:** Immutable record of an ingested raw field observation document.
* **Key Attributes:** `source_id`, `project_id`, `source_type` (`EXCEL`, `PDF`, `TEXT`, `TRANSCRIPT`), `file_name`, `sha256_hash`, `submitted_at`, `submitted_by`.
* **Mutability:** `IMMUTABLE` | **Source of Truth:** Field Ingestion Layer.

### 8. `SourceFragment`
* **Purpose:** Normalized text block or row extracted from a source document.
* **Key Attributes:** `fragment_id`, `source_id`, `fragment_type`, `raw_text`, `provenance_locator`.
* **Mutability:** `IMMUTABLE` | **Source of Truth:** Content Normalizer.

### 9. `ExecutionObservation`
* **Purpose:** Raw empirical observation payload parsed from fragment.
* **Key Attributes:** `observation_id`, `fragment_id`, `raw_action_text`, `raw_quantity`, `raw_location`.
* **Mutability:** `IMMUTABLE` | **Source of Truth:** Parser Engine.

### 10. `ExecutionEvent`
* **Purpose:** Structured, normalized execution event extracted from observation.
* **Key Attributes:** `event_id`, `observation_id`, `work_action`, `observed_quantity`, `unit_of_measure`, `observed_timestamp`, `discipline`, `location_tag`, `state` (`EXTRACTED`, `MATCHED`, `VALIDATED`, `PROJECTED`).
* **Mutability:** `APPEND-ONLY (VERSIONED)` | **Source of Truth:** Event Extraction Pipeline.

### 11. `CandidateMatch`
* **Purpose:** Linkage candidate between event and activity fingerprint.
* **Key Attributes:** `match_id`, `event_id`, `candidate_activity_id`, `raw_confidence_score`, `match_status` (`MATCHED`, `AMBIGUOUS`, `UNMATCHED`, `CONFLICTED`).
* **Mutability:** `DERIVED` | **Source of Truth:** Schedule-Aware Match Engine.

### 12. `Evidence`
* **Purpose:** Verifying evidence artifact bound to an event.
* **Key Attributes:** `evidence_id`, `event_id`, `evidence_type` (`PHOTO`, `QA_CERTIFICATE`, `SURVEY_LOG`), `artifact_uri`, `sha256_hash`.
* **Mutability:** `IMMUTABLE` | **Source of Truth:** Field / Inspection Layer.

### 13. `ProvenanceRecord`
* **Purpose:** Machine-resolvable provenance pointer connecting event back to source origin.
* **Key Attributes:** `provenance_id`, `event_id`, `source_id`, `locator_type` (`EXCEL_CELL`, `PDF_REGION`, `TEXT_SPAN`, `TRANSCRIPT_TIMESTAMP`), `locator_metadata_json`.
* **Mutability:** `IMMUTABLE` | **Source of Truth:** Provenance Engine.

### 14. `ConfidenceAssessment`
* **Purpose:** Structured factor breakdown of matching confidence.
* **Key Attributes:** `assessment_id`, `match_id`, `overall_confidence`, `semantic_score`, `spatial_score`, `temporal_score`, `discipline_score`, `reasoning_trace_json`.
* **Mutability:** `DERIVED` | **Source of Truth:** Confidence Engine.

### 15. `Conflict`
* **Purpose:** First-class object representing contradictory field claims or QA failures.
* **Key Attributes:** `conflict_id`, `event_id_a`, `event_id_b`, `conflict_type` (`QA_CONTRADICTION`, `QUANTITY_DISCREPANCY`), `status` (`UNRESOLVED`, `RESOLVED`, `SUPERSEDED`).
* **Mutability:** `MUTABLE` | **Source of Truth:** Conflict Engine.

### 16. `ValidationDecision`
* **Purpose:** Record of human planner verification decision in HITL queue.
* **Key Attributes:** `decision_id`, `event_id`, `selected_activity_id`, `planner_id`, `decision_type` (`APPROVED`, `RE_MAPPED`, `REJECTED`), `reason_code`, `timestamp`.
* **Mutability:** `APPEND-ONLY` | **Source of Truth:** Human Validation Layer.

### 17. `ScheduleProjection`
* **Purpose:** Derived candidate update to Primavera schedule actuals.
* **Key Attributes:** `projection_id`, `activity_id`, `proposed_actual_start`, `proposed_actual_finish`, `proposed_physical_percent_complete`, `evidence_index_json`.
* **Mutability:** `DERIVED VIEW` | **Source of Truth:** Projection Engine.

### 18. `InstitutionalMemoryEntry`
* **Purpose:** Historical alias or productivity metric learned from validated history.
* **Key Attributes:** `entry_id`, `entry_type` (`TERMINOLOGY_ALIAS`, `PRODUCTIVITY_RATE`), `jargon_term`, `formal_activity_name`, `frequency_count`.
* **Mutability:** `MUTABLE (INCREMENTAL)` | **Source of Truth:** Institutional Memory Layer.

### 19. `AuditRecord`
* **Purpose:** Immutable audit log of system operations.
* **Key Attributes:** `audit_id`, `timestamp`, `user_id`, `action_type`, `target_entity_id`, `audit_payload_json`.
* **Mutability:** `IMMUTABLE` | **Source of Truth:** Audit Layer.
