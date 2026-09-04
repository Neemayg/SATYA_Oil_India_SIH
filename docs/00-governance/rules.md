# System Engineering & Architecture Rules

> **Governance Standard:** Non-Negotiable System Rules  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Enforcement:** Mandatory for all human developers and AI coding agents.  

---

## Non-Negotiable Rules

### RULE 1: AI is Not the Source of Truth
AI models (LLMs, neural networks, heuristics) are analytical and probabilistic tools. They do not constitute authoritative operational reality. The source of truth remains verifiable physical evidence, raw field observations, and human planner validation.

### RULE 2: Raw Inputs Must Never Be Destroyed
The original field input (raw text, DPR document bytes, audio stream, site photo) must never be destroyed, overwritten, or silently modified. All extraction and normalization pipelines must operate read-only on raw inputs and emit new append-only artifacts.

### RULE 3: Strict Provenance Preservation
Every extracted `ExecutionEvent` must retain immutable provenance metadata pointing directly to its origin, including source identifier, file path/URI, character/block offset, ingestion timestamp, and author metadata.

### RULE 4: Explicit Confidence Scoring Mandatory
Every schedule match produced by automated algorithms or AI must have an explicit, normalized confidence score in the range $[0.0, 1.0]$, accompanied by a factor breakdown (semantic, structural, temporal).

### RULE 5: No Hallucinated Schedule Activity IDs
Language models and heuristics must NEVER invent, fabricate, or hallucinate a schedule `Activity ID` or `WBS ID`. Matching outputs must strictly reference verified Activity IDs present in the ingested baseline schedule manifest.

### RULE 6: Matching Engine Must Support UNMATCHED Status
The matching engine must explicitly support and output an `UNMATCHED` status whenever field evidence cannot be linked to a schedule activity with sufficient confidence or clarity.

### RULE 7: Low-Confidence Matches Require Human Review
Any automated match falling below the defined system confidence threshold ($\text{Confidence} < \theta_{\text{review}}$) must be flagged and routed to the Human-in-the-Loop (HITL) planner verification queue before affecting actual schedule progress.

### RULE 8: Contradictory Observations Must Be Preserved
When two or more field observations report contradictory status for the same execution window or activity, both observations must be preserved, recorded in the ledger, and explicitly surfaced as a `ConflictFlag`.

### RULE 9: "Not Reported" $\neq$ "Not Started" or "Delayed"
The absence of field reports for an activity during a given period ("not reported") must never automatically be interpreted as "not started", "halted", or "delayed". It must be classified specifically as an `EvidenceGap`.

### RULE 10: Granularity Mismatch Handling
Field-level execution is frequently more granular than baseline schedule activities. The matching engine must support mapping multiple micro-level field events to a higher-level L5/L6 schedule activity without forcing schedule fragmentation.

### RULE 11: Human Corrections Are Primary Intelligence
Planner overrides, re-mappings, and corrections made during HITL validation are valuable training and operational data. They must be permanently stored in Institutional Memory and never discarded.

### RULE 12: Every Important AI Decision Must Be Explainable
Any AI-driven matching decision, confidence calculation, or conflict detection must provide a structured, human-legible explanation trace detailing why the decision was made.

### RULE 13: No Direct Automatic Baseline Schedule Mutation
The system must never directly modify, overwrite, or re-baseline the baseline Primavera/MS Project schedule without an explicit, audit-tracked validation and projection workflow.

### RULE 14: No Technology Inclusion Without Purpose
Do not introduce frameworks, vector databases, microservices, or complex libraries simply to appear innovative. Every component must be directly justified by functional requirements.

### RULE 15: Prefer Simple, Testable Solutions
Always prefer straightforward, deterministic, and modular code over multi-layered abstractions or complex prompt chains that are difficult to unit-test and debug.

### RULE 16: Prototype vs. Production Integrity
No production-grade claim may be made in documentation, UI, or presentations for functionality that only exists as a mock, synthetic generator, or prototype.

### RULE 17: Synthetic Data Transparency
Do not claim synthetic or mock data is real Oil India proprietary data. All test datasets, synthetic DPRs, and mock schedules must be explicitly labeled as `SYNTHETIC` or `SAMPLE`.

### RULE 18: Definition of Done Required
Every implementation phase must satisfy its documented Definition of Done and exit criteria before development moves to subsequent phases.

### RULE 19: Documentation and Implementation Synchronization
Documentation (`docs/`) and implementation must remain synchronized at all times. Code commits that alter functionality or schema without updating documentation are strictly invalid.

### RULE 20: Strict Scope Boundary Control
Do not implement features, utility functions, or abstractions outside the explicitly approved Minimum Viable Product (MVP) scope defined for the active phase.
