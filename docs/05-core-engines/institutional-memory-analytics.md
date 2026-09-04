# SATYA Core Engine: Institutional Memory & Empirical Analytics

> **Document Status:** Canonical Core Engine Specification  
> **Governance Reference:** Phase 14  
> **Repository:** SATYA (Schedule-Aligned Truth & Yield Analytics) — Oil India Limited (SIH 2026)  

---

## 1. Executive Summary & Core Philosophy

The **Institutional Memory & Empirical Analytics Engine** serves as SATYA's evidence-backed self-improvement and empirical performance analysis layer. It captures planner domain knowledge, analyzes historical execution rates, tracks contractor reporting verifiability, and synthesizes conflict resolution patterns across pipeline executions.

### Core Architectural Principle

$$\text{Learn from History} \longrightarrow \text{Expose Explicit Knowledge} \longrightarrow \text{Assist Future Decisions}$$

**NOT:**

$$\text{Learn from History} \longrightarrow \text{Silently Rewrite Historical System Records}$$

1. **Auditable & Versioned:** Knowledge promotion requires explicit planner confirmation thresholds and preserves complete provenance traces.
2. **Project-Scoped:** Terminology aliases and productivity rate benchmarks are bound to explicit `project_id` contexts; global aliases across distinct oilfield projects are strictly deferred.
3. **Future-Facing Immutability:** Memory distillation affects future candidate retrieval scoring ($S_{\text{alias}}$ factor boost) only. Historical `MatchResult`, `TrustAssessment`, `ValidationDecision`, `ScheduleProjection`, and `ExecutionEvent` records are 100% immutable and cannot be rewritten retroactively.
4. **Safety Gated:** Additive alias retrieval ($S_{\text{alias}}$) can never bypass closed baseline schedule candidate vocabulary or match safety thresholds ($\theta_{\text{match}}$).

---

## 2. Terminology Memory & Alias Promotion Lifecycle

Raw field execution text (e.g., DPR notes, contractor logs) frequently contains informal jargon, site acronyms, or non-standard operational descriptions (e.g., "HDD trenchless drilling", "hydrotesting at km 14"). The Institutional Memory engine distills human planner corrections into versioned `TerminologyAliasRecord` items.

### 2.1 Promotion Lifecycle State Machine

```
              ┌──────────────────────────┐
              │     Planner Correction   │
              └────────────┬─────────────┘
                           │ 1st Correction
                           ▼
              ┌──────────────────────────┐
              │   AliasStatus.CANDIDATE  │ (Ineligible for candidate retrieval)
              └────────────┬─────────────┘
                           │ Repeated confirmations
                           │ N_planners >= min_candidate_confirmations
                           ▼
              ┌──────────────────────────┐
              │   AliasStatus.VALIDATED  │ (Provisional additive S_alias boost)
              └────────────┬─────────────┘
                           │ Confidence >= 0.80 & multi-source
                           ▼
              ┌──────────────────────────┐
              │    AliasStatus.ACTIVE    │ (Full additive S_alias boost)
              └────────────┬─────────────┘
                           │ Planner Re-override / Superseded
                           ▼
              ┌──────────────────────────┐
              │  AliasStatus.SUPERSEDED │ (Inactivated / Version Increment)
              └──────────────────────────┘
```

### 2.2 Deterministic Alias Confidence Formula

To avoid frequency-only bias, alias confidence score $C_{\text{alias}}$ is calculated via a multi-factor clamped formula parameterizable via `InstitutionalMemoryPolicy`:

$$C_{\text{alias}} = \text{clamp}\left( w_{\text{plan}} \cdot N_{\text{planners}} + w_{\text{src}} \cdot N_{\text{sources}} + R(\Delta t) - w_{\text{over}} \cdot N_{\text{reoverrides}},\, 0.0,\, 1.0 \right)$$

where:
* $N_{\text{planners}}$: Number of distinct human planners who confirmed this mapping.
* $N_{\text{sources}}$: Number of independent source documents where this phrase occurred.
* $R(\Delta t) = 0.5^{\frac{\Delta t}{T_{1/2}}}$: Exponential recency decay function ($T_{1/2} = 90$ days default).
* $N_{\text{reoverrides}}$: Number of subsequent planner re-overrides demoting/changing this phrase mapping.
* Default weights: $w_{\text{plan}} = 0.3$, $w_{\text{src}} = 0.2$, $w_{\text{over}} = 0.4$.

---

## 3. Matching Engine Integration ($S_{\text{alias}}$ Factor)

When active aliases exist for a project, `ScheduleAwareMatchingEngine` evaluates candidate activity matches by extending the non-ID score with an additive alias boost factor $S_{\text{alias}}$:

$$S_{\text{non\_id\_boosted}} = S_{\text{non\_id}} + 0.15 \cdot S_{\text{alias}}$$

