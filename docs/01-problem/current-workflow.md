# Current As-Is Workflow & Information Loss Analysis

> **Document Type:** As-Is Operational Process Analysis  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. As-Is Operational Workflow Overview

Currently, in Oil India infrastructure projects, field progress reporting follows a multi-step manual aggregation pipeline across organizational boundaries.

```
+-----------------------------------------------------------------------------------+
| STEP 1: PHYSICAL WORK EXECUTION (Site Crews & Contractors)                        |
| Field crews perform trenching, pipe stringing, welding, civil foundations, etc.   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 2: DAILY SITE LOGGING (Contractor Engineer / Site Supervisor)                |
| Data logged into paper sheets, site notebooks, WhatsApp groups, or Excel DPRs.   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 3: DPR COMPILATION & SUBMISSION (Contractor PM Office)                       |
| Contractor aggregates daily shift sheets into a Daily Progress Report (PDF/Excel).|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 4: VERIFICATION & COMPILATION (Oil India Resident/Site Engineer)             |
| Site Engineer manually reviews DPR, checks samples, signs off, forwards to PMO.  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 5: MANUAL PMIS/P6 UPDATE (Oil India Planning Engineer)                       |
| Planner reads text summaries, searches P6 schedule, manually interprets mapping,  |
| and types in Actual Start/Finish dates and physical % complete.                   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 6: EXECUTIVE S-CURVE & REPORTING (PMO Leadership)                             |
| Baseline vs. Actual S-Curves produced for management review.                       |
+-----------------------------------------------------------------------------------+
```

---

## 2. Detailed Step-by-Step Vulnerability & Information Loss Analysis

### Step 1 $\rightarrow$ Step 2: Physical Work to Daily Site Logging
* **Mechanism:** Site supervisor notes down work done during or at the end of a shift.
* **Information Loss:** Exact timestamps of work start/finish are lost; micro-location details are rounded off; local site bottlenecks (weather, machinery downtime) are captured informally or omitted.
* **Vulnerability:** Subjective quantity estimation (e.g., estimating "roughly 100m dug" without physical chainage measurement).
* **Status:** `[CONFIRMED]`

### Step 2 $\rightarrow$ Step 3: Site Logging to DPR Compilation
* **Mechanism:** Contractor office clerk compiles daily shift logs into a standardized DPR Excel/PDF template.
* **Information Loss:** Specific crew-level comments stripped; multi-location details flattened into single daily totals; photos/inspection slips stored in separate folders without cross-references.
* **Vulnerability:** Contractor optimism bias—exaggerating work quantities to meet daily billing targets; omitting safety incidents or work stoppages.
* **Status:** `[CONFIRMED]`

### Step 3 $\rightarrow$ Step 4: DPR Submission to Site Engineer Verification
* **Mechanism:** Oil India site engineer receives PDF/Excel DPR via email or file share, verifies against physical memory or site visits, signs approval.
* **Information Loss:** Detailed site engineer observations remain verbal or in personal notebooks; paper sign-offs create audit fragmentation.
* **Vulnerability:** Time pressure prevents site engineers from physically measuring every reported quantity; partial sign-offs accepted without QA certificates.
* **Status:** `[REASONABLE DOMAIN ASSUMPTION]`

### Step 4 $\rightarrow$ Step 5: Verified DPR to Planner Primavera P6 Update
* **Mechanism:** PMO Planning Engineer receives weekly batch of approved DPRs. Planner opens Primavera P6, manually reads DPR descriptions, searches for matching activity names, calculates percentage complete, and enters numbers.
* **Information Loss:** **CRITICAL LOSS POINT.** Contextual evidence (photos, QA slips, location chainages) is completely severed. The Primavera P6 database only stores a flat percentage number (e.g., `45%`), losing all link to raw DPR sources.
* **Vulnerability:** 
  1. *Guesswork Mapping:* Planner matches "Pipe Laying near River" to `ACT-2040` without knowing if it refers to Section A or Section B.
  2. *Granularity Flattening:* 10 daily field entries collapsed into a single manual slider movement in P6.
  3. *Unnoticed Conflicts:* If Contractor DPR says "100% welded" but QA report says "NDT failed", the planner enters 100% because QA reports are in a different binder.
* **Status:** `[CONFIRMED]`

---

## 3. Quantification of Reporting Latency

```
Physical Work Occurs (Day 0)
    │
    ├── Contractor DPR Compiled (Day 1)
    │
    ├── Site Engineer Sign-off (Day 3 - 5)
    │
    ├── PMO Batch Transmittal (Day 7 - 14)
    │
    └── Primavera P6 Update Entry (Day 15 - 30)
```

* **Latency:** Between 15 and 30 calendar days elapse between physical field execution and Primavera P6 schedule updates.
* **Operational Consequence:** Executive management views S-curves and critical path reports that are 3 to 4 weeks out of date, rendering proactive delay intervention impossible.

---

## 4. What "Real-Time" Realistically Means in Oil & Gas Construction

* **Myth:** Real-time project tracking means sub-second streaming IoT sensors on every shovel.
* **Realistic Domain Reality:** `[REASONABLE DOMAIN ASSUMPTION]` Real-time means **Daily to 48-Hour Batch Execution Alignment**—processing site observations as they occur on shift, validating evidence within 24 hours, and providing planners with daily verified schedule actual projections rather than monthly batch updates.
