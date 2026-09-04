# Architectural Decision Records (ADR)

> **Document Type:** Architectural Decision Log  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Status:** Canonical Record  

---

## Decision Index

| ID | Title | Date | Status |
| :--- | :--- | :--- | :--- |
| [DEC-001](#dec-001-execution-truth-layer-as-central-product-architecture) | Execution Truth Layer as Central Product Architecture | 2026-09-04 | APPROVED |
| [DEC-002](#dec-002-execution-events-treated-as-immutable-observations) | Execution Events Treated as Immutable Observations | 2026-09-04 | APPROVED |
| [DEC-003](#dec-003-ai-cannot-invent-schedule-activities) | AI Cannot Invent Schedule Activities | 2026-09-04 | APPROVED |
| [DEC-004](#dec-004-human-validation-gate-for-uncertain-ai-interpretation) | Human Validation Gate for Uncertain AI Interpretation | 2026-09-04 | APPROVED |
| [DEC-005](#dec-005-matching-engine-baseline-calibration-and-known-limitation-framing) | Matching Engine Baseline Calibration & Known Limitation Framing | 2026-09-04 | APPROVED |
| [DEC-006](#dec-006-evidence-confidence--conflict-engine-architecture-phase-8) | Evidence, Confidence & Conflict Engine Architecture (Phase 8) | 2026-09-04 | APPROVED & CLOSED |
| [DEC-007](#dec-007-human-validation-hitl-workflow-architecture-phase-9) | Human Validation (HITL) Workflow Architecture (Phase 9) | 2026-09-04 | APPROVED |

---

### DEC-001: Execution Truth Layer as Central Product Architecture

* **ID:** DEC-001
* **Date:** 2026-09-04
* **Decision:** Establish an Execution Truth Layer (ETL) as the core system architecture between raw field inputs and schedule actuals.
* **Context:** Upstream oil and gas projects suffer from a disconnect between field execution reality (unstructured DPRs, site notes) and Primavera P6 L5/L6 project schedules. Standard project tools try to force field engineers to enter Primavera activity IDs directly, leading to low adoption, or rely on unverified manual spreadsheet summaries.
* **Options Considered:**
  1. *Direct User Data Entry into PMIS:* Require field staff to manually tag Primavera Activity IDs in site logs. (Rejected: Unrealistic for remote field contractors).
  2. *Generic Conversational AI Chatbot:* Build a query-answering bot on top of DPR documents. (Rejected: Provides summaries but fails to produce structured, audit-ready schedule actuals).
  3. *Execution Truth Layer Architecture:* Build an automated intelligence layer that ingests raw field inputs, extracts structured Execution Events, matches them against Activity Fingerprints, and verifies evidence before updating progress. (Chosen).
* **Decision Made:** Option 3 — Build the Execution Truth Layer.
* **Reason:** Guarantees schedule grounding, preserves raw evidence provenance, and bridges the operational gap between field reality and formal scheduling.
* **Consequences:** The system must implement dedicated event extraction, fingerprinting, matching, and conflict verification pipelines.
* **Status:** APPROVED

---

### DEC-002: Execution Events Treated as Immutable Observations

* **ID:** DEC-002
* **Date:** 2026-09-04
* **Decision:** Treat all extracted execution events and raw field inputs as immutable, append-only records.
* **Context:** Progress reports in construction projects are frequently disputed during audit or contract billing. Modifying or overwriting past progress entries destroys the audit trail.
* **Options Considered:**
  1. *Mutable State Database:* Update field progress rows in-place when new reports arrive. (Rejected: Destroys historical auditability and provenance).
  2. *Immutable Observation Ledger:* Store every field report as an immutable `ExecutionEvent` with full provenance, treating progress calculation as a deterministic projection over the ledger. (Chosen).
* **Decision Made:** Option 2 — Immutable Event Ledger.
* **Reason:** Ensures 100% auditability, supports retrospective analysis, and enables re-running matching models as institutional memory improves.
* **Consequences:** Database storage must be designed for append-only events. Corrections are logged as new compensating events or planner overrides rather than in-place edits.
* **Status:** APPROVED

---

### DEC-003: AI Cannot Invent Schedule Activities

* **ID:** DEC-003
* **Date:** 2026-09-04
* **Decision:** Enforce a strict constraint preventing AI models from inventing or generating schedule Activity IDs or WBS IDs.
* **Context:** Large Language Models are prone to hallucination when generating structured identifiers, which can corrupt the PMIS schedule baseline.
* **Options Considered:**
  1. *Unconstrained LLM Generation:* Allow LLM to output freeform activity IDs based on prompt context. (Rejected: High risk of hallucinated IDs).
  2. *Strict Closed-Vocabulary Constrained Matching:* Force matching outputs to strictly map to valid candidate Activity IDs provided from the ingested baseline manifest, or return `UNMATCHED`. (Chosen).
* **Decision Made:** Option 2 — Strict constrained matching with `UNMATCHED` support.
* **Reason:** Ensures data integrity and prevents corrupt schedule updates.
* **Consequences:** Matching algorithms must validate generated candidate IDs against the ingested baseline dictionary before accepting any match result.
* **Status:** APPROVED

---

### DEC-004: Human Validation Gate for Uncertain AI Interpretation

* **ID:** DEC-004
* **Date:** 2026-09-04
* **Decision:** Position Human-in-the-Loop (HITL) planner validation between uncertain AI matching interpretations and trusted actual schedule updates.
* **Context:** Fully automated schedule updates based on probabilistic matching can introduce false progress entries, leading to incorrect critical path calculations.
* **Options Considered:**
  1. *Fully Autonomous Schedule Auto-Update:* Automatically update Primavera schedules whenever a match is made. (Rejected: Dangerous for high-value projects).
  2. *Threshold-Gated Human Validation (HITL):* Automatically accept high-confidence matches ($\ge \theta_{\text{auto}}$), while routing low-confidence or conflicting matches to a planner review queue. (Chosen).
* **Decision Made:** Option 2 — Threshold-gated HITL validation.
* **Reason:** Balances automation efficiency with human planner accountability and risk control.
* **Consequences:** The application requires a dedicated Human Validation UI and queue workflow. Planner feedback is saved to Institutional Memory.
* **Status:** APPROVED

---

### DEC-005: Matching Engine Baseline Calibration & Known Limitation Framing

* **ID:** DEC-005
* **Date:** 2026-09-04
* **Decision:** Phase 7.1 is APPROVED as a calibration and failure audit phase. Automatic schedule matching quality remains a calibrated baseline with known limitations and must NOT be presented or documented as a solved problem.
* **Context:** Evaluation benchmark metrics show strong candidate retrieval (Recall@10 = 75%), but weak discriminative ranking (Top-1 Recall = 12.5%) and conservative automatic match coverage (0% matched at default threshold $\theta_{\text{match}}=0.75$). Presenting 0% false confident matches without stating 0% automatic match coverage is misleading.
* **Key Directives & Boundaries:**
  1. **Truthful Framing Policy:** 0% false confident matches must always be presented alongside 0% automatic match coverage on the evaluation split. SATYA prioritizes safety over blind automation: "Under current calibration, SATYA refuses to make unsafe matches."
  2. **Ground Truth Ambiguity Stance:** Ground truth observations lacking locators (e.g. chainage or equipment tags) represent under-specified evidence. SATYA refusing to guess among identical candidate activities is correct system behavior.
  3. **Synthetic Truncation Defect Note:** Literal truncation strings (`...`) in synthetic observations are dataset generation defects, not matching engine failures to hack around. Synthetic data remains frozen.
  4. **Product Language Standard:** Standardize product UI and reporting terminology to `Schedule Match Confidence: XX%` (with explicit positive compatibility factors and missing discriminators) instead of generic `AI Match: XX%`. If confidence is below threshold, display `NO TRUSTED MATCH` and `Missing discriminator: chainage`.
  5. **Clean Boundary for Phase 8:** Move forward to Phase 8 (Evidence + Confidence + Conflict Engine). Phase 8 must NOT attempt to secretly fix Phase 7 ranking weights or lower safety thresholds to manufacture matches.
* **Status:** APPROVED

---

### DEC-006: Evidence, Confidence & Conflict Engine Architecture (Phase 8)

* **ID:** DEC-006
* **Date:** 2026-09-04
* **Decision:** Phase 8 implements an explicit, multi-layered Evidence, Confidence & Conflict Engine with 19 non-negotiable architectural rules.
* **Context:** Determining whether a field execution report is trustworthy requires evaluating evidence quality, corroboration across independent sources, evidence completeness gaps, and internal contradictions—separately from baseline schedule matching.
* **Key Directives & Boundaries:**
  1. **Complete Execution Truth Chain:** $\text{REALITY} \neq \text{EXTRACTED} \neq \text{MATCHED} \neq \text{TRUSTED} \neq \text{SCHEDULE ACTUAL}$.
  2. **`EvidenceClaim` Entity:** Decomposes source fragments into atomic claims ($\text{SourceFragment} \rightarrow \text{Evidence} \rightarrow \text{EvidenceClaim} \rightarrow \text{ExecutionEvent}$).
  3. **Multi-Factor Reliability Assessment:** Evaluates authority, verification status, provenance completeness, timestamp quality, and consistency rather than relying solely on `SourceType`.
  4. **Source Independence Grouping:** Uses `origin_group_id` so re-quoted reports (e.g., contractor email quoting contractor DPR) do not receive fake independent corroboration credit.
  5. **Deterministic Gating Tree:** Replaces opaque weighted formulas with a strict decision tree where severe conflicts (e.g. `QA_STATUS = REJECTED`) immediately trigger `REVIEW_REQUIRED` or `UNTRUSTED`.
  6. **Initial Policy Defaults:** `DEFAULT_MATCH_THRESHOLD = 0.75` and `DEFAULT_EVIDENCE_THRESHOLD = 0.60` are explicitly documented as configurable initial policy defaults, not scientifically proven constants.
  7. **Trust Meaning:** `TRUSTED` means "trusted under SATYA's evidence policy", NOT "physically proven".
  8. **Activity/Discipline-Aware Evidence Policies:** `EvidenceRequirementPolicy` defines mandatory evidence by activity/discipline type (e.g. mandatory NDT for welding; optional for earthworks).
  9. **Reporting Delay & Out-of-Sequence Semantics:** Ignores submission latency when evaluating execution dates, and classifies predecessor timing mismatches as `SCHEDULE_CONFLICT / OUT_OF_SEQUENCE_EXECUTION`.
  10. **Duplicate Separation:** Distinguishes benign `DUPLICATE_EVIDENCE` from contradictory `DUPLICATE_CONFLICT`.
  11. **Append-Only Versioned Ledger:** SQLite persistence creates new version records (`TrustAssessment v1` $\rightarrow$ `TrustAssessment v2`) for historical auditability.
* **Status:** APPROVED & CLOSED

---

### DEC-007: Human Validation (HITL) Workflow Architecture (Phase 9)

* **ID:** DEC-007
* **Date:** 2026-09-04
* **Decision:** Phase 9 implements an auditable Human-in-the-Loop (HITL) validation workflow with 5 explicit decision types and strict non-mutation audit rules.
* **Context:** Machine interpretation ($S_{\text{match}}$ and $S_{\text{evidence}}$) identifies candidates and flags risks, but human project planners hold authoritative responsibility for validating execution events before schedule projection.
* **Key Directives & Boundaries:**
  1. **Complete Execution Truth Chain:** $\text{FIELD REALITY} \rightarrow \text{SOURCE EVIDENCE} \rightarrow \text{EVIDENCE CLAIM} \rightarrow \text{EXECUTION EVENT} \rightarrow \text{SCHEDULE MATCH} \rightarrow \text{EVIDENCE ASSESSMENT} \rightarrow \text{CONFLICT DETECTION} \rightarrow \text{TRUST DECISION (AI)} \rightarrow \text{VALIDATION DECISION (HUMAN)} \rightarrow \text{TRUSTED EXECUTION TRUTH}$.
  2. **Non-Mutation Rule:** Human decisions append new records (`ValidationDecision` and `TrustAssessment v(N+1)`). In-place updates (`UPDATE candidate_matches`, `UPDATE match_results`, `UPDATE execution_events`) are strictly prohibited.
  3. **Decision Types:** Enforces 5 explicit decision types (`VALIDATE`, `CHANGE_MATCH`, `REJECT`, `REQUEST_EVIDENCE`, `DEFER`).
  4. **Decision State Snapshot:** Every `ValidationDecision` locks `reviewed_trust_version`, `reviewed_match_result_id`, and `reviewed_evidence_assessment_id` to reference the exact presented machine state.
  5. **Deterministic Queue Precedence:** Ranks review queue items deterministically ($P1$ Critical Conflict > $P2$ High Conflict/Ambiguous > $P3$ Medium/Gap > $P4$ Low Confidence) with tie-breaking (`severity` $\rightarrow$ `age` $\rightarrow$ `confidence` $\rightarrow$ `event_id`).
  6. **Workflow Decisions (`DEFER` / `REQUEST_EVIDENCE`):** `DEFER` and `REQUEST_EVIDENCE` record workflow actions while maintaining `REVIEW_REQUIRED` state. They do NOT manufacture false negative trust conclusions.
  7. **Institutional Memory Hook:** Re-mapping decisions emit a derived `PlannerCorrectionRecord` for Phase 14 analysis without executing real-time retraining in Phase 9.
* **Status:** APPROVED


