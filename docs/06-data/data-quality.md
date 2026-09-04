# Data Quality Rules & Quarantine Mechanics

> **Document Type:** Data Quality & Quarantine Specification  
> **Governance Status:** Phase 3 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Data Quality Check Catalog

SATYA enforces automated quality gates across all 3 ingestion layers:

```
                  ┌─────────────────────────────────────────┐
                  │    INGESTION & DATA QUALITY GATES       │
                  └────────────────────┬────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
[SCHEDULE QUALITY GATES]      [SOURCE QUALITY GATES]       [EVENT QUALITY GATES]
- Check missing Activity IDs  - Check SHA-256 duplicate    - Check impossible dates
- Check negative durations    - Check unreadable encoding  - Check missing quantities
- Check circular logic ties   - Check missing timestamps   - Check un-mapped disciplines
         │                             │                             │
         └─────────────────────────────┼─────────────────────────────┘
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │  DATA QUARANTINE REPOSITORY   │
                       │ (Quarantined for Review)      │
                       └───────────────────────────────┘
```

---

## 2. Detailed Quality Rules

### 2.1 Schedule Import Quality Rules
* `QUAL-SCH-01` (Unique Activity ID): Duplicate activity IDs in a single schedule import cause the second occurrence to be quarantined.
* `QUAL-SCH-02` (Valid Date Range): Planned start date occurring after planned finish date triggers a schedule logic error and quarantines the activity row.
* `QUAL-SCH-03` (Non-Negative Duration): Duration $< 0$ days is strictly rejected.

### 2.2 Field Source Quality Rules
* `QUAL-SRC-01` (Idempotent SHA-256 Check): If an ingested file matches an existing SHA-256 hash in storage, system returns the existing `SourceDocument` ID without creating duplicate events.
* `QUAL-SRC-02` (Encoding Validation): Corrupted or non-UTF8 text files are rejected with error log `Corrupted_Encoding`.

### 2.3 Execution Event Quality Rules
* `QUAL-EVT-01` (Impossible Future Timestamp): Observations with reported dates $> \text{Current Timestamp} + 24\text{ hours}$ are quarantined as `Future_Date_Error`.
* `QUAL-EVT-02` (Negative Quantities): Physical work quantities $\le 0$ are quarantined unless tagged explicitly as `REWORK_REDUCTION`.

---

## 3. Quarantine Mechanics & Exception Queue

* **Quarantine Store:** Any file, schedule row, or event failing a mandatory quality rule is isolated in the **Quarantine Repository**.
* **Non-Blocking Ingestion:** Quarantined items DO NOT crash the ingestion pipeline; valid rows are processed normally while bad rows are queued for planner inspection in the Exception Interface.
