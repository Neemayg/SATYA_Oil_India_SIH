# Human Validation (HITL) Workflow Core Specification

> **Document Type:** Core Engine Implementation & Architecture Specification  
> **Governance Status:** Phase 9 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Workflow Overview & Core Principles

The **Human Validation (HITL) Workflow Engine** (Phase 9) provides the backend queue management, review workspace contracts, and auditable validation decision handlers for human project planners.

It preserves the non-negotiable state separation chain:
$$\text{FIELD REALITY} \rightarrow \text{SOURCE EVIDENCE} \rightarrow \text{EVIDENCE CLAIM} \rightarrow \text{EXECUTION EVENT} \rightarrow \text{SCHEDULE MATCH} \rightarrow \text{EVIDENCE ASSESSMENT} \rightarrow \text{CONFLICT DETECTION} \rightarrow \text{TRUST DECISION (AI)} \rightarrow \mathbf{\text{VALIDATION DECISION (HUMAN)}} \rightarrow \mathbf{\text{TRUSTED EXECUTION TRUTH}}$$

```
                       ┌─────────────────────────┐
                       │   Planner Review Queue  │
                       └────────────┬────────────┘
                                    │
                             Planner Review
                                    │
     ┌──────────────┬───────────────┼───────────────┬──────────────┐
     ▼              ▼               ▼               ▼              ▼
 [VALIDATE]   [CHANGE_MATCH]    [REJECT]   [REQUEST_EVIDENCE]  [DEFER]
     │              │               │               │              │
     ▼              ▼               ▼               ▼              ▼
 [TRUSTED]      [TRUSTED]      [UNTRUSTED]      [REVIEW_REQ]   [REVIEW_REQ]
                    │                                              │
          (emits correction)                              (remains actionable)
```

---

## 2. Five Explicit Decision Types

| Decision Type | Purpose & Action | Resulting Trust Status | Versioning & Audit |
| :--- | :--- | :---: | :--- |
| `VALIDATE` | Planner concurs with machine recommendation & activity match. | `TRUSTED` | Appends `ValidationDecision` and `TrustAssessment v(N+1)`. |
| `CHANGE_MATCH` | Re-maps execution event to a different baseline Activity ID (enforces Rule 5). | `TRUSTED` | Appends `ValidationDecision`, `TrustAssessment v(N+1)`, and emits derived `PlannerCorrectionRecord`. |
| `REJECT` | Rejects reported execution claim (e.g. invalid report or contractor error). | `UNTRUSTED` | Appends `ValidationDecision` and `TrustAssessment v(N+1)`. |
| `REQUEST_EVIDENCE` | Flags event back to site for missing locators/proof ("insufficient information to conclude"). | `REVIEW_REQUIRED` | Appends `ValidationDecision` and `TrustAssessment v(N+1)`. Event remains in queue. |
| `DEFER` | Postpones decision for shift handoff or senior planner review. | `REVIEW_REQUIRED` | Appends `ValidationDecision` and `TrustAssessment v(N+1)`. Event remains actionable. |

---

## 3. Strict Non-Mutation Audit Rules

1. **In-Place Updates Prohibited:** `UPDATE candidate_matches`, `UPDATE match_results`, `UPDATE execution_events` statements are strictly forbidden.
2. **Decision State Snapshot:** Every `ValidationDecision` MUST record:
   * `reviewed_trust_version`: Locked version index presented to planner.
   * `reviewed_match_result_id`: Locked match result ID presented to planner.
   * `reviewed_evidence_assessment_id`: Locked evidence assessment ID presented.
3. **Institutional Memory Hook (Phase 14 Prep):** Re-mapping decisions (`CHANGE_MATCH`) create a derived `PlannerCorrectionRecord` capturing `original_activity_id` vs `corrected_activity_id` and `reason_category` for long-term productivity learning without executing real-time retraining in Phase 9.

---

## 4. Deterministic Review Queue Prioritization

Review queue items are ranked deterministically by priority tier and tie-breaking order:

1. **Priority Tier Precedence:**
   * **$P1$ (CRITICAL):** `CRITICAL` Severity Conflict Flag (e.g. `QA_CONFLICT`).
   * **$P2$ (HIGH):** `HIGH` Severity Conflict (Status/Quantity/Duplicate) or `AMBIGUOUS` Match Outcome.
   * **$P3$ (MEDIUM):** `INSUFFICIENT_EVIDENCE` Outcome or Mandatory Evidence Gap.
   * **$P4$ (LOW):** Match confidence below threshold.
2. **Deterministic Tie-Breaking Order:**  
   $$\text{Priority Tier (P1} \rightarrow \text{P4)} \longrightarrow \text{Ingestion Timestamp (Oldest first)} \longrightarrow \text{Match Confidence (Lowest first)} \longrightarrow \text{Event ID}$$

---

## 5. Review Workspace UI Presentation Contract

```text
================================================================================
PLANNER REVIEW WORKSPACE — EVENT ID: EVT-1010
================================================================================
RAW FIELD EVIDENCE:  "2026-09-02: Mainline ROW clearing 400m completed on PL-16-01 under ACT-1010. QA cleared."
PROVENANCE LOCATOR:  Sheet1!B12 (File: dpr_reports.xlsx, Author: Site Engineer)

MACHINE INTERPRETATION & ASSESSMENT:
• Extracted Event:    ROW Clearing (Quantity: 400.0 METER, Status: FINISH)
• Matched Activity:   ACT-1010 - Mainline ROW Clearing Sec 1 (Score: 91.0%)
• Evidence Support:   84.0% (Tier: HIGH, 2 unique origin groups)
• Detected Conflicts: NONE
• Current Trust:      🟢 TRUSTED (v1)

PLANNER DECISION ACTION:
[1] VALIDATE (Concur)  [2] CHANGE MATCH  [3] REJECT  [4] REQUEST EVIDENCE  [5] DEFER

STATE SNAPSHOT LOCKED: Trust v1 | Match MTH-492F01A8 | Evidence EVA-89A120FB
================================================================================
```
