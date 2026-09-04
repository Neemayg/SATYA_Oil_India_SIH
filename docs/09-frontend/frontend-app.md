# SATYA — Frontend Planner Dashboard & HITL Interface Specification
**Document Reference:** `docs/09-frontend/frontend-app.md`  
**Active Phase:** Phase 12 — Frontend Planner Dashboard & HITL Interface (🟢 APPROVED & CLOSED)

---

## 1. Executive Summary

Phase 12 delivers the web application for SATYA, providing Oil India project planners and managers an interactive **Execution Truth Layer** console over the Phase 5–10 backend engines via the Phase 11 REST API.

```
Client (Phase 12 Frontend Web App)
  │
  ├── Control Tower Dashboard
  ├── Reconciliation Desk (HITL Centerpiece)
  ├── Evidence & Provenance Center
  └── Schedule Explorer (SATYA Overlay)
  │
  ▼ HTTP REST API (Phase 11)
  http://127.0.0.1:8000/api/v1
```

---

## 2. Core Architectural Principles & Directives

1. **REST API Transport Consumer:** The frontend application communicates exclusively with Phase 11 REST API endpoints (`http://127.0.0.1:8000/api/v1`). It **never** accesses SQLite directly, **never** calculates domain-level metrics in JavaScript, **never** mutates domain models outside API endpoints, and **never** alters baseline schedule files.
2. **Zero-CDN Offline Web Stack:** Built with native system font stacks (`font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`) and inline SVG icons. Requires **zero external CDN links**, ensuring 100% offline functionality during SIH hackathon presentation.
3. **No-Fabrication / Data Honesty Directive:** The frontend **never** invents or fabricates missing backend data to look visually complete. Missing fields display `NOT AVAILABLE` / `N/A`.
4. **Distinct Multi-Layer State Representation:** Preserves distinct layers:
   $$\text{Match Outcome} \neq \text{Evidence Support} \neq \text{Conflict Severity} \neq \text{Trust Status} \neq \text{Planner Decision}$$
   Surfaces explicit *"Why SATYA believes this?"* factor breakdowns everywhere (`✓` for supported factors, `⚠` for weak/missing factors).
5. **REST Snapshot Lock Concurrency (HTTP 409 Conflict):** Displays `Trust Assessment v(N)` version index. If a `409 Conflict` (`STALE_REVIEW_STATE`) occurs on decision submit, an alert banner (*"⚠ Review state changed by another process"*) and an explicit `[Refresh Review]` button are shown. Active review items are **never** silently auto-refreshed.
6. **High-Density Engineering Console Design:** Styled with a dark slate palette (`#0F172A` Slate Dark) prioritizing visual data tables, crisp badges, and visual evidence data over visual noise.

---

## 3. View Component Architecture

| View | Path / Component | Description |
|---|---|---|
| **Control Tower** | `frontend/js/views/control_tower.js` | High-level project KPIs, Trusted Progress vs Unverified Claims bar, Quick DPR text upload, Actionable Feed |
| **Reconciliation Desk** | `frontend/js/views/reconciliation_desk.js` | HITL Centerpiece with 6-step visual hierarchy & snapshot locked decision form |
| **Evidence Center** | `frontend/js/views/evidence_center.js` | Complete end-to-end provenance trace visualizer (`GET /api/v1/evidence/events/{id}/trace`) |
| **Schedule Explorer** | `frontend/js/views/schedule_explorer.js` | WBS & activity table overlaid with SATYA truth (Actual/Forecast dates, Physical %, QA Status, Trust Status, Finish Variance) |

---

## 4. Verification & Testing

The Phase 12 implementation has been verified with 82 automated tests (69 unit tests, 13 integration tests):
- `tests/unit/test_api_endpoints.py`: Verifies `GET /api/v1/evidence/events/{event_id}/trace` read-model trace endpoint.
- `tests/unit/test_api_hitl_concurrency.py`: Verifies `409 Conflict` on stale `reviewed_trust_version`.
- `tests/integration/test_api_integration.py`: Verifies complete end-to-end flow from REST ingestion to projection generation.
