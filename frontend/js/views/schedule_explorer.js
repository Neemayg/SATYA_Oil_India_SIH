/**
 * SATYA Schedule Explorer View (Phase 12)
 * Interactive WBS & Activity Table with SATYA Execution Truth Overlay.
 * Communicates strictly via GET /api/v1/projections/projects/{id}/latest and GET /api/v1/fingerprints/projects/{id}.
 */

import {
  renderTrustBadge,
  renderQAClearanceBadge,
  formatPct,
  formatDate
} from "../formatters.js";

export class ScheduleExplorerView {
  constructor(apiClient, appState) {
    this.api = apiClient;
    this.state = appState;
  }

  async render(container) {
    container.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
        <div class="card-title">Schedule Explorer (SATYA Execution Truth Overlay)</div>
        <button id="btn-recalculate-proj" class="btn btn-primary" style="font-size: 0.8rem;">Recalculate Schedule Projection</button>
      </div>

      <div class="card">
        <div class="card-header">
          <div style="font-size: 0.85rem; color: var(--text-muted);">
            Baseline Schedule Authority: <strong id="sched-project-id" style="color: var(--text-main);">${this.state.currentProjectId}</strong>
          </div>
          <div id="sched-as-of-date" style="font-size: 0.8rem; color: var(--color-blue); font-weight: 700;">
            Projection As-Of Date: Loading...
          </div>
        </div>

        <div id="schedule-table-container" style="overflow-x: auto;">
          <div style="padding: 2rem; color: var(--text-muted); text-align: center;">Loading SATYA Schedule Overlay via REST API...</div>
        </div>
      </div>
    `;

    this.bindEvents(container);
    await this.loadSchedule();
  }

  async loadSchedule() {
    const projId = this.state.currentProjectId;
    const tableDiv = document.getElementById("schedule-table-container");
    if (!tableDiv) return;

    // Fetch Fingerprints (Baseline Schedule Activities)
    const fpRes = await this.api.getFingerprints(projId);
    const projRes = await this.api.getLatestProjection(projId);

    if (fpRes.ok && fpRes.data && fpRes.data.fingerprints) {
      const fingerprints = fpRes.data.fingerprints;
      const projection = projRes.ok && projRes.data ? projRes.data : null;

      const actProgressMap = {};
      if (projection && projection.activity_progress_map) {
        Object.assign(actProgressMap, projection.activity_progress_map);
      }

      document.getElementById("sched-as-of-date").innerText = `As-Of Date: ${projection ? formatDate(projection.as_of_date) : 'N/A'} (SHA-256 Baseline Verified)`;

      tableDiv.innerHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>Activity ID</th>
              <th>Activity Name</th>
              <th>WBS Path</th>
              <th>Discipline</th>
              <th>Baseline Start / Finish</th>
              <th>Actual / Forecast Finish</th>
              <th>Physical Progress %</th>
              <th>QA Clearance</th>
              <th>Trust Status</th>
              <th>Finish Variance</th>
            </tr>
          </thead>
          <tbody>
            ${fingerprints.map(fp => {
              const prog = actProgressMap[fp.activity_id] || null;

              const physPct = prog ? prog.physical_progress_pct : null;
              const qaStatus = prog ? prog.qa_clearance_status : null;
              const trustStatus = prog ? prog.trust_status : null;
              const actualStart = prog ? prog.actual_start : null;
              const forecastFinish = prog ? prog.forecast_finish : null;
              const finishVar = prog ? prog.finish_variance_days : null;

              const isCriticalDelay = prog ? prog.critical_activity_projected_delay : false;

              return `
                <tr style="${isCriticalDelay ? 'background: rgba(239, 68, 68, 0.08);' : ''}">
                  <td style="font-family: var(--font-mono); font-weight: 700;">
                    ${fp.activity_id}
                    ${fp.is_critical ? `<span style="color: var(--color-untrusted); font-size: 0.7rem; margin-left: 0.2rem;">[CRITICAL]</span>` : ''}
                  </td>
                  <td style="font-weight: 600;">${fp.activity_name}</td>
                  <td style="font-size: 0.75rem; color: var(--text-muted);">${fp.wbs_name_path}</td>
                  <td><span class="badge badge-neutral">${fp.discipline || 'UNKNOWN'}</span></td>
                  <td style="font-size: 0.75rem; color: var(--text-muted);">
                    ${formatDate(fp.planned_start)} to ${formatDate(fp.planned_finish)}
                  </td>
                  <td style="font-size: 0.75rem;">
                    ${actualStart ? `Start: ${formatDate(actualStart)}` : 'Not Started'}<br/>
                    ${forecastFinish ? `Forecast: ${formatDate(forecastFinish)}` : (prog ? 'Forecast: NOT AVAILABLE' : 'NOT AVAILABLE')}
                  </td>
                  <td style="font-weight: 700; color: var(--color-blue);">
                    ${formatPct(physPct)}
                  </td>
                  <td>${renderQAClearanceBadge(qaStatus)}</td>
                  <td>${renderTrustBadge(trustStatus)}</td>
                  <td style="font-family: var(--font-mono); font-weight: 700;">
                    ${finishVar !== null && finishVar !== undefined ? (
                      finishVar > 0 ? `<span style="color: var(--color-untrusted);">+${finishVar}d (DELAY)</span>` : `<span style="color: var(--color-trusted);">${finishVar}d</span>`
                    ) : '<span style="color: var(--text-muted);">NOT AVAILABLE</span>'}
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      `;
    } else {
      tableDiv.innerHTML = `<div style="padding: 2rem; color: var(--color-untrusted); text-align: center;">✕ Failed to load baseline schedule activities for project '${projId}'.</div>`;
    }
  }

  bindEvents(container) {
    const btnRe = container.querySelector("#btn-recalculate-proj");
    if (btnRe) {
      btnRe.addEventListener("click", async () => {
        btnRe.innerText = "Calculating Projection...";
        const res = await this.api.generateProjection(this.state.currentProjectId);
        if (res.ok) {
          await this.loadSchedule();
        }
        btnRe.innerText = "Recalculate Schedule Projection";
      });
    }
  }
}
