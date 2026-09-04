/**
 * SATYA Formatting Helpers (Phase 12)
 * Pure presentation formatters. Returns 'NOT AVAILABLE' for missing backend data.
 * Never invents mock or default values.
 */

export function renderTrustBadge(status) {
  if (!status) return `<span class="badge badge-neutral">NOT AVAILABLE</span>`;

  const s = String(status).toUpperCase();
  if (s === "TRUSTED") return `<span class="badge badge-trusted">✓ TRUSTED</span>`;
  if (s === "REVIEW_REQUIRED") return `<span class="badge badge-review">⚠ REVIEW REQUIRED</span>`;
  if (s === "UNTRUSTED") return `<span class="badge badge-untrusted">✕ UNTRUSTED</span>`;
  if (s === "CONFLICTED") return `<span class="badge badge-conflicted">⚡ CONFLICTED</span>`;
  return `<span class="badge badge-neutral">${s}</span>`;
}

export function renderMatchOutcomeBadge(outcome) {
  if (!outcome) return `<span class="badge badge-neutral">NOT AVAILABLE</span>`;

  const o = String(outcome).toUpperCase();
  if (o === "MATCHED") return `<span class="badge badge-trusted">✓ MATCHED</span>`;
  if (o === "AMBIGUOUS") return `<span class="badge badge-review">⚠ AMBIGUOUS</span>`;
  if (o === "UNMATCHED") return `<span class="badge badge-untrusted">✕ UNMATCHED</span>`;
  if (o === "INSUFFICIENT_EVIDENCE") return `<span class="badge badge-warning">? INSUFFICIENT EVIDENCE</span>`;
  return `<span class="badge badge-neutral">${o}</span>`;
}

export function renderPriorityPill(priority) {
  if (!priority) return `<span class="priority-pill priority-p4">P4</span>`;
  const p = String(priority).toUpperCase();
  if (p === "P1_CRITICAL" || p === "P1") return `<span class="priority-pill priority-p1">P1 CRITICAL</span>`;
  if (p === "P2_HIGH" || p === "P2") return `<span class="priority-pill priority-p2">P2 HIGH</span>`;
  if (p === "P3_MEDIUM" || p === "P3") return `<span class="priority-pill priority-p3">P3 MEDIUM</span>`;
  return `<span class="priority-pill priority-p4">P4 LOW</span>`;
}

export function renderQAClearanceBadge(status) {
  if (!status) return `<span class="badge badge-neutral">NOT AVAILABLE</span>`;
  const s = String(status).toUpperCase();
  if (s === "CLEARED") return `<span class="badge badge-trusted">✓ QA CLEARED</span>`;
  if (s === "PENDING") return `<span class="badge badge-review">⏳ QA PENDING</span>`;
  if (s === "NOT_REQUIRED") return `<span class="badge badge-neutral">N/A</span>`;
  return `<span class="badge badge-neutral">${s}</span>`;
}

export function formatPct(val) {
  if (val === null || val === undefined) return "NOT AVAILABLE";
  return `${Number(val).toFixed(1)}%`;
}

export function formatDate(dateStr) {
  if (!dateStr) return "N/A";
  return String(dateStr).split("T")[0];
}

export function renderFactorBreakdown(factorBreakdown) {
  if (!factorBreakdown) {
    return `<div class="text-muted">Factor breakdown score data NOT AVAILABLE</div>`;
  }

  const factors = [
    { key: "exact_identifier_score", name: "Exact ID Match" },
    { key: "spatial_chainage_score", name: "Spatial / Chainage" },
    { key: "wbs_structural_score", name: "WBS Structural" },
    { key: "discipline_score", name: "Discipline Match" },
    { key: "terminology_action_score", name: "Terminology & Actions" },
    { key: "temporal_window_score", name: "Temporal Baseline Window" }
  ];

  return `
    <div class="factor-grid">
      ${factors.map(f => {
        const score = factorBreakdown[f.key] !== undefined ? factorBreakdown[f.key] : null;
        const icon = score !== null && score > 0.7 ? "✓" : (score !== null && score > 0.3 ? "⚠" : "✕");
        const color = score !== null && score > 0.7 ? "var(--color-trusted)" : (score !== null && score > 0.3 ? "var(--color-review)" : "var(--color-untrusted)");
        const displayVal = score !== null ? `${(score * 100).toFixed(0)}%` : "N/A";

        return `
          <div class="factor-card">
            <div class="factor-name">${f.name}</div>
            <div class="factor-val" style="color: ${color}">
              <span>${icon} ${displayVal}</span>
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
}

export function renderSignalBadge(signalType) {
  if (!signalType) return "";
  const t = String(signalType).toUpperCase();
  if (t === "SILENT_CRITICAL_PATH_RISK") return `<span class="badge badge-untrusted">⚠ SILENT RISK</span>`;
  if (t === "REPORTING_LATENCY_STALENESS") return `<span class="badge badge-review">⏳ STALE REPORTING</span>`;
  if (t === "FORECAST_FINISH_SLIPPAGE") return `<span class="badge badge-untrusted">📉 FORECAST SLIP</span>`;
  if (t === "UNVERIFIED_CLAIM_TEMPORAL_DRIFT") return `<span class="badge badge-review">⚠ UNVERIFIED DRIFT</span>`;
  if (t === "OUT_OF_SEQUENCE_EXECUTION_WARNING") return `<span class="badge badge-conflicted">⚡ SEQUENCE ANOMALY</span>`;
  if (t === "QA_CLEARANCE_BOTTLENECK") return `<span class="badge badge-review">🔒 QA BOTTLENECK</span>`;
  return `<span class="badge badge-neutral">${t}</span>`;
}
