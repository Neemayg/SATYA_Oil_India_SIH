"""
SATYA Evidence, Confidence & Conflict Engine Unit Tests (Phase 8)
"""

import unittest
from datetime import datetime
from backend.models.domain_models import (
    ExecutionEvent, SourceDocument, SourceFragment, MatchResult, MatchOutcome,
    Evidence, EvidenceClaim, ClaimType, CorroborationStatus, TrustStatus, ConflictSeverity,
    ConflictType
)
from backend.persistence.database_engine import DatabaseEngine
from backend.evidence.claim_extractor import ClaimExtractor
from backend.evidence.reliability_evaluator import ReliabilityEvaluator
from backend.evidence.corroboration_engine import CorroborationEngine
from backend.evidence.gap_engine import GapEngine
from backend.evidence.conflict_engine import ConflictEngine
from backend.services.trust_evaluator_service import TrustEvaluatorService

class TestEvidenceEngine(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseEngine(":memory:")
        self.trust_service = TrustEvaluatorService(self.db)
        self.claim_extractor = ClaimExtractor()
        self.reliability_evaluator = ReliabilityEvaluator()
        self.corroboration_engine = CorroborationEngine()
        self.gap_engine = GapEngine()
        self.conflict_engine = ConflictEngine()

    def test_claim_extraction_multiple_claims(self):
        event = ExecutionEvent(
            event_id="EVT-1001",
            source_id="SRC-1001",
            fragment_id="FRG-1001",
            event_type="PROGRESS",
            observed_timestamp="2026-09-02",
            source_timestamp="2026-09-02T10:00:00",
            extracted_statement="Mainline trenching 400m completed on PL-16-01, QA pending.",
            discipline="PIPING",
            line_number="PL-16-01",
            observed_quantity=400.0,
            unit_of_measure="METER",
            progress_percent=100.0,
            pending_qa_clearance=True,
            extraction_confidence=0.95
        )
        evidence = Evidence(
            evidence_id="EVD-1001",
            event_id="EVT-1001",
            source_id="SRC-1001",
            fragment_id="FRG-1001",
            locator_type="EXCEL_CELL",
            locator_value="Sheet1!B12",
            source_type="DPR_EXCEL",
            origin_group_id="SRC-1001",
            raw_text_snippet=event.extracted_statement,
            observed_timestamp="2026-09-02"
        )

        claims = self.claim_extractor.extract_claims(event, evidence)
        claim_types = [c.claim_type for c in claims]

        self.assertIn(ClaimType.PROGRESS_CLAIM, claim_types)
        self.assertIn(ClaimType.QUANTITY_CLAIM, claim_types)
        self.assertIn(ClaimType.QA_CLAIM, claim_types)
        self.assertIn(ClaimType.LOCATION_CLAIM, claim_types)
        self.assertIn(ClaimType.TEMPORAL_CLAIM, claim_types)

        qa_claim = next(c for c in claims if c.claim_type == ClaimType.QA_CLAIM)
        self.assertEqual(qa_claim.claim_value["qa_status"], "PENDING")

    def test_multi_factor_evidence_reliability(self):
        evidence_high = Evidence(
            evidence_id="EVD-HIGH",
            event_id="EVT-1001",
            source_id="SRC-QA",
            fragment_id="FRG-QA",
            locator_type="PDF_LINE",
            locator_value="Line 42",
            source_type="QA_REPORT",
            origin_group_id="SRC-QA",
            raw_text_snippet="TPIA QA Inspection Cleared.",
            observed_timestamp="2026-09-02",
            provenance_map={"status": {"start_char": 0, "end_char": 20, "snippet": "TPIA QA Inspection Cleared."}}
        )
        source_doc = SourceDocument(
            source_id="SRC-QA",
            project_id="PRJ-NBG-2026",
            source_type="QA_REPORT",
            file_name="qa_cert.pdf",
            sha256_hash="abc123hash",
            raw_content="...",
            submitted_at="2026-09-02",
            received_at="2026-09-02",
            author="Third Party Inspector"
        )

        rel = self.reliability_evaluator.evaluate_reliability(evidence_high, source_doc)
        self.assertGreaterEqual(rel.overall_reliability_score, 0.75)
        self.assertEqual(rel.reliability_tier, "HIGH")

    def test_corroboration_origin_grouping(self):
        ev1 = Evidence("EVD-1", "EVT-1", "SRC-DPR", "FRG-1", "EXCEL_CELL", "A1", "DPR_EXCEL", "ORIGIN-CONTRACTOR", "DPR statement")
        ev2 = Evidence("EVD-2", "EVT-1", "SRC-EMAIL", "FRG-2", "TEXT_SPAN", "Line 1", "TEXT_DOCUMENT", "ORIGIN-CONTRACTOR", "Forwarded DPR statement")
        ev3 = Evidence("EVD-3", "EVT-1", "SRC-QA", "FRG-3", "PDF_LINE", "Line 5", "QA_REPORT", "ORIGIN-TPIA", "Independent QA log")

        # Case 1: Re-quoted same origin (DPR + Email quoting DPR) -> CORROBORATED_SAME_ORIGIN
        assessment_same = self.corroboration_engine.evaluate_corroboration("EVT-1", [ev1, ev2], [], [])
        self.assertEqual(assessment_same.corroboration_status, CorroborationStatus.CORROBORATED_SAME_ORIGIN)
        self.assertEqual(assessment_same.unique_origin_count, 1)

        # Case 2: Independent origins (DPR + Independent QA) -> CORROBORATED_INDEPENDENT
        assessment_ind = self.corroboration_engine.evaluate_corroboration("EVT-1", [ev1, ev3], [], [])
        self.assertEqual(assessment_ind.corroboration_status, CorroborationStatus.CORROBORATED_INDEPENDENT)
        self.assertEqual(assessment_ind.unique_origin_count, 2)

    def test_discipline_aware_evidence_gaps(self):
        event_piping = ExecutionEvent(
            event_id="EVT-PIP",
            source_id="SRC-1",
            fragment_id="FRG-1",
            event_type="FINISH",
            observed_timestamp="2026-09-02",
            source_timestamp="2026-09-02",
            extracted_statement="Mainline welding 100% complete.",
            discipline="PIPING",
            progress_percent=100.0,
            pending_qa_clearance=True,
            extraction_confidence=0.9
        )
        ev_pip = Evidence("EVD-P", "EVT-PIP", "SRC-1", "FRG-1", "TEXT_SPAN", "Line 1", "DPR_EXCEL", "ORIGIN-1", "Mainline welding 100% complete.")
        claims_pip = self.claim_extractor.extract_claims(event_piping, ev_pip)

        # Piping completion without QA passed triggers MISSING_QA_CLEARANCE gap
        gaps_pip = self.gap_engine.detect_gaps(event_piping, claims_pip, [ev_pip], CorroborationStatus.UNCORROBORATED)
        self.assertTrue(any("MISSING_QA_CLEARANCE" in g for g in gaps_pip))

        # Civil excavation completion does NOT trigger mandatory QA gap under civil policy
        event_civil = ExecutionEvent(
            event_id="EVT-CIV",
            source_id="SRC-1",
            fragment_id="FRG-2",
            event_type="FINISH",
            observed_timestamp="2026-09-02",
            source_timestamp="2026-09-02",
            extracted_statement="Earthwork excavation 100% complete.",
            discipline="CIVIL",
            progress_percent=100.0,
            extraction_confidence=0.9
        )
        ev_civ = Evidence("EVD-C", "EVT-CIV", "SRC-1", "FRG-2", "TEXT_SPAN", "Line 2", "DPR_EXCEL", "ORIGIN-1", "Earthwork excavation 100% complete.")
        claims_civ = self.claim_extractor.extract_claims(event_civil, ev_civ)
        gaps_civ = self.gap_engine.detect_gaps(event_civil, claims_civ, [ev_civ], CorroborationStatus.UNCORROBORATED)
        self.assertFalse(any("MISSING_QA_CLEARANCE" in g for g in gaps_civ))

    def test_conflict_engine_qa_conflict(self):
        event = ExecutionEvent("EVT-1", "SRC-1", "FRG-1", "FINISH", "2026-09-02", "2026-09-02", "Valve installation complete, QA rejected.", progress_percent=100.0, extraction_confidence=0.9)
        ev = Evidence("EVD-1", "EVT-1", "SRC-1", "FRG-1", "TEXT_SPAN", "Line 1", "DPR_EXCEL", "ORIGIN-1", event.extracted_statement)
        claims = self.claim_extractor.extract_claims(event, ev)

        conflicts = self.conflict_engine.detect_conflicts(event, claims, [ev], [], [])
        self.assertTrue(any(c.conflict_type == ConflictType.QA_CONFLICT for c in conflicts))
        self.assertEqual(conflicts[0].severity, ConflictSeverity.CRITICAL)

    def test_conflict_engine_reporting_delay_not_false_temporal_conflict(self):
        # Claim observed date is 2026-09-01, but submission date is 3 days later (2026-09-04)
        event = ExecutionEvent("EVT-1", "SRC-1", "FRG-1", "PROGRESS", "2026-09-01", "2026-09-04T18:00:00", "Work done on 1 Sep.", progress_percent=50.0, extraction_confidence=0.9)
        ev = Evidence("EVD-1", "EVT-1", "SRC-1", "FRG-1", "TEXT_SPAN", "Line 1", "DPR_EXCEL", "ORIGIN-1", event.extracted_statement, observed_timestamp="2026-09-01")
        claims = self.claim_extractor.extract_claims(event, ev)

        conflicts = self.conflict_engine.detect_conflicts(event, claims, [ev], [], [])
        # Submission delay should NOT trigger false TEMPORAL_CONFLICT
        self.assertFalse(any(c.conflict_type == ConflictType.TEMPORAL_CONFLICT for c in conflicts))

    def test_trust_assessment_with_no_evidence(self):
        # Event with high match confidence (0.90) but ZERO evidence records
        event = ExecutionEvent("EVT-NOEV", "SRC-1", "FRG-1", "PROGRESS", "2026-09-02", "2026-09-02", "Some statement", extraction_confidence=0.9)
        match_res = MatchResult("MTH-1", "EVT-NOEV", "SRC-1", MatchOutcome.MATCHED, "ACT-1010", "Mainline Trenching", 0.90)

        # Evaluate trust passing create_primary_evidence=False
        ta = self.trust_service.evaluate_trust_for_event(event, match_res, create_primary_evidence=False)
        # High schedule match MUST NOT compensate for zero evidence!
        self.assertNotEqual(ta.trust_status, TrustStatus.TRUSTED)

    def test_later_evidence_changes_trust_without_mutating_history(self):
        event = ExecutionEvent("EVT-HIST", "SRC-1", "FRG-1", "FINISH", "2026-09-02", "2026-09-02", "Mainline welding complete.", discipline="PIPING", line_number="PL-16-01", progress_percent=100.0, pending_qa_clearance=True, extraction_confidence=0.9)
        match_res = MatchResult("MTH-1", "EVT-HIST", "SRC-1", MatchOutcome.MATCHED, "ACT-1010", "Mainline Welding", 0.90)

        # v1: Initial evaluation with pending QA clearance -> REVIEW_REQUIRED
        ta_v1 = self.trust_service.evaluate_trust_for_event(event, match_res)
        self.assertEqual(ta_v1.version_index, 1)
        self.assertEqual(ta_v1.trust_status, TrustStatus.REVIEW_REQUIRED)

        # v2: Later QA clearance evidence arrives from independent TPIA origin
        ev_qa = Evidence("EVD-QA-PASS", "EVT-HIST", "SRC-QA-DOC", "FRG-QA", "PDF_LINE", "Line 10", "QA_REPORT", "ORIGIN-TPIA", "QA NDT Passed", observed_timestamp="2026-09-03")
        event.pending_qa_clearance = False
        event.extracted_statement = "Mainline welding complete. QA cleared."

        doc_qa = SourceDocument("SRC-QA-DOC", "PRJ-NBG-2026", "QA_REPORT", "qa.pdf", "hash123", "...", "2026-09-03", "2026-09-03", author="TPIA Inspector")

        ta_v2 = self.trust_service.evaluate_trust_for_event(event, match_res, source_doc=doc_qa, additional_evidence=[ev_qa])
        self.assertEqual(ta_v2.version_index, 2)
        self.assertEqual(ta_v2.trust_status, TrustStatus.TRUSTED)

        # Verify historical v1 remains intact in database!
        history = self.db.get_trust_assessments_by_event("EVT-HIST")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["version_index"], 1)
        self.assertEqual(history[0]["trust_status"], TrustStatus.REVIEW_REQUIRED)
        self.assertEqual(history[1]["version_index"], 2)
        self.assertEqual(history[1]["trust_status"], TrustStatus.TRUSTED)

if __name__ == "__main__":
    unittest.main()
