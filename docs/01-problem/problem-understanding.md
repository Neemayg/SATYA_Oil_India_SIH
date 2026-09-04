# Comprehensive Problem Understanding

> **Document Type:** Problem Analysis & Core Domain Mechanics  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  
> **Target Audience:** Architects, Domain Experts, Product Leads, SIH Evaluators  

---

## 1. Context & Background

Oil India Limited (OIL), a Navratna Public Sector Undertaking, executes high-capital upstream energy infrastructure projects across remote and challenging geographies (such as the Upper Assam Basin, Rajasthan fields, and offshore blocks). These projects include cross-country oil and gas pipelines, Gas Gathering Stations (GGS), Central Processing Facilities (CPF), drilling rig location preparations, and civil access infrastructure.

Project management offices (PMOs) at Oil India rely on structured, multi-tiered project schedules created in Primavera P6 or MS Project. These schedules contain thousands of activities organized into Work Breakdown Structures (WBS) down to Level 5 (Work Package) and Level 6 (Step/Task).

However, actual physical execution happens on the ground through multiple EPC (Engineering, Procurement, Construction) contractors, sub-contractors, discipline site engineers, and quality inspectors operating across spread-out field locations.

---

## 2. The Fundamental Disconnect

The core problem facing Oil India is an **information asymmetry and structural disconnect** between field execution reality and the formal PMIS project schedule.

```
+-----------------------------------------------------------------------+
|                    FIELD EXECUTION REALITY                            |
|  - Physical work: trenching, pipe stringing, welding, QA testing      |
|  - Fragmented observations: paper DPRs, WhatsApp, voice memos, photos |
|  - Micro-granularity: "150m pipe laid at Ch. 12+400 near stream"      |
+-----------------------------------------------------------------------+
                                   |
                                   |  (Manual aggregation, delay, bias,
                                   |   semantic loss, missing activity IDs)
                                   v
+-----------------------------------------------------------------------+
|                    FORMAL PROJECT SCHEDULE (P6)                       |
|  - Macro-granularity: Activity ACT-4820 (Mainline Pipe Laying Sec 2)   |
|  - Static dates: Planned Start, Planned Finish, Baseline Duration     |
|  - L5/L6 activities requiring explicit Actual Start/Finish & % Progress|
+-----------------------------------------------------------------------+
```

### Key Dimensions of the Disconnect
1. **Granularity Disconnect:** Field logs record micro-observations (e.g., "Crew 3 completed 12 joints of 16-inch welding"), while the baseline schedule tracks macro activities (e.g., `ACT-3020: Mainline Pipeline Welding - Zone B`).
2. **Taxonomy & Terminology Disconnect:** Field personnel use informal site shorthand (e.g., "tie-in done near river crossing"), whereas Primavera P6 uses formal WBS descriptions (e.g., `HDD-CW-04: Horizontal Directional Drilling River Crossing Tie-In`).
3. **Temporal & Latency Disconnect:** Physical events happen in real time, but reports are compiled daily, forwarded weekly, and entered into Primavera monthly—creating a 14 to 30-day reporting lag.
4. **Evidence & Integrity Disconnect:** Reported percentage progress is entered into spreadsheets without verifiable physical evidence (photos, NDT inspection logs, material slips), creating "optimism bias" and sudden late-stage delay surprises.

---

## 3. The Conceptual Backbone: Information Execution Chain

SATYA models the transformation of field physical reality into trusted schedule progress through a strict **7-stage Information Chain**.

```
[1. Field Observation]
         |
         v
[2. Source Document / Statement]
         |
         v
[3. Extracted Execution Event]
         |
         v
[4. Activity Matching]
         |
         v
[5. Multi-Modal Evidence Validation]
         |
         v
[6. Trusted Execution Event]
         |
         v
[7. Schedule Projection]
```

### Detailed Transition Analysis & Vulnerabilities

