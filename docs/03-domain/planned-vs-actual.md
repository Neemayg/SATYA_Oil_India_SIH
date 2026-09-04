# Planned vs. Actual Mechanics & Failure Mode Analysis

> **Document Type:** Planned vs. Actual Domain Mechanics & Failure Catalog  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Planned vs. Actual Schedule Mechanics

In Primavera P6 and MS Project, tracking physical execution requires updating 4 core parameters:
1. **`Actual Start Date`**: The verified date when work commenced.
2. **`Actual Finish Date`**: The verified date when work reached 100% completion.
3. **`Physical Percent Complete` ($\%_{\text{phys}}$)**: The proportion of physical quantity executed relative to baseline scope ($Q_{\text{actual}} / Q_{\text{planned}}$).
4. **`Remaining Duration` ($D_{\text{rem}}$)**: Estimated working time required to complete the remaining scope.

### The Inter-Attribute Mathematical Constraints
* If $\%_{\text{phys}} > 0\%$, then `Actual Start` MUST be populated.
* If $\%_{\text{phys}} = 100\%$, then `Actual Finish` MUST be populated and $D_{\text{rem}} = 0$.
* If $\%_{\text{phys}} < 100\%$, then `Actual Finish` MUST BE NULL and $D_{\text{rem}} > 0$.

---

## 2. Failure Mode Analysis & SATYA Mitigation Catalog

This section details 17 operational failure modes that occur when translating field observations to schedule actuals today, alongside SATYA's architectural counter-strategies.

```
FAILURE MODE CATEGORIES
├── 1. Lexical & Semantic Failures (1.1 - 1.3)
├── 2. Structural & Selection Failures (2.1 - 2.3)
├── 3. Temporal & Multi-Event Failures (3.1 - 3.3)
├── 4. Evidence & Granularity Failures (4.1 - 4.3)
├── 5. Logic & Sequence Failures (5.1 - 5.3)
└── 6. AI & Data Integrity Failures (6.1 - 6.2)
```

---

### Category 1: Lexical & Semantic Failures

#### 1.1 Terminology Mismatch
* **Description:** Field report uses localized site jargon (e.g., "Muck clearance done"), while P6 uses formal title (`Excavation & Waste Disposal`).
* **Operational Consequence:** String search fails; planner misidentifies task.
* **SATYA Mitigation:** Activity Fingerprinting using semantic embeddings and domain alias lookup.

#### 1.2 Non-Standard Abbreviations
* **Description:** Field report uses heavy abbreviations (e.g., `HDD 16in CS Xing Ch 12+400`).
* **Operational Consequence:** Regex parsers crash; manual interpretation required.
* **SATYA Mitigation:** Preprocessing normalization expansion layer trained on oil/gas construction acronyms.

#### 1.3 Spelling Variations & Typographical Errors
* **Description:** Field supervisor misspells names (e.g., "Treshing" instead of "Trenching", "Jont" instead of "Joint").
* **Operational Consequence:** Keyword matching drops match score to 0.
* **SATYA Mitigation:** Combined fuzzy edit-distance (Levenshtein) and phonetically resilient character n-gram matching.

---

### Category 2: Structural & Selection Failures

#### 2.1 Missing Activity IDs
* **Description:** Field observations never contain Primavera `Activity ID`s.
* **Operational Consequence:** Database direct key joins fail completely.
* **SATYA Mitigation:** Multi-factor contextual matching (semantic + WBS structural position + spatial location + temporal window).

#### 2.2 Multiple Candidate Activities
* **Description:** A report states "Trenching 100m completed", matching 12 different trenching activities across various pipeline sections.
* **Operational Consequence:** High risk of assigning progress to the wrong activity.
* **SATYA Mitigation:** Spatial chainage filtering and WBS parent node scoping to narrow candidate activities; assign confidence score.

#### 2.3 Wrong Activity Selection
* **Description:** A field event for `Section 2 Pipe Stringing` is mapped to `Section 1 Pipe Stringing` by a rushed planner.
* **Operational Consequence:** Section 1 is falsely marked complete; Section 2 actual delay is hidden.
* **SATYA Mitigation:** Temporal window gating and predecessor status verification to penalize out-of-bound candidate activities.

