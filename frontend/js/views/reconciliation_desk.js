/**
 * SATYA Reconciliation Desk View (Phase 12)
 * The visual centerpiece of SATYA.
 * 6-Step Visual Hierarchy: Field Observation -> Execution Event -> Schedule Match Candidates -> Evidence & Conflicts -> Trust Outcome -> Planner Decision Form.
 * REST Snapshot Lock (reviewed_trust_version) with HTTP 409 Conflict alert banner and [Refresh Review] action.
 */

import {
  renderTrustBadge,
  renderMatchOutcomeBadge,
  renderPriorityPill,
  renderFactorBreakdown,
  renderQAClearanceBadge,
  formatPct,
  formatDate
} from "../formatters.js";

export class ReconciliationDeskView {
  constructor(apiClient, appState) {
    this.api = apiClient;
    this.state = appState;
    this.currentQueueItems = [];
    this.selectedItem = null;
    this.traceData = null;
    this.staleStateAlert = false;
  }

  async render(container) {
    container.innerHTML = `
      <div class="reconciliation-grid">
        <!-- Left Sidebar: Prioritized Queue -->
        <div class="queue-sidebar">
          <div class="queue-header">
            <span style="font-weight: 700; font-size: 0.85rem;">REVIEW QUEUE</span>
            <select id="queue-priority-filter" class="project-select" style="font-size: 0.75rem; padding: 0.2rem 0.4rem;">
              <option value="">ALL PRIORITIES</option>
              <option value="P1_CRITICAL">P1 CRITICAL</option>
              <option value="P2_HIGH">P2 HIGH</option>
              <option value="P3_MEDIUM">P3 MEDIUM</option>
              <option value="P4_LOW">P4 LOW</option>
            </select>
          </div>
          <div id="queue-list" class="queue-list">
            <div style="padding: 1rem; color: var(--text-muted); font-size: 0.85rem;">Loading queue...</div>
          </div>
        </div>

        <!-- Center Workspace: 6-Step Hierarchy -->
        <div id="workspace-container" class="workspace-detail">
          <div class="card" style="text-align: center; padding: 3rem; color: var(--text-muted);">
            Select an actionable queue item from the left sidebar to open the Reconciliation Workspace.
          </div>
        </div>
      </div>
    `;

    this.bindEvents(container);
    await this.loadQueue();
  }

  async loadQueue(priorityFilter = null) {
    const projId = this.state.currentProjectId;
    const res = await this.api.getQueue(projId, priorityFilter);

    const listDiv = document.getElementById("queue-list");
    if (!listDiv) return;

    if (res.ok && res.data && res.data.queue_items) {
      this.currentQueueItems = res.data.queue_items;
      if (this.currentQueueItems.length === 0) {
        listDiv.innerHTML = `<div style="padding: 1rem; color: var(--color-trusted); font-size: 0.85rem; text-align: center;">✓ Queue Empty. Zero actionable items require planner review for this project.</div>`;
        document.getElementById("workspace-container").innerHTML = `
          <div class="card" style="text-align: center; padding: 3rem; color: var(--color-trusted);">
            ✓ All execution events for <strong>${projId}</strong> are fully reconciled and trusted.
          </div>
        `;
        return;
      }

      listDiv.innerHTML = this.currentQueueItems.map(item => `
        <div class="queue-item ${this.selectedItem && this.selectedItem.queue_item_id === item.queue_item_id ? 'active' : ''}" data-queue-id="${item.queue_item_id}">
          <div class="queue-item-meta">
            ${renderPriorityPill(item.priority)}
            <span class="queue-item-id">${item.event_id}</span>
          </div>
          <div class="queue-item-reason">${item.trigger_reason}</div>
          <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-dim); margin-top: 0.3rem;">
            <span>Match: ${(item.match_confidence * 100).toFixed(0)}%</span>
            <span>Trust ver: v${item.latest_trust_version}</span>
          </div>
        </div>
      `).join('');

      // Auto-select first item if none selected
      if (!this.selectedItem && this.currentQueueItems.length > 0) {
        await this.selectItem(this.currentQueueItems[0]);
      }
    } else {
      listDiv.innerHTML = `<div style="padding: 1rem; color: var(--color-untrusted); font-size: 0.85rem;">Failed to load queue. ${res.data?.error?.message || ""}</div>`;
    }
  }

