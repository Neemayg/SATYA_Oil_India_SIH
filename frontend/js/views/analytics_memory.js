/**
 * SATYA Analytics & Institutional Memory View (Phase 14)
 * Renders the 5th tab workspace: Terminology Memory, Productivity Benchmarks,
 * Contractor Reporting Scorecards, and Conflict Resolution Analytics.
 */

import { apiClient } from '../api_client.js';
import { state } from '../state.js';
import { renderStatusBadge } from '../formatters.js';

export async function renderAnalyticsMemoryView() {
    const container = document.getElementById('main-content');
    if (!container) return;

    const projectId = state.selectedProjectId || 'PRJ-NBG-2026';

    container.innerHTML = `
        <div class="view-header">
            <div>
                <h2>Analytics & Institutional Memory</h2>
                <p class="subtitle">Auditable, versioned execution knowledge distilled from planner decisions and empirical execution history.</p>
            </div>
            <button id="btn-trigger-distill" class="btn btn-primary">
                🧠 Run Memory Distillation
            </button>
        </div>

        <div id="analytics-alert-container"></div>

        <!-- 4 Pillars Grid -->
        <div class="grid grid-2 mb-6">
            <!-- Pillar A: Terminology Aliases -->
            <div class="card">
                <div class="card-header flex-between">
                    <h3>Terminology Memory Desk (Pillar A)</h3>
                    <span class="badge badge-info">Project Scoped</span>
                </div>
                <p class="text-muted mb-4">Learned field phrase aliases distilled from human planner corrections (CHANGE_MATCH).</p>
                <div id="memory-aliases-list">
                    <p class="text-muted">Loading terminology memory...</p>
                </div>
            </div>

            <!-- Pillar B: Productivity Rate Benchmarks -->
            <div class="card">
                <div class="card-header flex-between">
                    <h3>Productivity Rate Benchmarks (Pillar B)</h3>
                    <span class="badge badge-info">Sample Gated</span>
                </div>
                <p class="text-muted mb-4">Empirical actual physical execution rates (P50/P90) vs planned baseline rates.</p>
                <div id="productivity-benchmarks-list">
                    <p class="text-muted">Loading productivity benchmarks...</p>
                </div>
            </div>
        </div>

        <div class="grid grid-2 mb-6">
            <!-- Pillar C: Contractor Reporting Scorecard -->
            <div class="card">
                <div class="card-header flex-between">
                    <h3>Contractor Reporting Profile (Pillar C)</h3>
                    <span class="badge badge-secondary">Completeness Profile</span>
                </div>
                <div class="alert alert-info mb-4 text-xs">
                    ℹ <strong>Governance Disclaimer:</strong> This profile describes historical reporting and evidence completeness characteristics; it is NOT a contractor performance, compliance, or contractual quality score.
                </div>
                <div id="contractor-scorecard-list">
                    <p class="text-muted">Loading contractor reporting profiles...</p>
                </div>
            </div>

            <!-- Pillar D: Conflict & Warning Resolution -->
            <div class="card">
                <div class="card-header flex-between">
                    <h3>Conflict & Warning Resolution (Pillar D)</h3>
                    <span class="badge badge-secondary">Resolution Pathways</span>
                </div>
                <p class="text-muted mb-4">Resolution pathways and lead times for machine conflict flags and Time Agent warning signals.</p>
                <div id="conflict-patterns-list">
                    <p class="text-muted">Loading resolution analytics...</p>
                </div>
            </div>
        </div>
    `;

    // Bind Distillation Run Button
    const distillBtn = document.getElementById('btn-trigger-distill');
    if (distillBtn) {
        distillBtn.addEventListener('click', async () => {
            distillBtn.disabled = true;
            distillBtn.innerText = '🧠 Distilling Memory...';
            try {
                const res = await apiClient.distillMemory(projectId);
                const alertBox = document.getElementById('analytics-alert-container');
                if (alertBox && res.distillation_run) {
                    const run = res.distillation_run;
                    alertBox.innerHTML = `
                        <div class="alert alert-success mb-4 flex-between">
                            <span>✅ Memory Distillation Completed! Created ${run.candidates_created_count} candidate aliases, promoted ${run.promoted_aliases_count} aliases.</span>
                            <span class="text-xs text-muted">Run ID: ${run.distillation_run_id}</span>
                        </div>
                    `;
                }
                await loadAllAnalyticsData(projectId);
            } catch (err) {
                alert(`Memory Distillation Failed: ${err.message}`);
            } finally {
                distillBtn.disabled = false;
                distillBtn.innerText = '🧠 Run Memory Distillation';
            }
        });
    }

    await loadAllAnalyticsData(projectId);
}

