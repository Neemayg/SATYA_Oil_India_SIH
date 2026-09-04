# Execution Event Pipeline Core Engine Specification

> **Document Type:** Core Engine Implementation Specification  
> **Governance Status:** Phase 5 Implementation Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Engine Overview & Architecture

The **Execution Event Pipeline Engine** is the core vertical slice implemented in Phase 5. It transforms raw, heterogeneous field observation inputs into normalized, provenance-preserving `ExecutionEvent` records stored in an append-only SQLite database ledger.

```
[RAW SOURCE PAYLOAD]
         │
         ▼
[1. SOURCE INGESTION & SHA-256 HASHING] ──> (Idempotency Check)
         │
         ▼
[2. CONTENT NORMALIZATION & FRAGMENTATION] ──> (Provenance Locators)
         │
         ▼
[3. HYBRID EVENT EXTRACTION] ──> (Entities, Quantities, Shift Context)
         │
         ▼
[4. VALIDATION & CLOSED-VOCABULARY GUARDRAIL] ──> (Rule 5 Enforcement)
         │
         ├── (Pass) ──> [5. APPEND-ONLY EVENT LEDGER]
         └── (Fail) ──> [QUARANTINE REPOSITORY]
```

---

## 2. Implemented Components

* [`backend/models/domain_models.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/models/domain_models.py): Defines `SourceDocument`, `SourceFragment`, `ExecutionEvent`, `ProvenanceRecord`, `QuarantineRecord`, and `PipelineRunResult`.
* [`backend/ingestion/source_ingestion.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/ingestion/source_ingestion.py): Source loading, file hashing, raw archiving, and duplicate detection.
* [`backend/normalization/content_normalization.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/normalization/content_normalization.py): Whitespace normalization, fragment segmentation, and machine-resolvable provenance pointers.
* [`backend/extraction/event_extractor.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/extraction/event_extractor.py): Regex entity extraction, action verb taxonomy, discipline inference, and Phase 4.5 real-world fields (`shift_context`, `pending_qa_clearance`, `remaining_quantity`, `work_front_tag`).
* [`backend/validation/event_validator.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/validation/event_validator.py): Closed-Vocabulary Activity ID Guardrail (Rule 5) and quarantine manager.
* [`backend/persistence/database_engine.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/persistence/database_engine.py): SQLite database engine providing transaction safety and append-only ledger storage.
* [`backend/services/pipeline_service.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/services/pipeline_service.py): Pipeline orchestrator and structured logging.

---

## 3. Data Integrity & Safety Guardrails Enforced

1. **Raw Content Preservation:** Raw source files are archived immutably; original content is never overwritten or mutated.
2. **Rule 5 (No Hallucinated Activity IDs):** If raw text contains an Activity ID, it is validated against baseline vocabulary. If invalid or absent, `observed_activity_id` is set to `None`. No Activity IDs are ever fabricated.
3. **Idempotency Safeguard:** Exact duplicate content (matching SHA-256 hash) returns the existing source record without re-extracting duplicate events.
4. **Validation Isolation:** Extraction validation (`VALIDATED`) is explicitly separated from human execution validation.

---

## 4. Phase 5.1 Hardening & Technical Refinements

1. **One-to-Many Event Decomposition:** `extract_events_from_fragment` splits compound source statements containing multiple distinct actions or status indicators (joined by semicolons, conjunctions, or sentence breaks) into multiple discrete `ExecutionEvent` records.
2. **Raw Activity ID Preservation:** Invalid explicit Activity references (e.g., contractor aliases or typos like `PIP-9999`) are preserved in `raw_observed_activity_id` while `observed_activity_id` is set to `None` with `activity_id_validation_status = "INVALID_EXPLICIT_REFERENCE"`. Field observations are never destroyed.
3. **Field-Level Provenance Spans:** `ProvenanceRecord.field_provenance_map` tracks exact character start/end spans (`start_char`, `end_char`, `snippet`) for `event_type`, `raw_observed_activity_id`, `observed_quantity`, `discipline`, and `area_location`.
4. **Temporal Uncertainty & Resolution Status:** Relative date resolution returns `temporal_resolution_status` (`RESOLVED_RELATIVE_DATE`, `UNRESOLVED_RELATIVE_DATE`, `EXPLICIT_DATE`, `FALLBACK_SUBMISSION_DATE`). Unresolvable relative dates set `observed_timestamp = None` rather than fabricating timestamps.
5. **Strict Append-Only Immutability:** `DatabaseEngine` contains zero SQL `UPDATE execution_events` statements.
6. **Zero-Dependency Native XLSX Adapter:** `backend/ingestion/xlsx_adapter.py` provides native XML/zip parsing of `.xlsx` files without third-party pip dependencies.
