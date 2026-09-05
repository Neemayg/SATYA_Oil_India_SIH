"""
SATYA Manager Audit Route Handler
Compares worker-reported progress claims against independent manager audit
observations for every schedule activity and produces the audit report.

Worker claims  : any source type except MANAGER_AUDIT (DPR, supervisor notes, voice, diary...)
Manager audits : source type MANAGER_AUDIT (submitted from the mobile app in Manager mode)
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.persistence.database_engine import DatabaseEngine

QUANTITY_TOLERANCE = 0.10  # 10% difference between claim and audit is treated as agreement
DONE_TYPES = {"FINISH", "QA_CLEARANCE"}
BLOCKED_TYPES = {"HOLD"}


class AuditRouteHandler:

    def __init__(self, db: DatabaseEngine):
        self.db = db

    # ------------------------------------------------------------------
    def get_project_audit(self, project_id: str) -> Dict[str, Any]:
        fingerprints = {f["activity_id"]: f for f in self.db.get_fingerprints_by_project(project_id)}
        events = self.db.get_all_execution_events()

        # Latest match per event -> selected activity
        latest_match: Dict[str, Dict[str, Any]] = {}
        for m in self.db.get_all_match_results():
            prev = latest_match.get(m["event_id"])
            if not prev or (m.get("evaluated_at") or "") >= (prev.get("evaluated_at") or ""):
                latest_match[m["event_id"]] = m

        source_cache: Dict[str, Any] = {}
        per_activity: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        for ev in events:
            src = source_cache.get(ev["source_id"])
            if src is None:
                doc = self.db.get_source_document(ev["source_id"])
                src = {"project_id": doc.project_id, "source_type": doc.source_type, "author": doc.author, "file_name": doc.file_name} if doc else {}
                source_cache[ev["source_id"]] = src
            if src.get("project_id") and src["project_id"] != project_id:
                continue

            activity_id = ev.get("observed_activity_id")
            if not activity_id:
                m = latest_match.get(ev["event_id"])
                activity_id = m.get("selected_activity_id") if m else None
            if not activity_id:
                continue

            record = {
                "event_id": ev["event_id"],
                "event_type": ev.get("event_type"),
                "quantity": ev.get("observed_quantity"),
                "unit": ev.get("unit_of_measure"),
                "observed_at": ev.get("observed_timestamp") or (ev.get("source_timestamp") or "")[:10],
                "statement": ev.get("extracted_statement"),
                "author": src.get("author"),
                "source_type": src.get("source_type"),
                "source_id": ev["source_id"],
                "pending_qa": bool(ev.get("pending_qa_clearance")),
            }
            bucket = per_activity.setdefault(activity_id, {"claims": [], "audits": []})
            (bucket["audits"] if (src.get("source_type") or "").upper() == "MANAGER_AUDIT" else bucket["claims"]).append(record)

        activities: List[Dict[str, Any]] = []
        for activity_id, bucket in per_activity.items():
            fp = fingerprints.get(activity_id, {})
            claims = sorted(bucket["claims"], key=lambda r: r["observed_at"] or "")
            audits = sorted(bucket["audits"], key=lambda r: r["observed_at"] or "")
            latest_claim = claims[-1] if claims else None
            latest_audit = audits[-1] if audits else None
            status, variance_pct, reasons = self._compare(latest_claim, latest_audit, claims)
            activities.append({
                "activity_id": activity_id,
                "activity_name": fp.get("activity_name", activity_id),
                "discipline": fp.get("discipline"),
                "is_critical": bool(fp.get("is_critical")),
                "planned_quantity": fp.get("planned_quantity"),
                "unit": fp.get("unit_of_measure") or (latest_claim or {}).get("unit"),
                "planned_finish": fp.get("planned_finish"),
                "worker_claim_count": len(claims),
                "audit_count": len(audits),
                "latest_claim": latest_claim,
                "latest_audit": latest_audit,
                "claimed_quantity": self._best_quantity(claims),
                "audited_quantity": latest_audit["quantity"] if latest_audit else None,
                "variance_pct": variance_pct,
                "audit_status": status,
                "reasons": reasons,
                "days_since_audit": self._days_since(latest_audit["observed_at"]) if latest_audit else None,
            })

        order = {"DISCREPANCY": 0, "UNAUDITED": 1, "AUDIT_ONLY": 2, "CONFIRMED": 3}
        activities.sort(key=lambda a: (order.get(a["audit_status"], 9), -(a["variance_pct"] or 0)))

        claimed = [a for a in activities if a["worker_claim_count"] > 0]
        audited = [a for a in claimed if a["audit_count"] > 0]
        discrepancies = [a for a in activities if a["audit_status"] == "DISCREPANCY"]
        confirmed = [a for a in activities if a["audit_status"] == "CONFIRMED"]
        over = [a["variance_pct"] for a in audited if a["variance_pct"] is not None and a["variance_pct"] > 0]

        return {
            "project_id": project_id,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "activities_with_claims": len(claimed),
                "activities_audited": len(audited),
                "audit_coverage_pct": round(100.0 * len(audited) / len(claimed), 1) if claimed else 0.0,
                "confirmed": len(confirmed),
                "discrepancies": len(discrepancies),
                "unaudited": len([a for a in activities if a["audit_status"] == "UNAUDITED"]),
                "audit_only": len([a for a in activities if a["audit_status"] == "AUDIT_ONLY"]),
                "avg_over_reporting_pct": round(sum(over) / len(over), 1) if over else 0.0,
                "total_worker_claims": sum(a["worker_claim_count"] for a in activities),
                "total_audits": sum(a["audit_count"] for a in activities),
            },
            "activities": activities,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _best_quantity(claims: List[Dict[str, Any]]) -> Optional[float]:
        """Worker-claimed cumulative quantity: the latest reported quantity, or the max if reports are non-cumulative."""
        qs = [c["quantity"] for c in claims if c.get("quantity") is not None]
        if not qs:
            return None
        return max(qs[-1], max(qs)) if len(qs) > 1 else qs[0]

    @staticmethod
    def _days_since(date_str: Optional[str]) -> Optional[int]:
        try:
            return (datetime.utcnow().date() - datetime.strptime(date_str[:10], "%Y-%m-%d").date()).days
        except Exception:
            return None

    def _compare(self, claim: Optional[Dict[str, Any]], audit: Optional[Dict[str, Any]], claims: List[Dict[str, Any]]):
        if not claim and not audit:
            return "UNAUDITED", None, []
        if claim and not audit:
            return "UNAUDITED", None, ["No manager audit recorded for this activity yet."]
        if audit and not claim:
            return "AUDIT_ONLY", None, ["Manager audit exists but workers have not reported on this activity."]

        reasons: List[str] = []
        discrepancy = False
        variance_pct = None

        claimed_qty = self._best_quantity(claims)
        audited_qty = audit.get("quantity")
        if claimed_qty is not None and audited_qty is not None and claimed_qty > 0:
            variance_pct = round(100.0 * (claimed_qty - audited_qty) / claimed_qty, 1)
            if abs(claimed_qty - audited_qty) / claimed_qty > QUANTITY_TOLERANCE:
                discrepancy = True
                direction = "over" if claimed_qty > audited_qty else "under"
                reasons.append(f"Workers reported {claimed_qty:g} {claim.get('unit') or ''} but manager verified {audited_qty:g} ({abs(variance_pct):g}% {direction}-reported).")
            else:
                reasons.append(f"Quantity verified: claimed {claimed_qty:g}, audited {audited_qty:g} (within {int(QUANTITY_TOLERANCE * 100)}% tolerance).")

        ct, at = (claim.get("event_type") or ""), (audit.get("event_type") or "")
        if ct in DONE_TYPES and at in BLOCKED_TYPES:
            discrepancy = True
            reasons.append("Workers reported completion but manager found the work halted or failing inspection.")
        elif ct in DONE_TYPES and at == "PROGRESS":
            discrepancy = True
            reasons.append("Workers reported completion but manager observed work still in progress.")
        elif ct in DONE_TYPES and at in DONE_TYPES:
            reasons.append("Completion confirmed by manager audit.")
        elif ct == at and ct:
            reasons.append(f"Status agrees: both report {ct.lower().replace('_', ' ')}.")

        if audit.get("pending_qa") and ct in DONE_TYPES:
            reasons.append("Manager notes QA clearance still pending.")

        if (claim.get("observed_at") or "") > (audit.get("observed_at") or ""):
            reasons.append("A newer worker report exists since the last audit.")

        return ("DISCREPANCY" if discrepancy else "CONFIRMED"), variance_pct, reasons
