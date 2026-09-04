# Schedule-Aware Activity Matching Core Engine Specification

> **Document Type:** Core Engine Implementation Specification  
> **Governance Status:** Phase 7 Implementation Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Engine Overview & Architecture

The **Schedule-Aware Activity Matching Engine** (Phase 7) aligns extracted `ExecutionEvent` records to indexed `ActivityFingerprint` records from Primavera P6 / MS Project baseline schedules.

It produces explainable, multi-factor weighted match candidates and classifies every event into one of three explicit outcome states:
* `MATCHED`: High-confidence unambiguous match ($\ge 0.80$ overall confidence score and score margin $> 0.08$).
* `AMBIGUOUS`: Multiple viable candidate activities or moderate confidence ($0.45 \le \text{Confidence} < 0.80$ or close top 2 candidates). Routed to Human-in-the-Loop (HITL) planner review queue.
* `UNMATCHED`: No baseline schedule activity exceeds minimum threshold ($< 0.45$). Prevents false activity matching.

```
[ExecutionEvent] ────> [ScheduleAwareMatchingEngine] <──── [ActivityFingerprints]
                                │
                  ┌─────────────┴─────────────┐
                  │ Multi-Factor Weighted     │
                  │ Compatibility Scoring     │
                  └─────────────┬─────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │ Outcome Classification    │
                  │ & Threshold Evaluation    │
                  └─────────────┬─────────────┘
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
        [MATCHED]          [AMBIGUOUS]        [UNMATCHED]
        (High Conf)        (HITL Queue)      (No Valid Match)
```

---

## 2. Multi-Factor Compatibility Scoring Formula

$$\text{Confidence} = w_{\text{id}} \cdot S_{\text{id}} + w_{\text{tag}} \cdot S_{\text{tag}} + w_{\text{spatial}} \cdot S_{\text{spatial}} + w_{\text{wbs}} \cdot S_{\text{wbs}} + w_{\text{disc}} \cdot S_{\text{disc}} + w_{\text{term}} \cdot S_{\text{term}} + w_{\text{time}} \cdot S_{\text{time}}$$

| Factor | Weight ($w$) | Evaluated Compatibility Signals |
| :--- | :---: | :--- |
| **Explicit Identifier ($S_{\text{id}}$)** | 0.35 | 1.0 if explicit Activity ID matches valid schedule fingerprint |
| **Line / Equipment Tag ($S_{\text{tag}}$)** | 0.15 | Exact match on pipeline line number or equipment tag |
| **Spatial / Chainage ($S_{\text{spatial}}$)** | 0.15 | Area / zone / chainage interval overlap |
| **WBS Structure ($S_{\text{wbs}}$)** | 0.10 | WBS topological path alignment |
| **Discipline ($S_{\text{disc}}$)** | 0.10 | Engineering discipline match (Civil, Piping, Electrical, etc.) |
| **Terminology Action ($S_{\text{term}}$)** | 0.10 | Action verbs, entity nouns & domain synonyms match |
| **Temporal Window ($S_{\text{time}}$)** | 0.05 | Event date falls within or near planned baseline start/finish window |

---

## 3. Human-Readable Reasoning Trace

Every `MatchResult` includes audit-traceable bullet points explaining the decision without exposing raw LLM chain-of-thought:

```json
{
  "match_id": "MTH-492F01A8",
  "event_id": "EVT-1010",
  "outcome": "MATCHED",
  "selected_activity_id": "ACT-1010",
  "confidence_score": 0.96,
  "reasoning_trace": [
    "Status: MATCHED (Activity: ACT-1010, Confidence: 0.96)",
    "Selected Top Candidate: ACT-1010 - Mainline ROW Clearing & Grading Sec 1",
    "+ Explicit Activity ID 'ACT-1010' matches baseline schedule activity ACT-1010",
    "+ Line number 'PL-16-01' matches activity line reference",
    "+ Location area 'Section 1' matches activity zone 'Section 1'",
    "+ Discipline 'CIVIL' matches activity discipline 'CIVIL'",
    "+ Action verb(s) ['clearing', 'grading'] match activity action verb(s)",
    "+ Event date '2026-09-02' falls within planned baseline window (2026-09-01 to 2026-09-05)"
  ]
}
```

---

## 4. Implemented Backend Modules

* [`backend/models/domain_models.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/models/domain_models.py): Defines `MatchOutcome`, `MatchFactorScores`, `CandidateMatch`, and `MatchResult`.
* [`backend/matching/matching_engine.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/matching/matching_engine.py): Multi-factor scoring engine, candidate evaluator, threshold classifier, and reasoning trace generator.
* [`backend/persistence/database_engine.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/persistence/database_engine.py): SQLite persistence layer with `match_results` append-only table.
* [`backend/services/matching_service.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/services/matching_service.py): Service orchestrator coordinating event-to-fingerprint matching.
* [`scripts/evaluate_matching_engine.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/scripts/evaluate_matching_engine.py): Synthetic ground truth benchmark evaluation harness.

---

## 5. Architectural Isolation Safeguards

1. **Non-Destructive Event Ledger:** `MatchResult` records are stored in a separate `match_results` table. `raw_observed_activity_id` and `observed_activity_id` on `ExecutionEvent` are NEVER overwritten.
2. **Rule 5 Enforcement:** The engine NEVER fabricates Activity IDs. If no candidate exceeds threshold, it cleanly outputs `UNMATCHED`.
3. **Deterministic & Testable:** 100% unit and integration test coverage without external API or network dependencies.
