/**
 * SATYA Control Tower Dashboard View (Phase 12)
 * High-level project KPIs, progress comparison bar, quick upload, and actionable feed.
 * Pure presentation wrapper around Phase 11 REST endpoints.
 */

import { formatPct, renderPriorityPill, renderTrustBadge } from "../formatters.js";

export class ControlTowerView {
  constructor(apiClient, appState) {
    this.api = apiClient;
    this.state = appState;
  }

  async render(container) {
    container.innerHTML = `
      <div class="card-title" style="margin-bottom: 1rem;">Project Execution Control Tower</div>

      <!-- KPI Summary Cards -->
      <div class="kpi-grid">
        <div class="card">
          <div class="card-title" style="font-size: 0.75rem; color: var(--text-muted);">Trusted Physical Progress</div>
          <div id="kpi-trusted-progress" style="font-size: 1.8rem; font-weight: 800; color: var(--color-trusted); margin-top: 0.2rem;">Loading...</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Backed by verified evidence</div>
        </div>

        <div class="card">
          <div class="card-title" style="font-size: 0.75rem; color: var(--text-muted);">Baseline Scheduled Progress</div>
          <div id="kpi-baseline-progress" style="font-size: 1.8rem; font-weight: 800; color: var(--color-blue); margin-top: 0.2rem;">Loading...</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Read-only schedule authority</div>
        </div>

        <div class="card">
          <div class="card-title" style="font-size: 0.75rem; color: var(--text-muted);">Unverified Progress Claims</div>
          <div id="kpi-unverified-claims" style="font-size: 1.8rem; font-weight: 800; color: var(--color-review); margin-top: 0.2rem;">Loading...</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Reported without trusted evidence</div>
        </div>

        <div class="card">
          <div class="card-title" style="font-size: 0.75rem; color: var(--text-muted);">Pending Reconciliations</div>
          <div id="kpi-pending-recon" style="font-size: 1.8rem; font-weight: 800; color: var(--color-conflicted); margin-top: 0.2rem;">Loading...</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Actionable HITL queue items</div>
        </div>

        <div class="card">
          <div class="card-title" style="font-size: 0.75rem; color: var(--text-muted);">Critical Path Delays</div>
          <div id="kpi-critical-delays" style="font-size: 1.8rem; font-weight: 800; color: var(--color-untrusted); margin-top: 0.2rem;">Loading...</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">Activities with projected delay</div>
        </div>
      </div>

      <!-- Execution Progress Comparison Bar -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div class="card-header">
          <div class="card-title">Execution Truth vs. Reported Claims Comparison</div>
          <div style="font-size: 0.8rem; color: var(--text-muted);">
            Project: <strong id="tower-project-id">${this.state.currentProjectId}</strong>
          </div>
        </div>
        <div style="margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
          Visualizes: <strong>Trusted Execution Progress</strong> (Green) vs. <strong>Unverified Progress Claims</strong> (Amber)
        </div>
        <div class="progress-bar-container">
          <div id="bar-trusted" class="progress-bar-fill" style="width: 0%;"></div>
          <div id="bar-unverified" class="progress-bar-unverified" style="width: 0%;"></div>
          <div id="bar-text" class="progress-bar-text">Loading Progress Data...</div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
        <!-- Quick Field Observation Ingestion Panel -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">Quick Field Observation Ingestion</div>
            <span class="badge badge-blue">REST API Upload</span>
          </div>
          <form id="tower-upload-form">
            <div style="margin-bottom: 0.8rem;">
              <label style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Source Document Type</label>
              <select id="upload-source-type" class="project-select" style="width: 100%;">
                <option value="DPR_EXCEL">DPR_EXCEL (Daily Progress Report)</option>
                <option value="SITE_PHOTO_LOG">SITE_PHOTO_LOG (Inspection Log)</option>
                <option value="VOICE_TRANSCRIPT">VOICE_TRANSCRIPT (Voice Log)</option>
                <option value="CONTRACTOR_SUBMISSION">CONTRACTOR_SUBMISSION (Contractor Update)</option>
              </select>
            </div>
            <div style="margin-bottom: 0.8rem;">
              <label style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Field Raw Observation Text</label>
              <textarea id="upload-content" style="width: 100%; height: 100px; background: var(--bg-dark-input); color: var(--text-main); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.5rem; font-family: var(--font-mono); font-size: 0.85rem;" placeholder="e.g. 2026-09-02: Mainline trench excavation 350m completed on PL-NBG-SEC1 ACT-1010. QA cleared."></textarea>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;">Upload & Process Pipeline</button>
          </form>
          <div id="upload-status" style="margin-top: 0.8rem; font-size: 0.8rem;"></div>
        </div>

        <!-- High-Priority Queue Feed -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">High-Priority Actionable Feed (P1 / P2)</div>
            <button id="btn-refresh-feed" class="btn" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Refresh</button>
          </div>
          <div id="feed-container" style="max-height: 260px; overflow-y: auto;">
            <div style="color: var(--text-muted); font-size: 0.85rem;">Loading queue items...</div>
          </div>
        </div>
      </div>

      <!-- Time Agent Proactive Early Warning Signals Feed (Phase 13) -->
      <div class="card" style="margin-top: 1.5rem;">
        <div class="card-header">
          <div class="card-title">Time Agent Proactive Early-Warning Signals</div>
          <button id="btn-run-monitoring" class="btn btn-primary" style="padding: 0.25rem 0.6rem; font-size: 0.75rem;">Run Time Agent Evaluation</button>
        </div>
        <div id="signals-container" style="max-height: 250px; overflow-y: auto;">
          <div style="color: var(--text-muted); font-size: 0.85rem;">Loading active temporal warning signals...</div>
        </div>
      </div>
    `;

    this.bindEvents(container);
    await this.loadData();
  }

