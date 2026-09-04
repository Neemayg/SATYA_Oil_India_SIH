# SATYA Live Demo Operator Runbook & Failure Recovery Guide

**Repository:** SATYA (Schedule-Aligned Truth & Yield Analytics) — Oil India Limited (SIH 2026)  
**Document Path:** `docs/11-sih/demo_runbook.md`  
**Purpose:** Step-by-step technical operator checklist, environment preparation, live click sequence, and emergency failure recovery procedures for the SIH 2026 presentation team.

---

## 1. Environment & Pre-Demo Operator Checklist (T-15 Minutes)

### Environment Setup Commands
Execute terminal commands from repository root (`/Users/neemaysmac/Desktop/OIL_India_SIH`):

1. **Verify Python Environment**:
   ```bash
   python3 --version
   # Expected: Python 3.10+
   ```

2. **Verify Full Test Suite Regression**:
   ```bash
   python3 -m pytest tests/ -q --tb=no
   # Expected: 134 passed in ~18s
   ```

3. **Start SATYA REST API Server**:
   ```bash
   python3 backend/api/app.py
   # Or run dev server script:
   python3 scripts/run_server.py
   ```

4. **Verify Health Endpoint**:
   ```bash
   curl http://localhost:8000/api/v1/health
   # Expected Output: {"status":"UP","version":"0.17.0","timestamp":"..."}
   ```

5. **Prepare Chrome Browser Window**:
   - Open Google Chrome.
   - Navigate to `http://localhost:8000`.
   - Set Chrome zoom level to **110%** for maximum visual clarity on presentation screen.
   - Open Chrome DevTools Console (in case quick log inspection is needed).

---

## 2. Live Demo Click Sequence (Step-by-Step)

| Time | Target UI Tab | Operator Action | Expected Screen Output |
| :---: | :--- | :--- | :--- |
| `02:15` | **Field Capture / Ingestion** | Click text box. Paste raw snippet from `demo_data.md` (`SRC-DEMO-001`). | Raw DPR text displayed in input card. |
| `02:40` | **Field Capture / Ingestion** | Click **Submit Payload**. | Ingestion summary banner: 3 Execution Events extracted (`EVT-DEMO-101`, `102`, `103`). |
| `05:10` | **Reconciliation Desk** | Click Reconciliation Desk tab. Select Event `EVT-DEMO-101`. | Hero UI displays Field Claim, Candidate `ACT-1020` (Score: 0.42), and Factor Breakdown. |
| `07:15` | **Reconciliation Desk** | Click candidate `ACT-1020`. Select `CHANGE_MATCH`, Reason `TERMINOLOGY_ALIAS`. Type notes. | Confirmation modal pops up. |
| `08:15` | **Reconciliation Desk** | Click **Confirm Decision**. | Status updates to `TRUSTED` ($v2$). Ledger audit entry generated. |
| `08:40` | **Analytics & Memory** | Click Analytics & Memory tab. Select Project `PRJ-NBG-2026`. | Terminology Alias table displays `"hdd section 3" \(\rightarrow\) ACT-1020` as `CANDIDATE`. |
| `09:35` | **Schedule Projections** | Click Schedule Projections tab. Click **Generate Projection**. | Table updates: `ACT-1020` shows 93.3% progress (420m/450m), finish date 2026-09-09 (+3d variance). |
| `10:15` | **Time Agent Warnings** | Click Time Agent Warnings tab. | Card displays 2 active warnings: `FORECAST_FINISH_SLIPPAGE` & `QA_CLEARANCE_BOTTLENECK`. |

---

## 3. Emergency Failure Recovery Procedures

If a live presentation failure occurs (e.g. laptop restart, browser freeze, server crash), execute one of the following recovery paths immediately:

### Recovery Path A: Local REST Server Crash (10 Seconds)
If the backend REST server crashes during demo:
1. Open terminal window (kept minimized on screen 2).
2. Relaunch server:
   ```bash
   python3 backend/api/app.py
   ```
3. Refresh Chrome tab (`http://localhost:8000`).
4. Resume presentation from current step.

### Recovery Path B: Pre-Seeded State Recovery (5 Seconds)
If live ingestion fails due to unexpected input formatting:
1. Navigate browser URL directly to:
   ```
   http://localhost:8000/index.html?demo_mode=seeded
   ```
2. The UI will instantly load pre-seeded SQLite database records for `PRJ-NBG-2026`.
3. Proceed directly to **Reconciliation Desk** or **Schedule Projections**.

### Recovery Path C: Complete System / Network Failure (Offline Fallback)
If hardware failure prevents running code entirely:
1. Switch to Slide Deck ([`presentation_deck.md`](file:///Users/neemaysmac/Desktop/OIL_India_SIH/docs/11-sih/presentation_deck.md)).
2. Slide 7 contains high-resolution pre-rendered screenshot mockups of the Reconciliation Desk UI, Candidate Factor Breakdown, and Time Agent warning cards.
3. Deliver narration seamlessly using Slide 7 and Slide 8 visuals.
