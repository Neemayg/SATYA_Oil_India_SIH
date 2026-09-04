# Schedule Projection & Actual Progress Engine Specification

> **Document Type:** Core Engine Implementation & Architecture Specification  
> **Governance Status:** Phase 10 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Overview & Core Principles

The **Schedule Projection & Actual Progress Engine** (Phase 10) derives activity-level progress, forecast finish dates, calculation statuses, and schedule baseline variances from trusted execution events.

It enforces 4 fundamental architectural invariants:

1. **Strict Read-Only Baseline Immutability:** Baseline Primavera P6 / MS Project schedules (`baseline_schedule.json`) are read-only references and are **never** modified or overwritten.
2. **Recomputable Derived Progress Layer:** `ExecutionEvent` forms the immutable truth ledger. `ActivityProgress` and `ScheduleProjection` are 100% recomputable calculation layers.
3. **Trust Gate Safeguard Filter:** Only events with `TrustStatus == TRUSTED` (via AI deterministic gating tree or explicit Human Validation decisions) contribute to actual progress aggregation. `REVIEW_REQUIRED`, `UNTRUSTED`, or quarantined events are explicitly excluded and tracked as *"Unverified Progress Claims"*.
4. **Policy-Driven Progress Calculation:** Progress calculation is policy-based (`QUANTITY_BASED`, `MILESTONE_BASED`, `STATUS_BASED`). The formula $P_{\text{phys}} = \frac{Q_{\text{actual}}}{Q_{\text{planned}}}$ is applied **only** to quantity-driven activities with compatible units.

---

## 2. Dynamic Execution & Progress Flow

```
                    FIELD REALITY
                         │
                         ▼
                  EXECUTION EVENTS (Immutable Truth Ledger)
                         │
                         ▼
                EVIDENCE + CONFLICTS
                         │
                         ▼
                  TRUST ASSESSMENT
                         │
                         ▼
                 HUMAN VALIDATION
                         │
                         ▼
              TRUSTED EXECUTION TRUTH
                         │
                         ▼
              ┌─────────────────────┐
              │   PROGRESS LAYER    │  (Recomputable Calculated Layer)
              │                     │
              │ Activity Progress   │
              │ WBS Rollups         │
              │ Forecast Engine     │
              │ Schedule Variance   │
              └─────────────────────┘
                         │
                         ▼
             READ-ONLY BASELINE P6 SCHEDULE
```

---

## 3. Core Engine Rules & Mathematics

### 3.1 Progress Calculation Policies (`ProgressCalculationPolicy`)
- **`QUANTITY_BASED`:** Applied when $Q_{\text{planned}} > 0$ and unit is valid measurement ($m$, $m^3$, $MT$, $Joints$, etc.). $P_{\text{phys}} = \min\left(100.0, \frac{Q_{\text{actual}}}{Q_{\text{planned}}} \times 100\%\right)$.
- **`MILESTONE_BASED`:** Applied when duration is 0 or unit is Milestone. $P_{\text{phys}} = 100.0\%$ if finish event exists, else $50.0\%$ if start event exists, else $0.0\%$.
- **`STATUS_BASED`:** Applied to qualitative tasks. $P_{\text{phys}} = 100.0\%$ if finished, $50.0\%$ if in-progress, $0.0\%$ if not started.

### 3.2 Quantity Aggregation (`QuantityObservationType`)
- **`CUMULATIVE_TOTAL`:** Sequence of total progress observations ($20\text{m} \rightarrow 35\text{m} \rightarrow 50\text{m} \Rightarrow 50\text{m}$).
- **`DAILY_DELTA`:** Sequence of incremental progress claims ($+20\text{m} + 15\text{m} + 15\text{m} \Rightarrow 50\text{m}$).
- **`UNKNOWN`:** Fluctuating or ambiguous quantity claims $\rightarrow$ `ProgressCalculationStatus.CONFLICTED` (no blind summation).

### 3.3 Event Contribution Filtering for Actual Start
`Actual Start` ($AS$) is derived strictly from eligible event types (`START`, `PROGRESS`, `QUANTITY_UPDATE`, `RESUME`). Raw `INSPECTION` or `QA_CLEARANCE` events do not trigger actual start.

### 3.4 Physical Progress vs QA Clearance
Physical work completion ($P_{\text{phys}} = 100\%$) and QA clearance status (`qa_clearance_status`: `CLEARED`, `PENDING`, `NOT_REQUIRED`) remain distinct. Work can be 100% physically complete while QA clearance remains `PENDING`.

### 3.5 Forecast Engine & Null-Forecast Safety (`ForecastStatus`)
Execution rate is calculated from historical observation points:
$$Rate = \frac{\Delta Q}{\Delta t} \quad (\text{units/day})$$
$$RemainingDuration = \left\lceil \frac{Q_{\text{planned}} - Q_{\text{actual}}}{Rate} \right\rceil$$
$$ForecastFinish = AsOfDate + RemainingDuration$$

- If history is insufficient ($< 2$ timestamped quantity points or zero rate), $ForecastFinish = \text{None}$ and `ForecastStatus` is set to `INSUFFICIENT_HISTORY` or `ZERO_RATE`.

### 3.6 Schedule Variance & Baseline Authority
- **Completed Activity:** $SV_{\text{finish}} = ActualFinish - BaselineFinish$ (days).
- **Incomplete Activity:** $SV_{\text{finish}} = ForecastFinish - BaselineFinish$ (days, or `None` if forecast unavailable).
- **Sign Convention:** $+$ = delay (later than baseline), $-$ = ahead of schedule.
- **Critical Activity Projected Delay:** Identified when baseline `is_critical == True` and $SV_{\text{finish}} > 0$. Baseline P6 remains the critical path authority.

---

## 4. Retained Unverified Progress Claims

Events in `REVIEW_REQUIRED`, `UNTRUSTED`, or quarantined states are excluded from actual progress calculations and summarized separately:
$$\text{Unverified Reported Quantity} = \sum Q_{\text{untrusted}}$$
The system reports: *"Contractor reported X, but only Y is supported by trusted execution evidence."*

---

## 5. Domain Models Reference

- [`backend/models/domain_models.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/models/domain_models.py): `ActivityProgress`, `WBSProgress`, `ScheduleProjection`, `ProgressCalculationPolicy`, `QuantityObservationType`, `ProgressCalculationStatus`, `ForecastStatus`, `ProgressWeightPolicy`, `ActivityProgressStatus`, `QAClearanceStatus`.
- [`backend/projection/actual_progress_engine.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/projection/actual_progress_engine.py): Core calculation engine.
- [`backend/projection/projection_service.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/backend/projection/projection_service.py): Projection service orchestrator.
- [`tests/unit/test_schedule_projection.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/tests/unit/test_schedule_projection.py): 17 unit test cases.
- [`tests/integration/test_projection_integration.py`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/tests/integration/test_projection_integration.py): End-to-end integration test.