  async loadData() {
    const projId = this.state.currentProjectId;

    // Fetch Projection Data
    const projRes = await this.api.getLatestProjection(projId);
    if (projRes.ok && projRes.data) {
      const p = projRes.data;
      const trustedPct = p.overall_project_progress_pct !== undefined ? p.overall_project_progress_pct : 0.0;
      const baselinePct = p.overall_baseline_progress_pct !== undefined ? p.overall_baseline_progress_pct : 0.0;
      const unverifiedCount = p.unverified_event_count !== undefined ? p.unverified_event_count : 0;
      const criticalDelays = p.critical_activity_delays_count !== undefined ? p.critical_activity_delays_count : 0;

      document.getElementById("kpi-trusted-progress").innerText = formatPct(trustedPct);
      document.getElementById("kpi-baseline-progress").innerText = formatPct(baselinePct);
      document.getElementById("kpi-unverified-claims").innerText = unverifiedCount;
      document.getElementById("kpi-critical-delays").innerText = criticalDelays;

      // Update progress bar
      const barTrusted = document.getElementById("bar-trusted");
      const barUnverified = document.getElementById("bar-unverified");
      const barText = document.getElementById("bar-text");

      if (barTrusted && barUnverified && barText) {
        barTrusted.style.width = `${Math.min(100, trustedPct)}%`;
        barUnverified.style.width = `${Math.min(100 - trustedPct, unverifiedCount * 5)}%`;
        barText.innerText = `Trusted Physical Progress: ${formatPct(trustedPct)} | Unverified Claims: ${unverifiedCount}`;
      }
    }

    // Fetch Monitoring Active Signals (Phase 13)
    const sigRes = await this.api.getActiveSignals(projId);
    const sigContainer = document.getElementById("signals-container");
    if (sigContainer) {
      if (sigRes.ok && sigRes.data && sigRes.data.signals && sigRes.data.signals.length > 0) {
        sigContainer.innerHTML = sigRes.data.signals.map(s => `
          <div style="padding: 0.6rem; border-bottom: 1px solid var(--border-subtle); display: flex; align-items: flex-start; justify-content: space-between;">
            <div>
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.2rem;">
                <span class="badge ${s.severity === 'CRITICAL' || s.severity === 'HIGH' ? 'badge-untrusted' : 'badge-review'}">${s.severity}</span>
                <strong style="font-family: var(--font-mono);">${s.activity_id}</strong>
                <span style="font-size: 0.8rem; font-weight: 700; color: var(--color-blue);">${s.signal_type}</span>
              </div>
              <div style="font-size: 0.8rem; color: var(--text-main); font-weight: 600;">${s.summary}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">💡 Action: ${s.recommended_action}</div>
            </div>
          </div>
        `).join('');
      } else {
        sigContainer.innerHTML = `<div style="color: var(--color-trusted); font-size: 0.85rem; padding: 0.8rem; text-align: center;">✓ Zero active temporal warning signals detected for this project!</div>`;
      }
    } else {
      document.getElementById("kpi-trusted-progress").innerText = "N/A";
      document.getElementById("kpi-baseline-progress").innerText = "N/A";
    }

    // Fetch Queue Data
    const queueRes = await this.api.getQueue(projId);
    if (queueRes.ok && queueRes.data) {
      const q = queueRes.data;
      document.getElementById("kpi-pending-recon").innerText = q.count !== undefined ? q.count : 0;

      const feedContainer = document.getElementById("feed-container");
      if (feedContainer) {
        if (!q.queue_items || q.queue_items.length === 0) {
          feedContainer.innerHTML = `<div style="color: var(--color-trusted); font-size: 0.85rem; padding: 1rem; text-align: center;">✓ Zero pending HITL reviews required for this project!</div>`;
        } else {
          feedContainer.innerHTML = q.queue_items.slice(0, 5).map(item => `
            <div style="padding: 0.6rem; border-bottom: 1px solid var(--border-subtle); display: flex; align-items: center; justify-content: space-between;">
              <div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  ${renderPriorityPill(item.priority)}
                  <span style="font-family: var(--font-mono); font-weight: 700;">${item.event_id}</span>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">${item.trigger_reason}</div>
              </div>
              <button class="btn btn-primary btn-jump-recon" data-event-id="${item.event_id}" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Reconcile</button>
            </div>
          `).join('');
        }
      }
    }
  }

