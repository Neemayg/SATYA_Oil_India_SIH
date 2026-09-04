"""
SATYA Execution Event Extraction Engine
Parses normalized fragments into structured ExecutionEvent instances.
Uses deterministic regex entity extraction for actions, quantities, units, locations, equipment tags,
shift context, pending QA clearances, and explicit Activity IDs.
DO NOT INVENT ACTIVITY IDs. DO NOT PERFORM SCHEDULE MATCHING.
"""

import re
import uuid
from typing import Optional, List, Tuple, Dict, Any
from backend.models.domain_models import (
    SourceDocument, SourceFragment, ExecutionEvent, ProvenanceRecord,
    EventType, PipelineState
)
from backend.normalization.content_normalization import ContentNormalizationService

class ExecutionEventExtractionService:
    def __init__(self):
        self.normalizer = ContentNormalizationService()

        # Action Keywords Taxonomy
        self.action_keywords = {
            EventType.START: ["commenced", "started", "initiated", "taken up", "begun"],
            EventType.FINISH: ["completed", "finished", "done", "ended", "concluded"],
            EventType.QA_CLEARANCE: ["clearance", "cleared", "passed ndt", "radiography clear", "qc sign-off"],
            EventType.HOLD: ["halted", "stuck", "pending clearance", "rework required", "failed ndt", "stopped"],
            EventType.INSPECTION: ["inspection", "inspected", "tested", "hydrotest", "megger test"],
            EventType.PROGRESS: ["trenching", "welding", "erection", "pullback", "clearing", "grading", "lowering", "backfilling", "laying", "pulling"]
        }

        # Discipline Keywords Taxonomy
        self.discipline_keywords = {
            "CIVIL": ["trench", "row", "grading", "grubbing", "excavation", "backfill", "lowering", "dyke", "concreting", "foundation", "earthworks", "civ"],
            "PIPING": ["weld", "welding", "spool", "stringing", "hdd", "pullback", "hydrotest", "manifold", "header", "pipeline", "joint", "pip", "trunkline"],
            "STRUCTURAL": ["steel", "structural", "pipe rack", "shelter", "erection", "anchor bolt", "crane structure", "str"],
            "MECHANICAL": ["pump", "vessel", "separator", "compressor", "flare stack", "p-301", "v-101", "k-201", "mec"],
            "ELECTRICAL": ["transformer", "cable", "earthing", "megger", "glanding", "substation", "ele"],
            "INSTRUMENTATION": ["dcs", "panel", "transmitter", "pt-101", "loop", "calibration", "ins"],
            "QA_QC": ["ndt", "radiography", "ultrasonic", "tpia", "non-conformance", "ncr", "radiogr", "qa_"],
            "SAFETY_HSE": ["fire water", "ptw", "permit", "safety", "hydrant"]
        }

        # Common Units of Measure
        self.uom_patterns = [
            (r'meters?|m|kms?', "Meters"),
            (r'joints?|jts?', "Joints"),
            (r'spools?', "Spools"),
            (r'cu\.?m|cubic meters?', "Cu.M"),
            (r'sq\.?m|square meters?', "Sq.M"),
            (r'mt|metric tons?', "MT"),
            (r'items?|nos|numbers?', "Item"),
            (r'loops?', "Loops"),
            (r'percent|%', "Percent")
        ]

    def extract_activity_id(self, text: str) -> Optional[str]:
        """Extracts explicit Activity ID (e.g. ACT-1010 or ACT-SCP-8010) if present in raw text."""
        match = re.search(r'\b(ACT-(?:SCP-)?\d{4})\b', text, re.IGNORECASE)
        return match.group(1).upper() if match else None

    def infer_event_type(self, text: str) -> str:
        """Infers event type from action verbs."""
        lower = text.lower()
        if any(w in lower for w in ["failed", "rework required", "halted", "stopped"]):
            return EventType.HOLD
        if any(w in lower for w in ["cleared", "passed", "clearance cert"]):
            return EventType.QA_CLEARANCE
        if any(w in lower for w in ["completed", "finished", "100% done", "100% completed"]):
            return EventType.FINISH
        if any(w in lower for w in ["started", "commenced", "initiated"]):
            return EventType.START
        if any(w in lower for w in ["trenching", "welding", "erection", "pullback", "grading", "lowering", "backfilling", "progress"]):
            return EventType.PROGRESS
        return EventType.UNKNOWN

    def infer_discipline(self, text: str) -> str:
        """Infers discipline from technical keywords."""
        lower = text.lower()
        for disc, keywords in self.discipline_keywords.items():
            if any(k in lower for k in keywords):
                return disc
        return "UNKNOWN"

    def extract_quantity_and_uom(self, text: str) -> Tuple[Optional[float], Optional[str]]:
        """Extracts numeric quantity and standardized Unit of Measure."""
        # Search for numbers followed specifically by valid UOM patterns
        for pattern, std_uom in self.uom_patterns:
            regex = r'\b(\d+(?:\.\d+)?)\s*(?:' + pattern + r')(?!\w)'
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                return float(match.group(1)), std_uom
        return None, None

    def extract_real_world_fields(self, text: str) -> Tuple[Optional[str], bool, Optional[float], Optional[str]]:
        """
        Extracts Phase 4.5 real-world inspired fields:
        (shift_context, pending_qa_clearance, remaining_quantity, work_front_tag)
        """
        lower = text.lower()
        
        # Shift Context
        shift = None
        if "night shift" in lower:
            shift = "NIGHT_SHIFT"
        elif "day shift" in lower or "1st shift" in lower:
            shift = "DAY_SHIFT"
        elif "shift 2" in lower or "2nd shift" in lower:
            shift = "SHIFT_2"

        # Pending QA Clearance
        pending_qa = any(w in lower for w in ["clearance awaited", "clearance pending", "pending clearance", "pending qa", "pending ndt", "rework required", "failed ndt"])

        # Remaining Quantity
        rem_qty = None
        rem_match = re.search(r'\b(balance|remaining)\s+(\d+(?:\.\d+)?)\b', lower)
        if rem_match:
            rem_qty = float(rem_match.group(2))

        # Work Front Tag
        work_front = None
        wf_match = re.search(r'\b(front\s+[a-z0-9]+|well-pad\s+[a-z0-9]+|sector\s+[a-z0-9]+)\b', lower)
        if wf_match:
            work_front = wf_match.group(1).title()

        return shift, pending_qa, rem_qty, work_front

    def extract_location_or_chainage(self, text: str) -> Optional[str]:
        """Extracts location or chainage interval (e.g. Km 14.100 - 14.280 or Ch 12+400)."""
        chainage_match = re.search(r'\b(km\s*\d+(?:\.\d+)?(?:\s*to\s*\d+(?:\.\d+)?)?|ch\s*\d+\+\d+)\b', text, re.IGNORECASE)
        if chainage_match:
            return chainage_match.group(1)
        
        area_match = re.search(r'\b(section\s*\d+|ggs-3|tank farm\s*\d+|river crossing|spread\s*[a-z])\b', text, re.IGNORECASE)
        if area_match:
            return area_match.group(1).title()

        return None

    def calculate_extraction_confidence(
        self,
        event_type: str,
        discipline: str,
        qty: Optional[float],
        act_id: Optional[str],
        loc: Optional[str]
    ) -> float:
        """Calculates explicit Extraction Confidence score [0.0, 1.0]."""
        score = 0.40  # Base extraction score
        
        if event_type != EventType.UNKNOWN:
            score += 0.15
        if discipline != "UNKNOWN":
            score += 0.15
        if qty is not None:
            score += 0.15
        if loc is not None:
            score += 0.10
        if act_id is not None:
            score += 0.05

        return min(1.0, round(score, 2))

    def split_into_action_clauses(self, text: str) -> List[str]:
        """Splits compound statements into individual action clauses when distinct actions are present."""
        # Protect common abbreviations from splitting on period
        protected_text = re.sub(r'\b(approx|no|sec|km|vol|ref|drg)\.', r'\1_DOT_', text, flags=re.IGNORECASE)
        raw_clauses = re.split(r';|\.|\b(?:and|while|plus)\b', protected_text, flags=re.IGNORECASE)
        clauses = []
        for c in raw_clauses:
            cleaned = c.strip().replace('_DOT_', '.').replace('_dot_', '.')
            if cleaned and len(cleaned) > 3:
                clauses.append(cleaned)

        if len(clauses) <= 1:
            return [text]

        valid_clauses = []
        for c in clauses:
            if self.infer_event_type(c) != EventType.UNKNOWN or any(w in c.lower() for w in ["pending", "qa", "clearance", "balance", "rework"]):
                valid_clauses.append(c)

        if valid_clauses:
            return valid_clauses

        return [text]

    def build_field_provenance_map(
        self,
        full_text: str,
        event_type: str,
        raw_act_id: Optional[str],
        qty: Optional[float],
        uom: Optional[str],
        discipline: str,
        location: Optional[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Builds field-level provenance map with exact character start/end spans."""
        prov_map: Dict[str, Dict[str, Any]] = {}
        lower_text = full_text.lower()

        # Action / Event Type Span
        if event_type != EventType.UNKNOWN:
            verbs = self.action_keywords.get(event_type, [])
            for v in verbs:
                idx = lower_text.find(v)
                if idx != -1:
                    prov_map["event_type"] = {
                        "start_char": idx,
                        "end_char": idx + len(v),
                        "snippet": full_text[idx:idx + len(v)]
                    }
                    break

        # Raw Activity ID Span
        if raw_act_id:
            idx = full_text.find(raw_act_id)
            if idx != -1:
                prov_map["raw_observed_activity_id"] = {
                    "start_char": idx,
                    "end_char": idx + len(raw_act_id),
                    "snippet": raw_act_id
                }

        # Quantity Span
        if qty is not None:
            qty_str = str(int(qty)) if qty.is_integer() else str(qty)
            match = re.search(r'\b(' + re.escape(qty_str) + r'\s*[a-zA-Z%]+)\b', full_text, re.IGNORECASE)
            if match:
                idx = match.start(1)
                end_pos = match.end(1)
                prov_map["observed_quantity"] = {
                    "start_char": idx,
                    "end_char": end_pos,
                    "snippet": match.group(1)
                }
            else:
                idx = full_text.find(qty_str)
                if idx != -1:
                    prov_map["observed_quantity"] = {
                        "start_char": idx,
                        "end_char": idx + len(qty_str),
                        "snippet": qty_str
                    }

        # Discipline Span
        if discipline != "UNKNOWN":
            disc_keywords = self.discipline_keywords.get(discipline, [])
            for k in disc_keywords:
                idx = lower_text.find(k)
                if idx != -1:
                    prov_map["discipline"] = {
                        "start_char": idx,
                        "end_char": idx + len(k),
                        "snippet": full_text[idx:idx + len(k)]
                    }
                    break

        # Location Span
        if location:
            idx = full_text.find(location)
            if idx != -1:
                prov_map["area_location"] = {
                    "start_char": idx,
                    "end_char": idx + len(location),
                    "snippet": location
                }

        return prov_map

    def extract_events_from_fragment(
        self,
        doc: SourceDocument,
        frag: SourceFragment
    ) -> List[ExecutionEvent]:
        """
        Extracts one or more ExecutionEvents from a single SourceFragment.
        Handles compound statements (1 Fragment -> Multiple ExecutionEvents).
        """
        raw_text = frag.raw_text
        clauses = self.split_into_action_clauses(raw_text)
        events: List[ExecutionEvent] = []

        # Shared document-level activity ID if clause doesn't repeat it
        frag_act_id = self.extract_activity_id(raw_text)

        for clause_idx, clause in enumerate(clauses):
            clause_act_id = self.extract_activity_id(clause) or frag_act_id
            event_type = self.infer_event_type(clause)
            discipline = self.infer_discipline(clause)
            qty, uom = self.extract_quantity_and_uom(clause)
            location = self.extract_location_or_chainage(clause)
            shift, pending_qa, rem_qty, work_front = self.extract_real_world_fields(clause)

            obs_date, date_status, date_reason = self.normalizer.resolve_relative_date(clause, doc.submitted_at)

            confidence = self.calculate_extraction_confidence(event_type, discipline, qty, clause_act_id, location)
            event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"

            field_prov = self.build_field_provenance_map(clause, event_type, clause_act_id, qty, uom, discipline, location)

            provenance = ProvenanceRecord(
                provenance_id=f"PRV-{uuid.uuid4().hex[:8].upper()}",
                event_id=event_id,
                source_id=doc.source_id,
                source_type=doc.source_type,
                locator_type=frag.locator_type,
                locator_value=f"{frag.locator_value}#clause[{clause_idx}]" if len(clauses) > 1 else frag.locator_value,
                raw_text_snippet=clause,
                field_provenance_map=field_prov
            )

            event = ExecutionEvent(
                event_id=event_id,
                source_id=doc.source_id,
                fragment_id=frag.fragment_id,
                event_type=event_type,
                observed_timestamp=obs_date,
                source_timestamp=doc.submitted_at,
                extracted_statement=clause,
                raw_observed_activity_id=clause_act_id,  # Raw explicit ID preserved
                observed_activity_id=None,  # Set by guardrail after validation
                activity_id_validation_status="UNVALIDATED",
                temporal_resolution_status=date_status,
                temporal_resolution_basis=date_reason,
                discipline=discipline,
                area_location=location,
                equipment_tag=None,
                line_number=None,
                observed_quantity=qty,
                unit_of_measure=uom,
                progress_percent=100.0 if event_type == EventType.FINISH else None,
                status_text=f"Extracted: {event_type}",
                extraction_confidence=confidence,
                lifecycle_state=PipelineState.EXTRACTED,
                shift_context=shift,
                pending_qa_clearance=pending_qa,
                remaining_quantity=rem_qty,
                work_front_tag=work_front,
                provenance=provenance
            )
            events.append(event)

        return events

    def extract_event_from_fragment(
        self,
        doc: SourceDocument,
        frag: SourceFragment
    ) -> ExecutionEvent:
        """Backwards compatible single-event extraction wrapper."""
        events = self.extract_events_from_fragment(doc, frag)
        return events[0]