| Stage Transition | Operational Input | Output | What Can Go Wrong at This Transition |
| :--- | :--- | :--- | :--- |
| **1 $\rightarrow$ 2: Field Obs. $\rightarrow$ Source Doc** | Physical work performed on site | DPR, voice memo, site photo, inspection log | *Incomplete reporting, omitted events, delayed entry, typographical errors, subjective estimations.* |
| **2 $\rightarrow$ 3: Source Doc $\rightarrow$ Extracted Event** | Raw unstructured file/text | Normalized `ExecutionEvent` (raw entity) | *NLP parsing failure, entity extraction ambiguity, loss of context, misread numbers, wrong unit of measure.* |
| **3 $\rightarrow$ 4: Extracted Event $\rightarrow$ Matched Activity** | `ExecutionEvent` + Schedule Baseline | Candidate L5/L6 Activity Linkage | *Vocabulary mismatch, multiple candidate activities, incorrect WBS assignment, AI hallucination of Activity ID.* |
| **4 $\rightarrow$ 5: Match $\rightarrow$ Validation** | Candidate Match + Evidence Artifacts | Verified / Disputed Status + Confidence Score | *Missing evidence photos, conflicting contractor vs. QA report, stale inspection certificates, low confidence.* |
| **5 $\rightarrow$ 6: Validation $\rightarrow$ Trusted Event** | Verified Match + HITL Resolution (if low confidence) | Immutable `TrustedExecutionEvent` | *Planner override errors, uncalibrated thresholds, unverified planner bias.* |
| **6 $\rightarrow$ 7: Trusted Event $\rightarrow$ Schedule Projection** | `TrustedExecutionEvent` | Updated Actual Start/Finish & Progress % | *Corrupting baseline critical path, out-of-sequence logic errors, invalid Primavera date constraints.* |

---

## 4. Operational State Progression Model

A central tenet of SATYA's **Execution Truth Layer** is that a field observation is **never automatically a trusted schedule actual**. The state of field execution intelligence progresses strictly through five formal states:

```
+---------------+      +---------------+      +---------------+      +---------------+      +-----------------------+
|   OBSERVED    | ---> |   EXTRACTED   | ---> |    MATCHED    | ---> |   VALIDATED   | ---> | PROJECTED TO SCHEDULE |
+---------------+      +---------------+      +---------------+      +---------------+      +-----------------------+
 Raw field data        Structured event       Candidate L5/L6        Evidence verified       Baseline update /
 received              parsed                 link established       & HITL approved         earned value update
```

1. **`OBSERVED`**: Raw field input ingested (PDF, text, voice, image). Original file archived immutably with hash.
2. **`EXTRACTED`**: Structural parser extracts work action, quantity, location, date, and discipline. Provenance tracked.
3. **`MATCHED`**: Matching engine links extracted event to candidate L5/L6 Activity ID(s) with confidence score ($[0.0, 1.0]$) or returns `UNMATCHED`.
4. **`VALIDATED`**: Multi-modal evidence verified. High-confidence matches auto-pass; low-confidence/conflicting matches approved by human planner.
5. **`PROJECTED TO SCHEDULE`**: Trusted event updates actual start/finish dates, physical % complete, and schedule forecasting without corrupting baseline logic.

---

## 5. Key Domain Questions Answered

* **Who creates the schedule?** `[CONFIRMED]` Oil India PMO / Senior Planning Engineers using Primavera P6 or MS Project.
* **Who executes work?** `[CONFIRMED]` EPC Contractors, specialty sub-contractors, and Oil India field operations units.
* **Who reports actual progress?** `[CONFIRMED]` Contractor Site Engineers, Resident Engineers, Discipline Supervisors, and Third-Party Inspection Agencies (TPIA).
* **What exactly is a DPR?** `[CONFIRMED]` A Daily Progress Report—typically a multi-tab Excel spreadsheet or scanned PDF detailing daily manpower, equipment, quantity executed per area, weather, and bottlenecks.
* **What information does a planner actually receive?** `[REASONABLE DOMAIN ASSUMPTION]` Weekly/monthly aggregated summaries, static spreadsheets, or PDF reports lacking direct mapping to Primavera Activity IDs.
* **How does a field statement become an L5/L6 actual today?** `[REASONABLE DOMAIN ASSUMPTION]` Manually: a planner reads DPR text, guesses which P6 activity corresponds, estimates a cumulative percentage complete, and manually types it into P6.
* **Where does mapping fail today?** `[REASONABLE DOMAIN ASSUMPTION]` In informal text descriptions, missing activity IDs, granularity mismatches, delayed reporting, and subjective percentage claims.
* **What happens when reports contradict?** `[REASONABLE DOMAIN ASSUMPTION]` Contradictions are buried in manual aggregation, leading to sudden disputes during monthly billing or audit cycles.
* **What is lost between field $\rightarrow$ schedule?** `[REASONABLE DOMAIN ASSUMPTION]` Real execution productivity rates, exact start/finish timestamps, specific cause of micro-delays, and physical evidence links.
* **What does "real-time" realistically mean?** `[REASONABLE DOMAIN ASSUMPTION]` Daily to 48-hour batch synchronization matching field reporting cycles, not sub-second IoT streams.
* **What should SATYA automate vs. human decision?**
  * **Automate:** Extraction, Activity Fingerprint matching, confidence scoring, evidence linkage, conflict flagging, and candidate update generation.
  * **Human Decision:** Resolving low-confidence matches, settling contradictory field reports, approving schedule projection overrides, and adjusting baseline constraints.
