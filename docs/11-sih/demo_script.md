# SATYA Live 12-Minute Demo Script & Presenter Guide

**Repository:** SATYA (Schedule-Aligned Truth & Yield Analytics) — Oil India Limited (SIH 2026)  
**Document Path:** `docs/11-sih/demo_script.md`  
**Purpose:** Minute-by-minute presenter narration, UI click sequence, screen navigation, and backup failure recovery instructions for the live SIH 2026 presentation.

---

## Storyline Overview

The demo follows **ONE SINGLE MESSY FIELD REPORT** (`SRC-DEMO-001`) from raw observation through extraction, matching, human reconciliation, institutional memory distillation, actual progress projection, and Time Agent warning detection.

> [!IMPORTANT]
> **Core Pitch Line:** "SATYA does not merely digitize daily progress reports. It establishes an evidence-backed bridge between what the field reports and what the Primavera P6 schedule can safely believe."

---

## Timeline & Minute-by-Minute Script

```
0:00        1:00        2:00                5:00            7:00         8:30         9:30           11:00       12:00
│  Problem   │ SATYA Concept│ Field Ingestion & │ Reconciliation │ HITL       │ Memory     │ Time Agent   │ Performance│ Closing │
│  Statement │ Architecture │ Extraction        │ Desk (Hero UI) │ Validation │ Distillation│ & Projection │ & Safety   │ Impact  │
```

---

### Segment 1: The Problem Statement (0:00 – 1:00)
- **Presenter Screen**: Slide 2 (The Real Problem)
- **Presenter Narration**:
  > *"Good morning, esteemed judges. Infrastructure projects like Oil India's cross-country gas pipelines suffer from a fundamental disconnect. On one hand, we have **Field Reality**—messy daily progress reports (DPRs), site photos, voice notes, and WhatsApp updates written in informal field jargon like 'HDD Section 3'. On the other hand, we have the formal **Project Schedule**—Primavera P6 with 10,000 activity IDs, strict WBS codes, and baseline finish dates.*  
  >  
  > *Today, planners manually spend hours copying text into spreadsheets, guessing which activity was completed. Existing tools digitize text, but ask a fatal question: **Can the project schedule safely believe it?** If an unverified report silently updates a baseline schedule, the schedule loses integrity."*

---

### Segment 2: The SATYA Concept & Trust Layer (1:00 – 2:00)
- **Presenter Screen**: Slide 3 & Slide 4 (SATYA Architecture & Trust Boundary)
- **Presenter Narration**:
  > *"Enter **SATYA**—Schedule-Aligned Truth & Yield Analytics. SATYA is not an AI chatbot or a generic dashboard. It is an **Execution Intelligence Trust Layer** that sits between field observations and the project schedule.*  
  >  
  > *SATYA enforces a strict architectural principle: **Field Reality \(\neq\) Extracted Data \(\neq\) Scheduled Actuals**. SATYA never silently coerces bad text into schedule progress. Every progress claim must pass multi-factor fingerprint matching, evidence verification, and human-in-the-loop validation."*

---

