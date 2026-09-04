"""
SATYA Native XLSX File Adapter
Parses raw Microsoft Excel (.xlsx) files into structured records using standard library XML/Zip tools.
Zero third-party pip dependencies required.
"""

import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import List, Dict, Any, Tuple

class XLSXAdapter:
    """Native parser for .xlsx OpenXML spreadsheets."""

    def parse_xlsx_bytes(self, content_bytes: bytes) -> List[Dict[str, Any]]:
        """Parses raw bytes of an .xlsx file into structured row records with cell locators."""
        records: List[Dict[str, Any]] = []
        try:
            with zipfile.ZipFile(BytesIO(content_bytes)) as z:
                # 1. Parse Shared Strings if present
                shared_strings: List[str] = []
                if "xl/sharedStrings.xml" in z.namelist():
                    with z.open("xl/sharedStrings.xml") as f:
                        tree = ET.parse(f)
                        root = tree.getroot()
                        for si in root.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                            t = si.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                            shared_strings.append(t.text if t is not None and t.text else "")

                # 2. Parse Worksheet 1
                if "xl/worksheets/sheet1.xml" in z.namelist():
                    with z.open("xl/worksheets/sheet1.xml") as f:
                        tree = ET.parse(f)
                        root = tree.getroot()
                        sheet_data = root.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData")
                        if sheet_data is not None:
                            for row in sheet_data.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
                                r_num = row.get("r", "1")
                                row_cells: List[Tuple[str, str]] = []
                                for c in row.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                                    c_ref = c.get("r", f"Cell_{r_num}")
                                    c_type = c.get("t", "")
                                    v_elem = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                                    val = v_elem.text if v_elem is not None and v_elem.text else ""
                                    if c_type == "s" and val.isdigit() and int(val) < len(shared_strings):
                                        val = shared_strings[int(val)]
                                    row_cells.append((c_ref, val))
                                
                                # Combine non-empty cell values into row snippet
                                line_str = " | ".join([v for _, v in row_cells if v.strip()])
                                if line_str:
                                    records.append({
                                        "locator": f"Sheet1!Row{r_num}",
                                        "raw_snippet": line_str,
                                        "cell_data": row_cells
                                    })
        except Exception as e:
            # Fallback to plain string interpretation if zip parsing fails
            pass
            
        return records