### Operational Safety Constraints
1. **Additive Retrieval Only:** $S_{\text{alias}}$ provides a factor boost during candidate scoring; it NEVER bypasses candidate vocabulary filtering.
2. **Vocabulary Enforcement:** All candidate activity targets MUST exist in the imported schedule baseline vocabulary.
3. **Threshold Preserved:** The overall match threshold ($\theta_{\text{match}} = 0.80$) and ambiguity margin ($\Delta \ge 0.08$) remain strictly enforced.

---

## 4. Execution Rate Analytics

Empirical progress and productivity analytics calculate baseline vs actual execution rates grouped by `(project_id, wbs_id, activity_type, unit_of_measure, quantity_basis)`.

### 4.1 Unit of Measure & Basis Safety
Rate benchmarks strictly aggregate observations sharing identical Units of Measure (UOM) and quantity bases (e.g., `DAILY_DELTA` vs `CUMULATIVE_TOTAL`). Mixed UOM aggregations are rejected to prevent invalid rate math.

### 4.2 Sample Size Qualification (`BenchmarkStatus`)

To prevent small sample distortion, statistical metrics (Mean, P50, P90) are qualified by explicit sample size thresholds:

$$\text{Status} = \begin{cases}
\text{INSUFFICIENT\_SAMPLE} & \text{if } N < 3 \quad (\text{P50/P90 set to } \text{None}) \\
\text{PROVISIONAL} & \text{if } 3 \le N < 10 \quad (\text{Provisional analytics}) \\
\text{VALIDATED} & \text{if } N \ge 10 \quad (\text{Statistically robust P50/P90})
\end{cases}$$

### 4.3 Planned Rate Methodology
Planned rate is derived as:

$$\text{Planned Rate} = \frac{\text{Planned Quantity}}{\text{Baseline Duration Days}}$$

If planned quantity or duration is absent, `planned_rate` returns `None` rather than coercing to zero.

---

## 5. Contractor Reporting & Verification Profile

The **Contractor Reporting & Verification Profile** evaluates contractor field reporting verifiability and submission timeliness. It is explicitly framed as an operational reporting quality scorecard—NOT a contractor performance rating.

### Profile Metrics
* **Verification Ratio:** $\frac{N_{\text{trusted\_events}}}{N_{\text{total\_events}}}$
* **Average Reporting Latency:** $\text{Mean}(t_{\text{reported}} - t_{\text{observed}})$. Evaluated only when both observed timestamp and source report submission timestamp exist; returns `None` when timestamp data is incomplete.
* **Nullable Contractor Identifier:** Supports `None` for unassigned or general site observation documents.

---

## 6. Conflict & Warning Resolution Patterns

Analyzes historical resolution pathways for field evidence conflicts (e.g., `QA_CONFLICT`, `LOCATION_MISMATCH`) and Time Agent warning signals (`SILENT_CRITICAL_PATH_RISK`, `REPORTING_LATENCY_STALENESS`).

### Separation of Acknowledgment vs Physical Resolution
* **Acknowledged Count:** Captures Time Agent warnings acknowledged by planners for monitoring without state changes.
* **Resolved Count:** Captures underlying physical condition resolutions or HITL decision closures.
* **Resolution Pathways:** Tracks distribution across `VALIDATED`, `REMAPPED` (CHANGE_MATCH), and `REJECTED` planner decisions.

---

## 7. Data Models & API Surface

### 7.1 Key REST Endpoints (`/api/v1/memory/*` & `/api/v1/analytics/*`)
* `POST /api/v1/memory/projects/{project_id}/distill`: Triggers memory distillation run for planner corrections.
* `GET /api/v1/memory/projects/{project_id}/aliases`: Returns versioned terminology alias records.
* `GET /api/v1/analytics/projects/{project_id}/productivity`: Returns empirical execution rate benchmarks.
* `GET /api/v1/analytics/projects/{project_id}/contractors`: Returns contractor reporting verifiability profiles.
* `GET /api/v1/analytics/projects/{project_id}/conflicts`: Returns conflict and warning resolution pattern analytics.

---

## 8. Verification & Test Coverage

Phase 14 is backed by comprehensive unit and integration test suites:
* `tests/unit/test_institutional_memory.py`: Tests alias candidate creation, promotion state transitions, same-planner isolation, project isolation, distillation reproducibility, and historical match immutability.
* `tests/unit/test_execution_analytics.py`: Tests rate benchmarks, UOM compatibility, sample size gating, null planned rate handling, reporting latency calculation, and signal acknowledgment/resolution separation.
* `tests/integration/test_analytics_integration.py`: Tests complete end-to-end REST API lifecycle from DPR upload and HITL correction through memory distillation and analytics retrieval.
