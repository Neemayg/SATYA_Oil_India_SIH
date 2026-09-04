"""
SATYA Content Normalization Engine
Segments raw source content into fragments, normalizes character encoding and whitespace,
resolves relative temporal terms ("today", "yesterday") safely, and attaches machine-resolvable provenance pointers.
"""

import json
import re
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from backend.models.domain_models import SourceDocument, SourceFragment, SourceType, PipelineState

class ContentNormalizationService:

    def normalize_text(self, text: str) -> str:
        """Cleans whitespace and encoding artifacts without stripping domain terms."""
        if not text:
            return ""
        # Strip non-printable unicode artifacts while preserving standard text
        cleaned = text.replace('\r\n', '\n').replace('\r', '\n')
        # Collapse multiple spaces
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        return cleaned.strip()

    def resolve_relative_date(self, text: str, reference_date_str: Optional[str]) -> Tuple[Optional[str], str, str]:
        """
        Resolves relative temporal expressions like 'today', 'yesterday' against reference_date_str.
        Returns (resolved_date_iso, resolution_status, explanation).
        Does NOT invent a date if unresolvable.
        """
        lower_text = text.lower()
        has_relative = "yesterday" in lower_text or "today" in lower_text or "this shift" in lower_text

        # First check for explicit date in text
        iso_match = re.search(r'\b(20\d{2}-\d{2}-\d{2})\b', text)
        if iso_match:
            return iso_match.group(1), "EXPLICIT_DATE", "Extracted explicit ISO date"

        dmy_match = re.search(r'\b(\d{2})[-/](\d{2})[-/](20\d{2})\b', text)
        if dmy_match:
            day, month, year = dmy_match.groups()
            return f"{year}-{month}-{day}", "EXPLICIT_DATE", "Extracted explicit DMY date"

        # Try parsing reference date for relative resolution
        ref_dt = None
        if reference_date_str:
            try:
                if 'T' in reference_date_str:
                    ref_dt = datetime.fromisoformat(reference_date_str.replace('Z', '+00:00'))
                else:
                    ref_dt = datetime.strptime(reference_date_str[:10], "%Y-%m-%d")
            except Exception:
                ref_dt = None

        if has_relative:
            if not ref_dt:
                return None, "UNRESOLVED_RELATIVE_DATE", "Relative date term present but reference submission date is missing or invalid"
            if "yesterday" in lower_text:
                res_dt = ref_dt - timedelta(days=1)
                return res_dt.strftime("%Y-%m-%d"), "RESOLVED_RELATIVE_DATE", "Resolved relative phrase 'yesterday'"
            elif "today" in lower_text or "this shift" in lower_text:
                return ref_dt.strftime("%Y-%m-%d"), "RESOLVED_RELATIVE_DATE", "Resolved relative phrase 'today'"

        if ref_dt:
            return ref_dt.strftime("%Y-%m-%d"), "FALLBACK_SUBMISSION_DATE", "Defaulted to submission reference date"
        
        return None, "MISSING_DATE", "No explicit or relative date found in text or submission metadata"

    def fragment_document(self, doc: SourceDocument) -> List[SourceFragment]:
        """
        Segments SourceDocument into Machine-Resolvable SourceFragments.
        Supports JSON synthetic payloads, multi-line text, and CSV/Excel rows.
        """
        fragments: List[SourceFragment] = []
        raw_content = doc.raw_content

        # Case 1: JSON Synthetic Payload
        if doc.source_type == SourceType.JSON_SYNTHETIC or raw_content.strip().startswith('{'):
            try:
                data = json.loads(raw_content)
                records = data.get("records", [data]) if isinstance(data, dict) else data
                for idx, rec in enumerate(records):
                    snippet = rec.get("raw_snippet", json.dumps(rec))
                    loc_type = "JSON_RECORD"
                    loc_val = rec.get("locator", f"Record[{idx}]")
                    
                    frag = SourceFragment(
                        fragment_id=f"FRG-{uuid.uuid4().hex[:8].upper()}",
                        source_id=doc.source_id,
                        fragment_index=idx,
                        raw_text=snippet,
                        normalized_text=self.normalize_text(snippet),
                        locator_type=loc_type,
                        locator_value=str(loc_val)
                    )
                    fragments.append(frag)
                return fragments
            except Exception:
                pass  # Fallback to line-by-line parsing if JSON parse fails

        # Case 2: Multi-Line Text / PDF / Site Log
        lines = raw_content.split('\n')
        line_idx = 0
        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith('#'):
                continue
            
            loc_type = "TEXT_LINE" if doc.source_type != SourceType.DPR_PDF else "PDF_LINE"
            loc_val = f"Line {line_idx + 1}"
            
            frag = SourceFragment(
                fragment_id=f"FRG-{uuid.uuid4().hex[:8].upper()}",
                source_id=doc.source_id,
                fragment_index=line_idx,
                raw_text=line_str,
                normalized_text=self.normalize_text(line_str),
                locator_type=loc_type,
                locator_value=loc_val
            )
            fragments.append(frag)
            line_idx += 1

        doc.extraction_status = PipelineState.NORMALIZED
        return fragments
