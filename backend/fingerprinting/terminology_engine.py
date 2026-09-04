"""
SATYA Terminology Intelligence Engine
Provides domain-specific abbreviation expansion, technical synonym generation,
field alias resolution, and action verb / entity noun extraction for Oil & Gas EPC schedules.
"""

import re
from typing import List, Set, Dict, Tuple

class TerminologyIntelligenceEngine:
    """Oil & Gas EPC domain lexicon and terminology intelligence service."""

    def __init__(self):
        # EPC Abbreviation & Acronym Expansion Dictionary
        self.abbreviations: Dict[str, List[str]] = {
            "ROW": ["Right of Way", "ROW Clearing", "Ground Clearance", "Site Access Strip"],
            "HDD": ["Horizontal Directional Drilling", "River Crossing", "Sub-surface Drilling", "Pullback"],
            "GGS": ["Gas Gathering Station", "Gathering Terminal", "GGS Facility"],
            "NDT": ["Non-Destructive Testing", "Radiography", "Ultrasonic Testing", "Weld Quality Check"],
            "TPIA": ["Third Party Inspection Agency", "Third Party Inspection", "Clearance Certificate"],
            "DCS": ["Distributed Control System", "Control System", "PLC Panel"],
            "CS": ["Carbon Steel", "CS Pipe"],
            "SS": ["Stainless Steel", "SS Spool"],
            "NB": ["Nominal Bore", "Pipe Diameter"],
            "OD": ["Outer Diameter"],
            "WT": ["Wall Thickness"],
            "PTW": ["Permit to Work", "Safety Permit"],
            "NCR": ["Non-Conformance Report", "Defect Notice"],
            "FAT": ["Factory Acceptance Test"],
            "SAT": ["Site Acceptance Test"],
            "P&ID": ["Piping & Instrumentation Diagram"],
            "WBS": ["Work Breakdown Structure"],
            "CPM": ["Critical Path Method"]
        }

        # Technical Concept Synonyms & Field Jargon Aliases
        self.term_synonyms: Dict[str, List[str]] = {
            "clearing": ["grading", "grubbing", "row prep", "ground levelling", "bush clearing", "site clearing"],
            "trenching": ["excavation", "ditching", "dug", "trench digging", "earth cutting"],
            "welding": ["stringing", "jointing", "girth weld", "weld seam", "spool welding", "tie-in weld"],
            "lowering": ["lowering-in", "pipe laying", "trench lowering", "bedding"],
            "backfilling": ["backfill", "trench cover", "mounding", "soil compaction"],
            "hydrotest": ["hydrostatic test", "pressure test", "strength test", "leak test"],
            "erection": ["assembly", "fit-up", "mounting", "structural placement", "positioning"],
            "concreting": ["civil foundation", "pouring", "shuttering", "rebar placement", "curing"],
            "pullback": ["hdd pullback", "pipe pull", "reaming", "pilot hole"],
            "substation": ["transformer", "switchgear", "earthing", "power shelter"],
            "manifold": ["header", "valve station", "skid", "piping cluster"]
        }

        # Action Verbs Inventory
        self.action_verbs: Set[str] = {
            "clearing", "grading", "trenching", "excavation", "welding", "stringing",
            "lowering", "backfilling", "hydrotest", "erection", "concreting", "pullback",
            "installation", "commissioning", "testing", "calibration", "glanding",
            "termination", "pigging", "radiography", "alignment", "fabrication",
            "pouring", "sandblasting", "painting", "insulation", "wrapping"
        }

    def expand_abbreviations(self, text: str) -> List[str]:
        """Expands domain abbreviations present in text into full technical phrases."""
        expansions: List[str] = []
        tokens = re.findall(r'\b[A-Z0-9&\-]{2,8}\b', text)
        for t in tokens:
            t_upper = t.upper()
            if t_upper in self.abbreviations:
                expansions.extend(self.abbreviations[t_upper])
        return list(set(expansions))

    def extract_action_verbs(self, text: str) -> List[str]:
        """Extracts primary action verbs from activity name or statement."""
        lower = text.lower()
        words = re.findall(r'\b[a-z]{3,15}\b', lower)
        found = [w for w in words if w in self.action_verbs]
        return list(set(found))

    def extract_entity_nouns(self, text: str) -> List[str]:
        """Extracts domain entity nouns (e.g. pipeline, vessel, spool, transformer, ROW)."""
        lower = text.lower()
        entities = []
        domain_nouns = [
            "pipeline", "mainline", "row", "trench", "spool", "vessel", "pump",
            "compressor", "transformer", "cable", "substation", "dcs", "panel",
            "valve", "header", "manifold", "dyke", "foundation", "shelter",
            "joint", "crossing", "river", "well-pad", "tank", "flare", "separator"
        ]
        for n in domain_nouns:
            if re.search(r'\b' + re.escape(n) + r'\b', lower):
                entities.append(n)
        return entities

    def generate_synonyms_and_aliases(self, text: str) -> Tuple[List[str], List[str]]:
        """Generates technical synonyms and real-world field jargon aliases for text."""
        synonyms: Set[str] = set()
        field_aliases: Set[str] = set()
        lower = text.lower()

        for term, syns in self.term_synonyms.items():
            if term in lower:
                for s in syns:
                    synonyms.add(s)
                    field_aliases.add(s)

        # Add abbreviation expansions to field aliases
        expansions = self.expand_abbreviations(text)
        for exp in expansions:
            field_aliases.add(exp.lower())

        return list(synonyms), list(field_aliases)

    def generate_search_tokens(self, text: str, wbs_path: str, discipline: str) -> List[str]:
        """Builds comprehensive token set for fast text search and semantic matching."""
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text + " " + wbs_path + " " + discipline).lower()
        tokens = set(clean_text.split())
        
        # Add expansions
        expansions = self.expand_abbreviations(text)
        for exp in expansions:
            tokens.update(exp.lower().split())

        # Remove common stop words
        stopwords = {"and", "the", "for", "in", "at", "of", "to", "a", "an", "with", "by", "on"}
        tokens = {t for t in tokens if t not in stopwords and len(t) > 1}
        return list(tokens)
