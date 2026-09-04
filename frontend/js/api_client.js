/**
 * SATYA REST API Client (Phase 12)
 * Communicates strictly via http://127.0.0.1:8000/api/v1 REST endpoints.
 * Never mutates data directly or executes business logic in browser.
 */

export class SATYAApiClient {
  constructor(baseUrl = "/api/v1") {
    this.baseUrl = baseUrl;
  }

  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultHeaders = {
      "Content-Type": "application/json"
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    if (config.body && typeof config.body === "object") {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      return {
        status: response.status,
        ok: response.ok,
        data: data
      };
    } catch (err) {
      console.error(`[API Error] Request failed on ${endpoint}:`, err);
      return {
        status: 0,
        ok: false,
        data: {
          error: {
            code: "NETWORK_ERROR",
            message: `Failed to connect to backend server at ${url}. Ensure scripts/run_server.py is running.`,
            details: {}
          }
        }
      };
    }
  }

  // System Endpoints
  async getHealth() {
    return this._request("/health");
  }

  // Ingestion Endpoints
  async uploadIngestion(payload) {
    return this._request("/ingestion/upload", {
      method: "POST",
      body: payload
    });
  }

  async getSourceDocument(sourceId) {
    return this._request(`/ingestion/sources/${sourceId}`);
  }

  async getExecutionEvent(eventId) {
    return this._request(`/ingestion/events/${eventId}`);
  }

  // Fingerprint Endpoints
  async getFingerprints(projectId) {
    return this._request(`/fingerprints/projects/${projectId}`);
  }

  async searchFingerprints(query, discipline = null) {
    let url = `/fingerprints/search?q=${encodeURIComponent(query)}`;
    if (discipline) url += `&discipline=${encodeURIComponent(discipline)}`;
    return this._request(url);
  }

  // Matching Endpoints
  async matchEvent(eventId) {
    return this._request("/matching/match", {
      method: "POST",
      body: { event_id: eventId }
    });
  }

  async getEventMatches(eventId) {
    return this._request(`/matching/events/${eventId}`);
  }

  // Evidence & Trust Endpoints
  async evaluateTrust(eventId, matchResultId = null) {
    return this._request("/evidence/evaluate", {
      method: "POST",
      body: { event_id: eventId, match_result_id: matchResultId }
    });
  }

  async getEventTrust(eventId) {
    return this._request(`/evidence/events/${eventId}/trust`);
  }

  async getEventConflicts(eventId) {
    return this._request(`/evidence/events/${eventId}/conflicts`);
  }

  async getEventTrace(eventId) {
    return this._request(`/evidence/events/${eventId}/trace`);
  }

  // HITL Queue & Decisions Endpoints
  async getQueue(projectId = null, priorityFilter = null) {
    let url = "/hitl/queue";
    const params = [];
    if (projectId) params.push(`project_id=${encodeURIComponent(projectId)}`);
    if (priorityFilter) params.push(`priority=${encodeURIComponent(priorityFilter)}`);
    if (params.length > 0) url += `?${params.join("&")}`;
    return this._request(url);
  }

  async submitHitlDecision(payload) {
    return this._request("/hitl/decisions", {
      method: "POST",
      body: payload
    });
  }

  // Schedule Projection Endpoints
  async generateProjection(projectId, asOfDate = null) {
    return this._request("/projections/generate", {
      method: "POST",
      body: { project_id: projectId, as_of_date: asOfDate }
    });
  }

  async getLatestProjection(projectId) {
    return this._request(`/projections/projects/${projectId}/latest`);
  }

  async getActivityProgress(projectId, activityId) {
    return this._request(`/projections/projects/${projectId}/activities/${activityId}`);
  }

  // Time Agent Monitoring Endpoints (Phase 13)
  async evaluateMonitoring(projectId, asOfDate = null) {
    return this._request("/monitoring/evaluate", {
      method: "POST",
      body: { project_id: projectId, as_of_date: asOfDate }
    });
  }

  async getActiveSignals(projectId, severity = null) {
    let url = `/monitoring/projects/${projectId}/signals`;
    if (severity) url += `?severity=${encodeURIComponent(severity)}`;
    return this._request(url);
  }

  async getSignalDetails(signalId) {
    return this._request(`/monitoring/signals/${signalId}`);
  }

  // Analytics & Institutional Memory Endpoints (Phase 14)
  async distillMemory(projectId, asOfDate = null) {
    return this._request(`/memory/projects/${projectId}/distill`, {
      method: "POST",
      body: { as_of_date: asOfDate }
    });
  }

  async getMemoryAliases(projectId, status = null) {
    let url = `/memory/projects/${projectId}/aliases`;
    if (status) url += `?status=${encodeURIComponent(status)}`;
    return this._request(url);
  }

  async getProductivityAnalytics(projectId) {
    return this._request(`/analytics/projects/${projectId}/productivity`);
  }

  async getContractorAnalytics(projectId) {
    return this._request(`/analytics/projects/${projectId}/contractors`);
  }

  async getConflictAnalytics(projectId) {
    return this._request(`/analytics/projects/${projectId}/conflicts`);
  }
}