---

### Category 3: Temporal & Multi-Event Failures

#### 3.1 Duplicate Field Reports
* **Description:** Contractor reports 50m pipe laying in Monday's DPR and includes the same 50m in Tuesday's cumulative summary.
* **Operational Consequence:** Progress double-counted (100m recorded for 50m physical work).
* **SATYA Mitigation:** Provenance hash tracking and cumulative delta calculation in the Execution Event Ledger.

#### 3.2 Delayed Field Reporting
* **Description:** Field work performed on 1st of month is reported on 25th of month.
* **Operational Consequence:** Schedule actual start timestamp applied retroactively, causing sudden S-curve jump.
* **SATYA Mitigation:** Separate `observed_timestamp` from `ingested_timestamp` to maintain true chronological audit trail.

#### 3.3 Contradictory Field Reports
* **Description:** Contractor DPR claims 100% welding complete; QA report submitted same day notes NDT rejection on 4 joints.
* **Operational Consequence:** Progress accepted, leading to rework dispute during commissioning.
* **SATYA Mitigation:** Active Conflict Engine detects opposing claims and flags event for HITL review.

---

### Category 4: Evidence & Granularity Failures

#### 4.1 Activity Aggregation (Micro to Macro)
* **Description:** 30 daily field events map to 1 long-duration L5 activity.
* **Operational Consequence:** Individual micro-events are lost or overwrite previous progress values.
* **SATYA Mitigation:** Event aggregation pipeline summing incremental quantities ($Q_{\text{cum}} = \sum q_i$) against baseline target ($Q_{\text{target}}$).

#### 4.2 Activity Splitting
* **Description:** Field report states "Trenching stopped halfway due to hard rock; crew moved to Section B".
* **Operational Consequence:** Partial activity progress recorded without capturing split duration.
* **SATYA Mitigation:** Execution Event Ledger captures sub-event location bounds and logs operational stoppage tags.

#### 4.3 Missing Verifying Evidence
* **Description:** High progress percentage (e.g., 90%) claimed without attached photo, QA test, or measurement sheet.
* **Operational Consequence:** "Optimism bias" accepted into schedule baseline.
* **SATYA Mitigation:** Evidence-backed scoring reduces confidence score ($\text{Confidence} < 0.60$) for unverified claims, triggering HITL review.

---

### Category 5: Logic & Sequence Failures

#### 5.1 Out-of-Sequence Execution
* **Description:** Field report indicates pipe lowering started before trenching activity is marked finished.
* **Operational Consequence:** Primavera P6 CPM logic engine throws warnings or distorts critical path calculations.
* **SATYA Mitigation:** Dependency graph verification flagging `Out-of-Sequence` warning to planner.

#### 5.2 Planned vs. Actual Date Ambiguity
* **Description:** Field note says "Started on Tuesday", but report doesn't specify if Tuesday refers to this week or last week.
* **Operational Consequence:** Wrong calendar date populated in actual start field.
* **SATYA Mitigation:** Relative date resolution using document creation metadata and temporal window bounds.

#### 5.3 "Not Reported" Misinterpreted as "Not Started"
* **Description:** Remote site loses cellular connectivity for 4 days; zero DPRs arrive. System assumes zero progress occurred.
* **Operational Consequence:** False schedule delay alert generated.
* **SATYA Mitigation:** Explicit `EvidenceGap` classification distinguishing missing data from verified non-performance.

---

### Category 6: AI & Data Integrity Failures

#### 6.1 AI Model Hallucination
* **Description:** An unconstrained LLM invents a non-existent Activity ID (e.g., `ACT-9999`).
* **Operational Consequence:** PMIS database import crashes or corrupts project schedule.
* **SATYA Mitigation:** Rule 5 enforcement—matching engine strictly operates over a closed dictionary of valid baseline activity IDs; supports `UNMATCHED`.

#### 6.2 Stale Schedule Baseline Data
* **Description:** Field observations matched against an outdated P6 schedule baseline revised 2 months ago.
* **Operational Consequence:** Invalid activity mappings and wrong WBS path assignments.
* **SATYA Mitigation:** Versioned schedule manifest ingestion; matching engine binds events to specific active baseline version IDs.
