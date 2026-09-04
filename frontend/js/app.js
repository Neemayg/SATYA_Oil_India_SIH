/**
 * SATYA Web Application Entry Point & Router (Phase 12)
 * Initializes application state, tab router, dynamic project selector, and health monitor.
 */

import { SATYAApiClient } from "./api_client.js";
import { appState } from "./state.js";

import { ControlTowerView } from "./views/control_tower.js";
import { ReconciliationDeskView } from "./views/reconciliation_desk.js";
import { EvidenceCenterView } from "./views/evidence_center.js";
import { ScheduleExplorerView } from "./views/schedule_explorer.js";
import { renderAnalyticsMemoryView } from "./views/analytics_memory.js";

document.addEventListener("DOMContentLoaded", async () => {
  console.log("[SATYA] Initializing Frontend Application...");

  const apiClient = new SATYAApiClient("/api/v1");

  const views = {
    "control-tower": new ControlTowerView(apiClient, appState),
    "reconciliation": new ReconciliationDeskView(apiClient, appState),
    "evidence": new EvidenceCenterView(apiClient, appState),
    "schedule": new ScheduleExplorerView(apiClient, appState),
    "analytics": { render: () => renderAnalyticsMemoryView() }
  };

  const container = document.getElementById("view-container");
  const projectSelect = document.getElementById("global-project-select");
  const healthPill = document.getElementById("global-health-pill");
  const navTabs = document.querySelectorAll(".nav-tab");

  // Operational Health Check
  const checkHealth = async () => {
    const res = await apiClient.getHealth();
    if (res.ok && res.data && res.data.status === "OK") {
      healthPill.className = "badge badge-trusted";
      healthPill.innerHTML = `● API OPERATIONAL`;
    } else {
      healthPill.className = "badge badge-untrusted";
      healthPill.innerHTML = `● API OFFLINE`;
    }
  };

  await checkHealth();

  // Dynamic Project Selector Initialization
  if (projectSelect) {
    projectSelect.innerHTML = appState.availableProjects.map(p => `
      <option value="${p.id}" ${p.id === appState.currentProjectId ? 'selected' : ''}>${p.name}</option>
    `).join('');

    projectSelect.addEventListener("change", (e) => {
      appState.setProject(e.target.value);
      renderActiveView();
    });
  }

  // View Tab Router
  const renderActiveView = async () => {
    const currentViewKey = appState.activeView;
    const viewComponent = views[currentViewKey];

    navTabs.forEach(tab => {
      if (tab.getAttribute("data-view") === currentViewKey) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });

    if (viewComponent && container) {
      container.innerHTML = `<div style="padding: 2rem; text-align: center; color: var(--text-muted);">Loading view...</div>`;
      await viewComponent.render(container);
    }
  };

  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const viewKey = tab.getAttribute("data-view");
      appState.setView(viewKey);
      renderActiveView();
    });
  });

  // Global Event Listener for jump to reconciliation
  window.addEventListener("satya:jump_recon", () => {
    renderActiveView();
  });

  // Initial View Render
  await renderActiveView();
});
