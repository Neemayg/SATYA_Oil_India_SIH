# Conceptual Normalized Execution Event Model

> **Document Type:** Execution Event Conceptual Specification  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Executive Summary

An **Execution Event** is the fundamental atomic unit of physical execution intelligence in SATYA. It represents a structured, normalized claim derived from a raw field observation.

Unlike traditional project management systems that immediately mutate schedule database rows, SATYA captures execution events as append-only records in the **Execution Event Ledger**.

---

## 2. Normalized Conceptual Execution Event Model

```
+-----------------------------------------------------------------------------------+
|                            EXECUTION EVENT CONCEPT                                |
+-----------------------------------------------------------------------------------+
|  1. Event Header          : Event ID, Ingestion Timestamp, Validation State        |
|  2. Provenance Reference  : Source File, Offset, Document Type, Author Metadata   |
|  3. Action Payload        : Work Action, Observed Quantity, Unit, Text Snippet    |
|  4. Contextual Extracted  : Location/Chainage, Discipline, Observed Timestamp     |
|  5. Candidate Match Links : Target Activity ID(s), Confidence Score, Factor Math  |
|  6. Evidence & Conflicts  : Evidence References, Conflict Flags, Reasoning Trace  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Attribute Conceptual Breakdown

### 3.1 Event Header & Provenance
* `event_id`: Unique immutable event identifier. `[CONFIRMED]`
* `source_id`: Pointer to raw ingested file/artifact in raw storage. `[CONFIRMED]`
* `source_type`: Category of source document (`DPR_EXCEL`, `DPR_PDF`, `VOICE_MEMO`, `SITE_PHOTO`, `INSPECTION_CERTIFICATE`). `[CONFIRMED]`
* `source_timestamp`: Timestamp when the original document was created or reported in the field. `[CONFIRMED]`
* `ingested_timestamp`: Timestamp when SATYA ingested the document. `[CONFIRMED]`
* `provenance`: Detailed locator metadata (`file_path`, `sheet_name`, `row_or_line_number`, `byte_offset`, `raw_text_snippet`). `[CONFIRMED]`

### 3.2 Action & Entity Payload
* `work_action`: Extracted physical action verb (`TRENCHED`, `WELDED`, `INSTALLED`, `TESTED`, `CLEARED`, `INSPECTED`). `[CONFIRMED]`
* `observed_quantity`: Scalar quantity value observed (e.g., `150.0`). `[CONFIRMED]`
* `unit_of_measure`: Standardized unit string (`Meters`, `Joints`, `MT`, `Percent`). `[CONFIRMED]`
* `raw_entity_text`: Exact verbatim text block extracted from source. `[CONFIRMED]`
* `discipline`: Inferred or declared discipline (`CIVIL`, `MECHANICAL`, `PIPING`, `ELECTRICAL`, `INSTRUMENTATION`). `[CONFIRMED]`
* `location`: Geographical location tag, well-pad identifier, or chainage segment (`Km 14.200 - 14.350`). `[REASONABLE DOMAIN ASSUMPTION]`

### 3.3 Candidate Match & Confidence
* `candidate_activity_ids`: Array of candidate baseline schedule `Activity ID`s ranked by match score. `[CONFIRMED]`
* `confidence_score`: Normalized certainty metric $[0.0, 1.0]$. `[CONFIRMED]`
* `score_breakdown`: Component score breakdown (`semantic_score`, `structural_score`, `temporal_score`). `[CONFIRMED]`
* `match_reasoning`: Human-legible explanation trace explaining why the linkage was formed. `[CONFIRMED]`

### 3.4 Evidence & Validation State
* `evidence_references`: Array of linked corroborating artifacts (e.g., geotagged photo ID, TPIA NDT report ID). `[CONFIRMED]`
* `validation_state`: Current operational status (`OBSERVED`, `EXTRACTED`, `MATCHED`, `VALIDATED`, `PROJECTED_TO_SCHEDULE`). `[CONFIRMED]`
* `conflicts`: Array of detected conflict flags (`ContradictoryQuantity`, `Out-of-Sequence`, `QA_Failed`). `[CONFIRMED]`

---

## 4. Event Types Taxonomy

In oil and gas construction, Execution Events fall into 4 core event types:

1. **`PROGRESS_INCREMENT`**: Reports progress volume achieved during a period (e.g., "Laid 200m pipe").
2. **`MILESTONE_STATUS`**: Reports discrete actual start or actual finish events (e.g., "Hydrotest completed on 2026-09-04").
3. **`INSPECTION_RECORD`**: QA/QC inspection result certifying or rejecting executed work.
4. **`BOTTLENECK_STPAGE`**: Operational stoppage event explaining delay (e.g., "Work stopped due to heavy rain / ROW unacquired").