  bindEvents(container) {
    const form = container.querySelector("#tower-upload-form");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const content = container.querySelector("#upload-content").value.trim();
        const sourceType = container.querySelector("#upload-source-type").value;
        const statusDiv = container.querySelector("#upload-status");

        if (!content) {
          statusDiv.innerHTML = `<span style="color: var(--color-untrusted)">Please enter raw field observation text!</span>`;
          return;
        }

        statusDiv.innerHTML = `<span style="color: var(--text-muted)">Processing pipeline via REST API...</span>`;
        const res = await this.api.uploadIngestion({
          project_id: this.state.currentProjectId,
          source_type: sourceType,
          file_name: "tower_upload.txt",
          content: content
        });

        if (res.ok && res.data) {
          statusDiv.innerHTML = `<span style="color: var(--color-trusted)">✓ Successfully ingested Source ID ${res.data.source_id}! Extracted ${res.data.events_extracted_count} events (${res.data.quarantined_count} quarantined).</span>`;
          container.querySelector("#upload-content").value = "";
          await this.loadData();
        } else {
          statusDiv.innerHTML = `<span style="color: var(--color-untrusted)">✕ Error: ${res.data?.error?.message || "Failed to ingest"}</span>`;
        }
      });
    }

    const btnRefresh = container.querySelector("#btn-refresh-feed");
    if (btnRefresh) {
      btnRefresh.addEventListener("click", () => this.loadData());
    }

    const btnRunMon = container.querySelector("#btn-run-monitoring");
    if (btnRunMon) {
      btnRunMon.addEventListener("click", async () => {
        btnRunMon.innerText = "Evaluating...";
        await this.api.evaluateMonitoring(this.state.currentProjectId);
        await this.loadData();
        btnRunMon.innerText = "Run Time Agent Evaluation";
      });
    }

    container.addEventListener("click", (e) => {
      if (e.target.classList.contains("btn-jump-recon")) {
        const eventId = e.target.getAttribute("data-event-id");
        this.state.setView("reconciliation");
        window.dispatchEvent(new CustomEvent("satya:jump_recon", { detail: { eventId } }));
      }
    });
  }
}
