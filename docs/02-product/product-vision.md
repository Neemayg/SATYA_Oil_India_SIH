# SATYA Product Vision & System Positioning

> **Document Type:** Product Vision & Positioning Architecture  
> **Governance Status:** Phase 2 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Core Vision Statement

> **"We are not replacing the project schedule. We are creating the evidence-backed execution layer that makes schedule actuals trustworthy."**

**SATYA** (Schedule-Aligned Truth & Yield Analytics) is an **Execution Truth Layer (ETL)** designed for capital infrastructure projects executed by Oil India Limited. Positioned between heterogeneous, fragmented field execution observations and the formal Primavera P6 / MS Project L5/L6 schedule, SATYA converts informal field reports into immutable, evidence-backed Execution Events, links them to schedule activities, evaluates confidence, surfaces contradictions, and routes low-confidence events to human planners before producing audit-trusted schedule actuals.

---

## 2. What SATYA Is vs. What SATYA Is NOT

| What SATYA IS | What SATYA IS NOT |
| :--- | :--- |
| **An Execution Intelligence & Truth Layer:** Positioned between field execution and Primavera P6. | **A Generic AI Chatbot:** It is not a conversational Q&A bot built on top of PDF documents. |
| **An Evidence-Backed Grounding Engine:** Linking physical proof (photos, QA logs) to schedule progress. | **A DPR Summarizer:** It does not merely generate daily executive summaries or bullet points. |
| **An Immutable Observation Event Ledger:** Preserving raw field inputs and complete provenance. | **A PMIS / Primavera Replacement:** It does not create or overwrite baseline schedule logic. |
| **A Schedule-Aware Matching Engine:** Grounding field logs against L5/L6 Activity Fingerprints. | **A Generic Construction Dashboard:** It does not simply render static BI charts without schedule grounding. |
| **A Human-in-the-Loop Safeguard:** Keeping planners accountable for low-confidence/disputed updates. | **An Autonomous Decision Maker:** AI never invents Activity IDs or forces schedule changes silently. |

---

## 3. Who SATYA Is Primarily For

1. **Primary Operational User:** **Oil India PMO Planning & Scheduling Engineers** who currently spend up to 70% of their working hours manually reading text DPRs, guessing Primavera activity matches, and updating P6 actuals.
2. **Primary Operational Provider:** **Resident Site Engineers & Field Supervisors** reporting daily shift work across remote pipeline, drilling, and civil sites.
3. **Primary Executive Consumer:** **Oil India Project Directors & PMO Leadership** requiring audit-proof, evidence-backed progress percentage and early warnings of critical path delays.

---

## 4. The Operational Problem Solved

Existing manual project management workflows fail because:
* Field execution information is **heterogeneous** (PDFs, spreadsheets, WhatsApp text, voice memos, paper logs).
* Field observations are **differently granular** (shift-level micro-tasks vs. L5/L6 work packages).
* Field terminology is **informal and localized** (lacking Primavera Activity IDs).
* Progress reports suffer from **optimism bias** ("90% complete syndrome") due to unverified subjective percentage entry.
* Contradictions between contractor DPR claims and third-party QA inspection logs remain hidden in manual spreadsheets.

SATYA bridges this gap by creating a deterministic, evidence-verified pipeline that transforms informal field claims into trusted schedule updates.

---

## 5. What Makes the Execution Truth Layer Different

```
TRADITIONAL METHOD:
[Field Observation] --------(Manual Interpretation / Guesswork)--------> [Primavera P6 Actuals]
                                                                        (Unverified & Latent)

SATYA EXECUTION TRUTH LAYER:
[Field Observation]
       │
       ▼
[Execution Event Ledger] (Immutable + Provenance)
       │
       ▼
[Activity Fingerprint Matching] (Semantic + WBS + Temporal)
       │
       ▼
[Evidence & Conflict Verification] (Confidence Score + QA Proof)
       │
       ▼
[Human-in-the-Loop Validation] (Planner Review Queue)
       │
       ▼
[Trusted Execution Event]
       │
       ▼
[Schedule Projection] (Audit-Proof Primavera P6 Actuals)
```

---

## 6. The Trusted Execution Event Concept

A **Trusted Execution Event** is an immutable, verified record representing a physical work occurrence that has satisfied 4 criteria:
1. **Provenance Verification:** Raw text snippet, byte offset, author, and timestamp recorded in the immutable ledger.
2. **Schedule Activity Alignment:** Matched to a valid baseline L5/L6 Activity ID without AI hallucination.
3. **Multi-Modal Evidence Corroboration:** Supported by physical proof (geotagged photo, QA clearance certificate, survey log) or explicit planner review.
4. **Conflict Resolution:** Checked for contradictory claims and out-of-sequence execution logic.

---

## 7. Anti-Generic-AI Critical Evaluation

* **Test Question 1:** *"If we removed the word 'AI' from this product description, would SATYA still solve a difficult operational problem?"*
  * **Answer:** **YES.** SATYA solves the fundamental structural, spatial, and temporal alignment problem between micro-level field observations and Primavera L5/L6 schedule baselines, establishing an audit-proof evidence ledger and human-in-the-loop validation gate.
* **Test Question 2:** *"Could this product be described simply as 'DPR parser + LLM + dashboard'?"*
  * **Answer:** **NO.** A DPR parser + LLM + dashboard lacks schedule-aware topology, multi-vector activity fingerprinting, evidence-backed confidence math, active conflict/evidence-gap detection, immutable ledger provenance, and institutional memory accumulation.