async function loadAllAnalyticsData(projectId) {
    // 1. Load Terminology Memory Aliases
    try {
        const res = await apiClient.getMemoryAliases(projectId);
        const listEl = document.getElementById('memory-aliases-list');
        if (listEl) {
            if (!res.aliases || res.aliases.length === 0) {
                listEl.innerHTML = `<p class="text-muted">No terminology aliases distilled yet. Perform planner corrections on Reconciliation Desk and click 'Run Memory Distillation'.</p>`;
            } else {
                let html = `<table class="table text-xs">
                    <thead>
                        <tr>
                            <th>Field Phrase</th>
                            <th>Target Activity</th>
                            <th>Status</th>
                            <th>Confidence</th>
                            <th>Planners</th>
                        </tr>
                    </thead>
                    <tbody>`;
                res.aliases.forEach(a => {
                    const badgeClass = a.status === 'ACTIVE' ? 'badge-success' : (a.status === 'VALIDATED' ? 'badge-info' : 'badge-secondary');
                    html += `
                        <tr>
                            <td><code>${a.alias_phrase}</code></td>
                            <td><strong>${a.target_activity_id}</strong></td>
                            <td><span class="badge ${badgeClass}">${a.status}</span></td>
                            <td>${(a.confidence_weight * 100).toFixed(0)}%</td>
                            <td>${a.distinct_planner_count}</td>
                        </tr>
                    `;
                });
                html += `</tbody></table>`;
                listEl.innerHTML = html;
            }
        }
    } catch (err) {
        console.error("Failed to load memory aliases", err);
    }

    // 2. Load Productivity Rate Benchmarks
    try {
        const res = await apiClient.getProductivityAnalytics(projectId);
        const listEl = document.getElementById('productivity-benchmarks-list');
        if (listEl) {
            if (!res.benchmarks || res.benchmarks.length === 0) {
                listEl.innerHTML = `<p class="text-muted">No productivity benchmarks calculated yet. Ingest trusted execution events to populate actual rates.</p>`;
            } else {
                let html = `<table class="table text-xs">
                    <thead>
                        <tr>
                            <th>WBS / Activity</th>
                            <th>Planned Rate</th>
                            <th>Actual P50</th>
                            <th>Actual P90</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>`;
                res.benchmarks.forEach(b => {
                    const plannedStr = b.planned_rate !== null ? `${b.planned_rate} ${b.unit_of_measure}/d` : 'N/A';
                    const statusBadge = b.benchmark_status === 'VALIDATED' ? 'badge-success' : (b.benchmark_status === 'PROVISIONAL' ? 'badge-warning' : 'badge-secondary');
                    html += `
                        <tr>
                            <td>
                                <div><strong>${b.wbs_id}</strong></div>
                                <span class="text-muted">${b.activity_type} (${b.unit_of_measure})</span>
                            </td>
                            <td>${plannedStr}</td>
                            <td><strong>${b.p50_rate}</strong> ${b.unit_of_measure}/d</td>
                            <td>${b.p90_rate} ${b.unit_of_measure}/d</td>
                            <td><span class="badge ${statusBadge}">${b.benchmark_status}</span></td>
                        </tr>
                    `;
                });
                html += `</tbody></table>`;
                listEl.innerHTML = html;
            }
        }
    } catch (err) {
        console.error("Failed to load productivity benchmarks", err);
    }

    // 3. Load Contractor Reporting Profiles
    try {
        const res = await apiClient.getContractorAnalytics(projectId);
        const listEl = document.getElementById('contractor-scorecard-list');
        if (listEl) {
            if (!res.profiles || res.profiles.length === 0) {
                listEl.innerHTML = `<p class="text-muted">No contractor reporting data available.</p>`;
            } else {
                let html = `<table class="table text-xs">
                    <thead>
                        <tr>
                            <th>Contractor / Source</th>
                            <th>Total Events</th>
                            <th>Verification Ratio</th>
                            <th>Avg Reporting Delay</th>
                        </tr>
                    </thead>
                    <tbody>`;
                res.profiles.forEach(p => {
                    const name = p.contractor_id || 'UNKNOWN / UNATTRIBUTED';
                    const delayStr = p.avg_reporting_delay_days !== null ? `${p.avg_reporting_delay_days} days` : 'N/A';
                    html += `
                        <tr>
                            <td><strong>${name}</strong></td>
                            <td>${p.total_events}</td>
                            <td><strong class="text-success">${(p.verification_ratio * 100).toFixed(1)}%</strong> (${p.trusted_events}/${p.total_events})</td>
                            <td>${delayStr}</td>
                        </tr>
                    `;
                });
                html += `</tbody></table>`;
                listEl.innerHTML = html;
            }
        }
    } catch (err) {
        console.error("Failed to load contractor profiles", err);
    }

    // 4. Load Conflict & Warning Resolution Patterns
    try {
        const res = await apiClient.getConflictAnalytics(projectId);
        const listEl = document.getElementById('conflict-patterns-list');
        if (listEl) {
            if (!res.patterns || res.patterns.length === 0) {
                listEl.innerHTML = `<p class="text-muted">No conflict or warning resolution history recorded.</p>`;
            } else {
                let html = `<table class="table text-xs">
                    <thead>
                        <tr>
                            <th>Conflict / Signal Type</th>
                            <th>Occurrences</th>
                            <th>Pathways (Valid / Remap / Reject)</th>
                            <th>Acknowledged vs Resolved</th>
                        </tr>
                    </thead>
                    <tbody>`;
                res.patterns.forEach(p => {
                    html += `
                        <tr>
                            <td><code>${p.conflict_or_signal_type}</code></td>
                            <td>${p.total_occurrences}</td>
                            <td>${p.validated_count} Valid / ${p.remapped_count} Remap / ${p.rejected_count} Reject</td>
                            <td>${p.acknowledged_count} Ack / <strong class="text-success">${p.resolved_count} Resolved</strong></td>
                        </tr>
                    `;
                });
                html += `</tbody></table>`;
                listEl.innerHTML = html;
            }
        }
    } catch (err) {
        console.error("Failed to load conflict patterns", err);
    }
}