### Segment 3: Live Ingestion, Extraction & Candidate Matching (2:00 – 5:00)
- **Presenter Screen**: Live SATYA Web UI — Ingestion / Field Capture Tab
- **Operator Action**:
  1. Open Field Capture Tab (`frontend/index.html`).
  2. Paste raw DPR snippet from [`demo_data.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/11-sih/demo_data.md):
     ```text
     Night shift: HDD Section 3 crossing completed. Approx. 420 m drilling completed on Line PL-16-01. QA/NDT clearance pending due to hydrotest delay. Work reported today, execution started yesterday.
     ```
  3. Click **Submit Payload**.
- **Presenter Narration**:
  > *"Let's see SATYA in action. We paste a raw, unformatted DPR snippet from Duliajan field office. Watch what happens when we submit.*  
  >  
  > *SATYA's Layer 1 Extraction Engine decomposes this single text block into **three discrete execution events**:
  > 1. A **PROGRESS Event**: 420 meters of pipeline drilling.
  > 2. A **FINISH Event**: Completion claim for HDD Section 3.
  > 3. A **QA_CLEARANCE Event**: Explicit status 'PENDING'.*  
  >  
  > *Notice that SATYA preserved QA status as a separate fact. It did not collapse physical work and QA clearance into a single status. Physical work and quality verification are distinct facts."*

---

### Segment 4: Reconciliation Desk — The Hero UI (5:00 – 7:00)
- **Presenter Screen**: Live SATYA Web UI — Reconciliation Desk Tab
- **Operator Action**: Click on Reconciliation Desk Tab, select Event `EVT-DEMO-101`.
- **Presenter Narration**:
  > *"Now we move to the hero screen of SATYA—the **Reconciliation Desk**. Here, the planner asks: **Why does SATYA believe this field report corresponds to a specific schedule activity?***  
  >  
  > *Look at the Candidate Matching panel. SATYA evaluates candidate activities against the Primavera P6 schedule. It identifies **ACT-1020: Mainline HDD River Crossing Section 3** with a Match Score of **0.42**.*  
  >  
  > *Why is the score 0.42? Look at the factor breakdown:
  > - Location Match: +0.80 ('Section 3')
  > - Discipline Match: +1.00 ('PIPING')
  > - Terminology Match: +0.75 ('HDD crossing')
  > - Explicit Activity ID: +0.00 (No 'ACT-1020' string in raw text).*  
  >  
  > *Because 0.42 is below our safety threshold of \(\theta_{\text{match}} = 0.80\), SATYA **refuses to match automatically**. It designates the status as `INSUFFICIENT_EVIDENCE` and delegates it to the human planner. SATYA is intentionally conservative."*

---

### Segment 5: Human-in-the-Loop Validation & Audit Ledger (7:00 – 8:30)
- **Presenter Screen**: Live SATYA Web UI — Reconciliation Desk Modal
- **Operator Action**:
  1. Select Candidate `ACT-1020`.
  2. Select Decision Type: **CHANGE_MATCH**.
  3. Select Reason: **TERMINOLOGY_ALIAS**.
  4. Type Notes: *"Field phrase HDD Section 3 corresponds to baseline ACT-1020."*
  5. Click **Confirm Decision**.
- **Presenter Narration**:
  > *"As the planner, I verify that 'HDD Section 3' in the field corresponds to activity `ACT-1020` in Primavera. I click **CHANGE MATCH**.*  
  >  
  > *What just happened under the hood? SATYA created a new **Version 2 TrustAssessment** marked `TRUSTED`. But look at the database audit log: **SATYA did not overwrite the machine's original assessment**. Version 1 remains intact in an append-only ledger. We have 100% complete auditability."*

---

### Segment 6: Institutional Memory Distillation (8:30 – 9:30)
- **Presenter Screen**: Live SATYA Web UI — Analytics & Memory Tab
- **Operator Action**:
  1. Click Analytics & Memory Tab.
  2. Highlight the newly created Terminology Alias entry: `"hdd section 3" \(\rightarrow\) ACT-1020`.
  3. Show Status: `CANDIDATE` (1 planner correction).
- **Presenter Narration**:
  > *"Now watch SATYA's **Institutional Memory Store**. The planner correction was automatically distilled into a terminology alias candidate (`hdd section 3 \(\rightarrow\) ACT-1020`).*  
  >  
  > *When a second independent report or planner confirms this mapping, the alias promotes from `CANDIDATE` to `VALIDATED`. In future ingestion runs, this alias provides an additive score boost ($S_{\text{alias}} = +0.25$), allowing future field reports to match automatically.*  
  >  
  > *And here is SATYA's core governance rule: **Institutional Memory assists candidate ranking; it never overrides schedule vocabulary safety or bypasses threshold bounds.** Memory learns terminology, but safety gates remain absolute."*

---

### Segment 7: Schedule Projection & Time Agent Warnings (9:30 – 11:00)
- **Presenter Screen**: Live SATYA Web UI — Control Tower / Projections Tab
- **Operator Action**:
  1. Navigate to Schedule Projections.
  2. Click **Generate Projection**.
  3. Highlight `ACT-1020`: Progress **93.3%** (420m / 450m), Projected Finish **2026-09-09** vs Baseline **2026-09-06** (+3 days delay).
  4. Navigate to Time Agent Warnings Tab. Show 2 active warnings: `FORECAST_FINISH_SLIPPAGE` and `QA_CLEARANCE_BOTTLENECK`.
- **Presenter Narration**:
  > *"Once the execution event is verified into trusted truth, SATYA updates the **Schedule Projection Engine**. Activity `ACT-1020` now reflects 93.3% physical progress (420m of 450m).*  
  >  
  > *Immediately downstream, SATYA's **Time Agent Engine** evaluates the project schedule and surfaces two critical warnings:
  > 1. **FORECAST FINISH SLIPPAGE**: Projected finish date has slipped 3 days past the baseline finish.
  > 2. **QA CLEARANCE BOTTLENECK**: Physical work is 93.3% complete, but QA clearance is PENDING, blocking downstream hydrotest activity `ACT-1025`.*  
  >  
  > *Notice that the Time Agent did not predict this from thin air. It operates strictly downstream of the verified execution trust pipeline."*

---

### Segment 8: System Architecture & Empirical Validation (11:00 – 12:00)
- **Presenter Screen**: Slide 10 & Slide 11 (Technical Differentiation & Empirical Validation)
- **Presenter Narration**:
  > *"To summarize SATYA's technical foundation:
  > - **134 Automated Tests** passing 100% cleanly.
  > - **Empirical Benchmark**: **309 events/second** throughput on Large 10,000-activity workloads with sub-4ms latency.
  > - **Accepted-Match Precision**: **100.0%** at production threshold \(\theta = 0.80\) with zero accepted false matches.
  > - **Honest Benchmark Governance**: Our empirical calibration score (ECE 0.1783) shows that SATYA acts as a conservative safety filter—preferring human reconciliation over unsafe automatic schedule corruption."*

---

### Segment 9: Closing & Value Proposition (12:00 – 13:00)
- **Presenter Screen**: Slide 12 (Impact / Closing Statement)
- **Presenter Narration**:
  > *"SATYA transforms how infrastructure projects manage execution reality. By building an auditable, evidence-backed trust layer between field observations and Primavera P6, SATYA gives Oil India planners faster trusted actuals, earlier variance visibility, and complete peace of mind.*  
  >  
  > ***SATYA turns field observations into evidence-backed execution truth that the project schedule can safely consume.** Thank you, and we welcome your questions!"*

---

## Live Demo Operator Runbook & Backup Plan

### Step-by-Step Operator Checklist
1. **Prerequisites Verification (T-10 mins)**:
   - Ensure local dev server is running on port 8000: `python3 backend/api/app.py` or `python3 scripts/run_server.py`.
   - Verify health endpoint: `curl http://localhost:8000/api/v1/health` $\rightarrow$ `{"status": "UP"}`.
   - Open Chrome browser to `http://localhost:8000`. Set zoom level to **110%**.
2. **Execution Sequence during Speech**:
   - `02:15`: Paste payload `SRC-DEMO-001` into Ingestion text area $\rightarrow$ Click Ingest.
   - `05:10`: Click Reconciliation Desk $\rightarrow$ Select `EVT-DEMO-101`.
   - `07:15`: Open Match Modal $\rightarrow$ Select `ACT-1020` $\rightarrow$ Click `CHANGE_MATCH` $\rightarrow$ Confirm.
   - `08:40`: Open Memory Tab $\rightarrow$ Point to alias `"hdd section 3"`.
   - `09:35`: Open Projections Tab $\rightarrow$ Click Generate Projection $\rightarrow$ Point to +3 days delay on `ACT-1020`.
   - `10:15`: Open Time Agent Tab $\rightarrow$ Point to `QA_CLEARANCE_BOTTLENECK` warning.

### Live Demo Backup Failure Recovery Path
If local server, network, or UI encounters an unexpected issue during presentation:
- **Backup Path A (Pre-loaded Saved State)**: Refresh browser to load pre-seeded SQLite database state (`http://localhost:8000?demo_mode=seeded`).
- **Backup Path B (Offline Visual Walkthrough)**: Use pre-rendered high-resolution screenshot carousel in `docs/11-sih/presentation_deck.md`.
