# System Architecture Overview & Architectural Principles

> **Document Type:** System Architecture Overview  
> **Governance Status:** Phase 3 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Executive Architecture Summary

SATYA is designed as a modular, evidence-backed **Execution Truth Layer (ETL)** positioned between heterogeneous field execution inputs and formal L5/L6 project schedules (Primavera P6 / MS Project).

The fundamental architectural principle of SATYA is the explicit decoupling of physical reality from interpretation and schedule state:

$$\text{FIELD REALITY} \neq \text{EXTRACTED INTERPRETATION} \neq \text{SCHEDULE ACTUAL}$$

```
                                  ┌────────────────────────────────┐
                                  │   SCHEDULE BASELINE MANIFEST   │
                                  │  (Primavera P6 / MS Project)   │
                                  └───────────────┬────────────────┘
                                                  │
                                                  ▼
                                  ┌────────────────────────────────┐
                                  │  ACTIVITY FINGERPRINT ENGINE   │
                                  └───────────────┬────────────────┘
                                                  │
                                                  │
FIELD OBSERVATIONS                                │
─────────────────                                 │
Excel DPRs / PDFs / Text                          │
Voice Transcripts / Photos                        ▼
        │                         ┌────────────────────────────────┐
        └────────────────────────>│  EXECUTION EVENT EXTRACTION    │
                                  └───────────────┬────────────────┘
                                                  │
                                                  ▼
                                  ┌────────────────────────────────┐
                                  │  SCHEDULE-AWARE MATCH ENGINE   │
                                  └───────────────┬────────────────┘
                                                  │
                ┌─────────────────────────────────┼─────────────────────────────────┐
                ▼                                 ▼                                 ▼
           [MATCHED]                         [AMBIGUOUS]                       [UNMATCHED]
                │                                 │                                 │
                └─────────────────────────────────┼─────────────────────────────────┘
                                                  │
                                                  ▼
                                  ┌────────────────────────────────┐
                                  │  EVIDENCE + CONFIDENCE +       │
                                  │  CONFLICT DETECTION ENGINE     │
                                  └───────────────┬────────────────┘
                                                  │
                                                  ▼
                                  ┌────────────────────────────────┐
                                  │  HUMAN VALIDATION GATE (HITL)  │
                                  └───────────────┬────────────────┘
                                                  │
                                                  ▼
                                  ┌────────────────────────────────┐
                                  │   EXECUTION TRUTH LEDGER       │
                                  └───────────────┬────────────────┘
                                                  │
                                                  ▼
                                  ┌────────────────────────────────┐
                                  │  SCHEDULE PROJECTION ENGINE    │
                                  └────────────────────────────────┘
```

---

## 2. Authoritative Source-of-Truth Model

To prevent data corruption, AI hallucinations, or accidental history destruction, SATYA establishes strict authoritative ownership across system layers:

| Layer / Artifact | Authoritative Source | Immutable? | Authority Rules |
| :--- | :--- | :--- | :--- |
| **Original Source Artifact** | Source Input Layer | `IMMUTABLE` | Stored in raw form with SHA-256 hash. Can never be altered or deleted. |
| **Extracted Event Payload** | Execution Event Ledger | `APPEND-ONLY` | Represents empirical observation. Re-parsing creates a new version; old version preserved. |
| **Schedule Baseline Topology** | Baseline Schedule Manifest | `READ-ONLY` | Project schedule baseline is imported read-only; SATYA never mutates baseline logic. |
| **Candidate Activity Linkage** | Matching Engine Output | `DERIVED` | Probabilistic candidate linkages are calculated; never treated as unverified facts. |
| **Trusted Execution Event** | Human Validation Gate | `MUTABLE GATE` | Transitions to trusted state ONLY when verified by evidence auto-pass or planner sign-off. |
| **Schedule Projection** | Projection Engine View | `DERIVED VIEW` | Downstream projection view generated from trusted events; completely decoupled from raw ledger. |

---

## 3. Technology-Neutral Architecture Design

The architecture of SATYA defines component interfaces, data flows, and state boundaries without binding the design to specific technology vendors or frameworks.

* **Deployment Boundary:** Modular Monolith architecture for SIH MVP, cleanly decoupled so that core engines (Fingerprinting, Extraction, Matching, Conflict) can evolve into microservices if needed in enterprise production.
* **Database Neutrality:** Data models rely on standard relational and JSON document abstractions supported by standard ANSI SQL databases.
* **AI Model Neutrality:** Entity extraction and semantic embedding interfaces use generic model adapter patterns, preventing vendor lock-in to specific LLM APIs.

---

## 4. Architectural Trade-Off Analysis

| Architectural Decision | Option A | Option B | SATYA Recommendation | Engineering Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Deployment Model** | Distributed Microservices | Modular Monolith | **Modular Monolith** | Avoids network latency and complex IPC overhead during SIH MVP development while maintaining strict module boundaries. |
| **Event Storage Model** | In-place Mutable Records | Immutable Append-Only Ledger | **Immutable Append-Only Ledger** | Guarantees 100% auditability for CAG/internal audits. Obsoleted events are marked superseded, not deleted. |
| **Matching Strategy** | Pure LLM Prompting | Hybrid Deterministic + Semantic | **Hybrid Layered Matching** | Pure LLM prompting suffers from hallucination and high latency; hybrid approach uses deterministic filtering before semantic ranking. |
| **Schedule Mutation** | Direct Primavera DB Update | Decoupled Schedule Projection | **Decoupled Schedule Projection** | Directly mutating Primavera DB risks corrupting critical path CPM logic. Projection view exports `.xer`/`.xml` transmittals. |

---

## 5. Architectural Anti-Patterns (Strictly Avoided)

1. **LLM Direct Schedule Mutator:** Allowing an LLM to directly write actual start/finish dates into Primavera P6.
2. **Single Opaque AI Score:** Collapsing extraction, matching, and evidence quality into an unexplained single percentage scalar.
3. **Destructive Aggregation:** Overwriting individual daily field observations during weekly progress calculation.
4. **Silent Overwrite of Conflicts:** Overwriting a contractor claim when a QA test fails, rather than preserving both in conflict state.
5. **Activity ID Hallucination:** Allowing the AI model to invent non-existent schedule Activity IDs.
6. **Absence-as-Delay Fallacy:** Automatically marking an un-reported active task as "Delayed".
7. **Microservice Over-Engineering:** Splitting a hackathon prototype into 15 independent microservices.