  async selectItem(item) {
    this.selectedItem = item;
    this.staleStateAlert = false;

    // Highlight active item in list
    document.querySelectorAll(".queue-item").forEach(el => {
      if (el.getAttribute("data-queue-id") === item.queue_item_id) {
        el.classList.add("active");
      } else {
        el.classList.remove("active");
      }
    });

    // Fetch full trace data via API
    const traceRes = await this.api.getEventTrace(item.event_id);
    if (traceRes.ok && traceRes.data) {
      this.traceData = traceRes.data;
    } else {
      this.traceData = null;
    }

    // Fetch candidate matches via API
    const matchRes = await this.api.getEventMatches(item.event_id);
    const matchesData = matchRes.ok ? matchRes.data : null;

    // Fetch schedule fingerprints vocabulary for Rule 5 dropdown
    const vocabRes = await this.api.searchFingerprints("");
    const fingerprints = vocabRes.ok && vocabRes.data ? vocabRes.data.results : [];

    this.renderWorkspace(item, this.traceData, matchesData, fingerprints);
  }

  renderWorkspace(item, trace, matches, fingerprints) {
    const container = document.getElementById("workspace-container");
    if (!container) return;

    const ev = trace?.execution_event || {};
    const src = trace?.source_document || {};
    const ta = trace?.latest_trust_assessment || {};
    const claims = trace?.claims || [];
    const conflicts = trace?.conflicts || [];
    const ea = trace?.evidence_assessment || {};
    const mr = matches || {};

    const latestTrustVer = ta.version_index || item.latest_trust_version || 1;
    const matchId = mr.match_id || "MTH-1";
    const eaId = ea.assessment_id || "EVA-1";

    container.innerHTML = `
      <!-- Stale State Alert Banner -->
      ${this.staleStateAlert ? `
        <div class="alert-banner alert-warning">
          <div>
            <strong>⚠ Review State Changed:</strong> This event was updated by another process or planner while you were reviewing it. Your decision was not submitted.
          </div>
          <button id="btn-stale-refresh" class="btn btn-warning" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;">Refresh Review</button>
        </div>
      ` : ''}

      <!-- Header Workspace Info -->
      <div style="display: flex; align-items: center; justify-content: space-between; background: var(--bg-dark-surface); padding: 0.8rem 1rem; border: 1px solid var(--border-color); border-radius: 8px;">
        <div style="display: flex; align-items: center; gap: 0.8rem;">
          <span style="font-family: var(--font-mono); font-size: 1.1rem; font-weight: 800;">${item.event_id}</span>
          ${renderTrustBadge(ta.trust_status || "REVIEW_REQUIRED")}
          ${renderPriorityPill(item.priority)}
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">
          Snapshot Version: <strong style="color: var(--color-blue)">v${latestTrustVer}</strong> | Trigger: <strong>${item.trigger_reason}</strong>
        </div>
      </div>

      <!-- STEP A: FIELD OBSERVATION -->
      <div class="recon-step-card">
        <div class="recon-step-header">
          <div class="recon-step-title">STEP A. FIELD OBSERVATION (RAW SOURCE EVIDENCE)</div>
          <span class="badge badge-neutral">Source ID: ${ev.source_id || "N/A"}</span>
        </div>
        <div class="recon-step-body">
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.6rem;">
            <div>Author: <strong style="color: var(--text-main);">${src.author || "N/A"}</strong></div>
            <div>Source Type: <strong style="color: var(--text-main);">${src.source_type || "N/A"}</strong></div>
            <div>Observed Date: <strong style="color: var(--text-main);">${formatDate(ev.observed_timestamp)}</strong></div>
          </div>
          <div style="background: var(--bg-dark-input); padding: 0.75rem; border-radius: 6px; border: 1px solid var(--border-subtle); font-family: var(--font-mono); font-size: 0.85rem; color: #F1F5F9;">
            "${src.raw_content || ev.extracted_statement || "Raw source snippet not available"}"
          </div>
        </div>
      </div>

      <!-- STEP B: EXTRACTED EXECUTION EVENT -->
      <div class="recon-step-card">
        <div class="recon-step-header">
          <div class="recon-step-title">STEP B. EXTRACTED EXECUTION EVENT</div>
          <span class="badge badge-neutral">Event Type: ${ev.event_type || "N/A"}</span>
        </div>
        <div class="recon-step-body">
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; font-size: 0.85rem;">
            <div class="factor-card">
              <div class="factor-name">Discipline</div>
              <div class="factor-val">${ev.discipline || "NOT AVAILABLE"}</div>
            </div>
            <div class="factor-card">
              <div class="factor-name">Observed Quantity</div>
              <div class="factor-val">${ev.observed_quantity !== null && ev.observed_quantity !== undefined ? `${ev.observed_quantity} ${ev.unit_of_measure || ''}` : "NOT AVAILABLE"}</div>
            </div>
            <div class="factor-card">
              <div class="factor-name">Raw Activity ID Ref</div>
              <div class="factor-val">${ev.raw_observed_activity_id || "NONE"}</div>
            </div>
            <div class="factor-card">
              <div class="factor-name">Pending QA Clearance</div>
              <div class="factor-val">${ev.pending_qa_clearance ? "YES (Pending)" : "NO"}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- STEP C: SCHEDULE RECONCILIATION & CANDIDATE MATCHES -->
      <div class="recon-step-card">
        <div class="recon-step-header">
          <div class="recon-step-title">STEP C. SCHEDULE RECONCILIATION & CANDIDATE MATCHES</div>
          ${renderMatchOutcomeBadge(mr.outcome || "UNMATCHED")}
        </div>
        <div class="recon-step-body">
          <div style="margin-bottom: 0.8rem; font-size: 0.85rem;">
            <strong>Schedule Match Confidence:</strong> <span style="font-size: 1.1rem; font-weight: 800; color: var(--color-blue);">${((mr.confidence_score || 0) * 100).toFixed(0)}%</span>
            <span style="color: var(--text-muted); margin-left: 1rem;">Selected Target Activity: <strong>${mr.selected_activity_id || "UNMATCHED"}</strong></span>
          </div>

          <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); margin-top: 0.5rem; text-transform: uppercase;">"Why SATYA Believes This Match?" (Factor Scores Breakdown):</div>
          ${renderFactorBreakdown(mr.factor_breakdown)}

          ${mr.candidate_matches && mr.candidate_matches.length > 0 ? `
            <div style="margin-top: 0.8rem;">
              <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.3rem;">Top Candidate Schedule Activities:</div>
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Activity ID</th>
                    <th>Activity Name</th>
                    <th>WBS Path</th>
                    <th>Match Score</th>
                  </tr>
                </thead>
                <tbody>
                  ${mr.candidate_matches.map(c => `
                    <tr>
                      <td style="font-family: var(--font-mono); font-weight: 700;">${c.activity_id}</td>
                      <td>${c.activity_name}</td>
                      <td style="font-size: 0.75rem; color: var(--text-muted);">${c.wbs_name_path}</td>
                      <td style="font-weight: 700; color: var(--color-blue);">${((c.scores?.overall_confidence_score || 0) * 100).toFixed(0)}%</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : ''}
        </div>
      </div>

      <!-- STEP D: EVIDENCE & CONFLICTS -->
      <div class="recon-step-card">
        <div class="recon-step-header">
          <div class="recon-step-title">STEP D. EVIDENCE CLAIMS & CONFLICT FLAGS</div>
          <span class="badge ${conflicts.length > 0 ? 'badge-untrusted' : 'badge-trusted'}">${conflicts.length} Conflicts Flagged</span>
        </div>
        <div class="recon-step-body">
          <!-- Claims List -->
          <div style="margin-bottom: 0.8rem;">
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.3rem;">Extracted Atomic Claims:</div>
            ${claims.length > 0 ? `
              <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                ${claims.map(c => `
                  <div style="background: var(--bg-dark-input); border: 1px solid var(--border-subtle); padding: 0.4rem 0.7rem; border-radius: 4px; font-size: 0.8rem;">
                    <strong>${c.claim_type}:</strong> ${c.raw_statement} (Confidence: ${(c.confidence * 100).toFixed(0)}%)
                  </div>
                `).join('')}
              </div>
            ` : `<div style="color: var(--text-muted); font-size: 0.8rem;">No evidence claims extracted.</div>`}
          </div>

          <!-- Conflicts List -->
          ${conflicts.length > 0 ? `
            <div>
              <div style="font-size: 0.75rem; font-weight: 700; color: var(--color-untrusted); text-transform: uppercase; margin-bottom: 0.3rem;">Detected Execution Conflicts:</div>
              ${conflicts.map(c => `
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid var(--color-untrusted); padding: 0.6rem; border-radius: 6px; margin-bottom: 0.4rem; font-size: 0.8rem;">
                  <strong style="color: var(--color-untrusted);">${c.conflict_type} (${c.severity}):</strong> ${c.description}
                </div>
              `).join('')}
            </div>
          ` : `<div style="color: var(--color-trusted); font-size: 0.8rem;">✓ Zero execution conflicts detected.</div>`}
        </div>
      </div>

      <!-- STEP E: TRUST OUTCOME -->
      <div class="recon-step-card">
        <div class="recon-step-header">
          <div class="recon-step-title">STEP E. TRUST OUTCOME & GATING RATIONALE</div>
          ${renderTrustBadge(ta.trust_status || "REVIEW_REQUIRED")}
        </div>
        <div class="recon-step-body">
          <div style="font-size: 0.85rem; color: var(--text-main);">
            Gating Trigger: <strong>${ta.gating_trigger || "INITIAL_REVIEW"}</strong>
          </div>
          ${ta.rationale_breakdown && ta.rationale_breakdown.primary_reason ? `
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;">
              Primary Rationale: <em>${ta.rationale_breakdown.primary_reason}</em>
            </div>
          ` : ''}
        </div>
      </div>

      <!-- STEP F: PLANNER DECISION FORM (SNAPSHOT LOCKED) -->
      <div class="recon-step-card" style="border: 2px solid var(--color-blue);">
        <div class="recon-step-header" style="background: rgba(59, 130, 246, 0.15);">
          <div class="recon-step-title" style="color: var(--color-blue);">STEP F. PLANNER VALIDATION DECISION FORM (SNAPSHOT LOCKED)</div>
          <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-main);">Snapshot Version: v${latestTrustVer}</span>
        </div>
        <div class="recon-step-body">
          <form id="hitl-decision-form">
            <input type="hidden" id="form-event-id" value="${item.event_id}" />
            <input type="hidden" id="form-reviewed-ver" value="${latestTrustVer}" />
            <input type="hidden" id="form-match-id" value="${matchId}" />
            <input type="hidden" id="form-ea-id" value="${eaId}" />

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
              <div>
                <label style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Validation Action</label>
                <select id="form-decision-type" class="project-select" style="width: 100%;">
                  <option value="VALIDATE">VALIDATE (Confirm SATYA Trust Assessment)</option>
                  <option value="CHANGE_MATCH">CHANGE_MATCH (Re-map to different schedule activity)</option>
                  <option value="REJECT">REJECT (Mark Event as Untrusted)</option>
                  <option value="REQUEST_EVIDENCE">REQUEST_EVIDENCE (Flag missing QA/evidence requirement)</option>
                  <option value="DEFER">DEFER (Postpone decision for site verification)</option>
                </select>
              </div>

              <div>
                <label style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Select Valid Project Activity (Schedule Baseline Constraint)</label>
                <select id="form-activity-id" class="project-select" style="width: 100%;">
                  <option value="">-- Keep Current Selected Target (${mr.selected_activity_id || 'UNMATCHED'}) --</option>
                  ${fingerprints.map(f => `
                    <option value="${f.activity_id}">${f.activity_id} - ${f.activity_name} (${f.wbs_name_path})</option>
                  `).join('')}
                </select>
              </div>
            </div>

            <div style="margin-bottom: 1rem;">
              <label style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Override Reason Category</label>
              <select id="form-override-category" class="project-select" style="width: 100%;">
                <option value="EXPLICIT_ID_CORRECTION">EXPLICIT_ID_CORRECTION</option>
                <option value="SITE_OBSERVATION_VERIFIED">SITE_OBSERVATION_VERIFIED</option>
                <option value="EVIDENCE_MANUALLY_VERIFIED">EVIDENCE_MANUALLY_VERIFIED</option>
                <option value="QA_CLEARANCE_CONFIRMED">QA_CLEARANCE_CONFIRMED</option>
                <option value="OTHER">OTHER</option>
              </select>
            </div>

            <div style="margin-bottom: 1rem;">
              <label style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Planner Review Notes & Justification</label>
              <textarea id="form-reason-notes" style="width: 100%; height: 70px; background: var(--bg-dark-input); color: var(--text-main); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.5rem; font-family: var(--font-mono); font-size: 0.85rem;" placeholder="Enter explicit planner review rationale..."></textarea>
            </div>

            <div style="display: flex; gap: 0.75rem;">
              <button type="submit" class="btn btn-primary" style="flex: 1;">Submit Decision (Enforce Snapshot Lock v${latestTrustVer})</button>
            </div>
          </form>
          <div id="form-result-status" style="margin-top: 0.8rem; font-size: 0.85rem;"></div>
        </div>
      </div>
    `;

    this.bindFormEvents(container, item);
  }

  bindFormEvents(container, item) {
    const btnStale = container.querySelector("#btn-stale-refresh");
    if (btnStale) {
      btnStale.addEventListener("click", () => this.selectItem(item));
    }

    const form = container.querySelector("#hitl-decision-form");
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const eventId = container.querySelector("#form-event-id").value;
        const reviewedVer = parseInt(container.querySelector("#form-reviewed-ver").value, 10);
        const matchId = container.querySelector("#form-match-id").value;
        const eaId = container.querySelector("#form-ea-id").value;
        const decisionType = container.querySelector("#form-decision-type").value;
        const targetActId = container.querySelector("#form-activity-id").value;
        const overrideCat = container.querySelector("#form-override-category").value;
        const reasonNotes = container.querySelector("#form-reason-notes").value.trim();
        const statusDiv = container.querySelector("#form-result-status");

        statusDiv.innerHTML = `<span style="color: var(--text-muted)">Submitting decision via REST API...</span>`;

        const payload = {
          event_id: eventId,
          planner_id: "PLN-EXPERT-01",
          decision_type: decisionType,
          reviewed_trust_version: reviewedVer,
          reviewed_match_result_id: matchId,
          reviewed_evidence_assessment_id: eaId,
          selected_activity_id: targetActId || null,
          override_reason_category: overrideCat,
          reason_notes: reasonNotes || "Planner decision submitted via SATYA Console."
        };

        const res = await this.api.submitHitlDecision(payload);

        if (res.status === 409) {
          // REST Snapshot Lock Stale State Alert!
          this.staleStateAlert = true;
          statusDiv.innerHTML = `<span style="color: var(--color-review)">⚠ HTTP 409 Conflict: ${res.data?.error?.message}</span>`;
          this.renderWorkspace(item, this.traceData, null, []);
        } else if (res.ok && res.data) {
          statusDiv.innerHTML = `<span style="color: var(--color-trusted)">✓ Decision recorded! Decision ID: ${res.data.decision_id}. Resulting Trust Status: <strong>${res.data.resulting_trust_status}</strong>.</span>`;
          await this.loadQueue();
        } else {
          statusDiv.innerHTML = `<span style="color: var(--color-untrusted)">✕ Error: ${res.data?.error?.message || "Failed to submit decision"}</span>`;
        }
      });
    }
  }

  bindEvents(container) {
    const filterSelect = container.querySelector("#queue-priority-filter");
    if (filterSelect) {
      filterSelect.addEventListener("change", (e) => {
        this.loadQueue(e.target.value);
      });
    }

    container.addEventListener("click", (e) => {
      const queueEl = e.target.closest(".queue-item");
      if (queueEl) {
        const queueId = queueEl.getAttribute("data-queue-id");
        const item = this.currentQueueItems.find(i => i.queue_item_id === queueId);
        if (item) {
          this.selectItem(item);
        }
      }
    });

    window.addEventListener("satya:jump_recon", async (e) => {
      const eventId = e.detail?.eventId;
      if (eventId) {
        await this.loadQueue();
        const found = this.currentQueueItems.find(i => i.event_id === eventId);
        if (found) {
          await this.selectItem(found);
        }
      }
    });
  }
}
