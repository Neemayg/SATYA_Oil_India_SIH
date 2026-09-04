/**
 * SATYA Frontend State Store (Phase 12)
 * Holds client-side active selections (current project ID, active view tab, selected queue item).
 * Does NOT compute or store domain-level metrics.
 */

export const appState = {
  currentProjectId: "PRJ-NBG-2026",
  activeView: "control-tower",
  selectedQueueItemId: null,
  activeQueueItem: null,
  activeTraceData: null,
  availableProjects: [
    { id: "PRJ-NBG-2026", name: "PRJ-NBG-2026 (North Basin Pipeline Expansion)" },
    { id: "PRJ-SCP-2026", name: "PRJ-SCP-2026 (South Basin Compressor Station)" }
  ],

  setProject(projectId) {
    this.currentProjectId = projectId;
    console.log(`[State] Active Project set to: ${projectId}`);
  },

  setView(viewName) {
    this.activeView = viewName;
    console.log(`[State] Active View set to: ${viewName}`);
  },

  setSelectedQueueItem(item, traceData = null) {
    this.activeQueueItem = item;
    this.activeTraceData = traceData;
    this.selectedQueueItemId = item ? item.queue_item_id : null;
    console.log(`[State] Selected Queue Item set to:`, this.selectedQueueItemId);
  }
};
