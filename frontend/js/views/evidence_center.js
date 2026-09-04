/**
 * SATYA Evidence & Provenance Center View (Phase 12)
 * Full End-to-End Provenance Inspector: Source Document -> Evidence Fragment -> Atomic Claim -> Event -> Locators.
 * Communicates strictly via GET /api/v1/evidence/events/{event_id}/trace.
 */

import { renderTrustBadge, formatDate } from "../formatters.js";

export class EvidenceCenterView {
  constructor(apiClient, appState) {
    this.api = apiClient;
    this.state = appState;
  }

  async render(container) {
    container.innerHTML = `
      <div class="card-title" style="margin-bottom: 1rem;">Evidence & Provenance Traceability Center</div>

      <!-- Search Bar -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <form id="evidence-search-form" style="display: flex; gap: 0.75rem;">
          <input type="text" id="evidence-event-id-input" class="project-select" style="flex: 1; font-family: var(--font-mono);" placeholder="Enter Event ID (e.g. EVT-1001) to view complete provenance trace..." />
          <button type="submit" class="btn btn-primary">Trace Evidence Chain</button>
        </form>
      </div>

      <!-- Trace Details Workspace -->
      <div id="evidence-trace-workspace">
        <div class="card" style="text-align: center; padding: 3rem; color: var(--text-muted);">
          Enter an Event ID above to inspect its full provenance tree and raw source fragment locators.
        </div>
      </div>
    `;

    this.bindEvents(container);
  }

  async loadTrace(eventId) {
    const workspace = document.getElementById("evidence-trace-workspace");
    if (!workspace) return;

    workspace.innerHTML = `<div style="padding: 2rem; color: var(--text-muted); text-align: center;">Fetching end-to-end trace from backend REST API...</div>`;

    const res = await this.api.getEventTrace(eventId);
    if (res.ok && res.data) {
      const d = res.data;
      const ev = d.execution_event || {};
      const src = d.source_document || {};
      const claims = d.claims || [];
      const frags = d.evidence_fragments || [];
      const ta = d.latest_trust_assessment || {};

      workspace.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
          <!-- Execution Event Overview Card -->
          <div class="recon-step-card">
            <div class="recon-step-header">
              <div class="recon-step-title">1. EXECUTION EVENT</div>
              ${renderTrustBadge(ta.trust_status || "REVIEW_REQUIRED")}
            </div>
            <div class="recon-step-body">
              <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; font-size: 0.85rem;">
                <div>Event ID: <strong style="font-family: var(--font-mono);">${ev.event_id || eventId}</strong></div>
                <div>Discipline: <strong>${ev.discipline || "N/A"}</strong></div>
                <div>Observed Quantity: <strong>${ev.observed_quantity !== null && ev.observed_quantity !== undefined ? `${ev.observed_quantity} ${ev.unit_of_measure || ''}` : "NOT AVAILABLE"}</strong></div>
                <div>Source ID: <strong style="font-family: var(--font-mono);">${ev.source_id || "N/A"}</strong></div>
              </div>
            </div>
          </div>

          <!-- Atomic Evidence Claims Card -->
          <div class="recon-step-card">
            <div class="recon-step-header">
              <div class="recon-step-title">2. EXTRACTED ATOMIC EVIDENCE CLAIMS (${claims.length})</div>
            </div>
            <div class="recon-step-body">
              ${claims.length > 0 ? `
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Claim ID</th>
                      <th>Claim Type</th>
                      <th>Raw Statement</th>
                      <th>Normalized Value</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${claims.map(c => `
                      <tr>
                        <td style="font-family: var(--font-mono); font-weight: 700;">${c.claim_id}</td>
                        <td><span class="badge badge-blue">${c.claim_type}</span></td>
                        <td>${c.raw_statement}</td>
                        <td>${c.normalized_value !== null ? `${c.normalized_value} ${c.unit || ''}` : "N/A"}</td>
                        <td style="font-weight: 700; color: var(--color-trusted);">${(c.confidence * 100).toFixed(0)}%</td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              ` : `<div style="color: var(--text-muted); font-size: 0.85rem;">Zero atomic evidence claims extracted for this event.</div>`}
            </div>
          </div>

          <!-- Evidence Fragments & Provenance Locators Card -->
          <div class="recon-step-card">
            <div class="recon-step-header">
              <div class="recon-step-title">3. EVIDENCE FRAGMENTS & PROVENANCE LOCATORS</div>
              <span class="badge badge-neutral">${frags.length} Fragments</span>
            </div>
            <div class="recon-step-body">
              ${frags.length > 0 ? frags.map(f => `
                <div style="background: var(--bg-dark-input); border: 1px solid var(--border-subtle); padding: 0.75rem; border-radius: 6px; margin-bottom: 0.6rem;">
                  <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.3rem;">
                    <span>Fragment ID: <strong style="font-family: var(--font-mono); color: var(--text-main);">${f.fragment_id}</strong></span>
                    <span>Locator: <strong>${f.locator_type} (${f.locator_value})</strong></span>
                    <span>Origin Group: <strong>${f.origin_group_id}</strong></span>
                  </div>
                  <div style="font-family: var(--font-mono); font-size: 0.85rem; color: #F1F5F9; background: #000; padding: 0.5rem; border-radius: 4px;">
                    "${f.raw_text_snippet}"
                  </div>
                </div>
              `).join('') : `<div style="color: var(--text-muted); font-size: 0.85rem;">Zero evidence fragments linked.</div>`}
            </div>
          </div>

          <!-- Raw Source Document Metadata Card -->
          <div class="recon-step-card">
            <div class="recon-step-header">
              <div class="recon-step-title">4. ORIGINAL SOURCE DOCUMENT LEDGER</div>
              <span class="badge badge-neutral">${src.file_name || "Raw Text Input"}</span>
            </div>
            <div class="recon-step-body">
              <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.6rem;">
                <div>Project ID: <strong style="color: var(--text-main);">${src.project_id || "N/A"}</strong></div>
                <div>Author: <strong style="color: var(--text-main);">${src.author || "Unknown"}</strong></div>
                <div>SHA-256 Hash: <strong style="font-family: var(--font-mono); color: var(--text-main);">${src.sha256_hash ? src.sha256_hash.substring(0, 16) + '...' : 'N/A'}</strong></div>
              </div>
              <div style="background: var(--bg-dark-input); padding: 0.75rem; border-radius: 6px; font-family: var(--font-mono); font-size: 0.85rem; color: #94A3B8; max-height: 150px; overflow-y: auto;">
                ${src.raw_content || "Raw document content not available"}
              </div>
            </div>
          </div>
        </div>
      `;
    } else {
      workspace.innerHTML = `
        <div class="card" style="text-align: center; padding: 2rem; color: var(--color-untrusted);">
          ✕ Could not find provenance trace for Event ID '${eventId}'. Ensure the event exists in backend database.
        </div>
      `;
    }
  }

  bindEvents(container) {
    const form = container.querySelector("#evidence-search-form");
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const input = container.querySelector("#evidence-event-id-input").value.trim();
        if (input) {
          this.loadTrace(input);
        }
      });
    }
  }
}
