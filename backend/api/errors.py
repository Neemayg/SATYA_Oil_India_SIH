"""
SATYA API Standardized Error Model (Phase 11)
Defines SATYAError exception and uniform JSON error payload format.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

class SATYAError(Exception):
    """
    Standardized API exception for SATYA Backend Application Services.
    """
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.request_id = request_id or f"REQ-{uuid.uuid4().hex[:8].upper()}"
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "request_id": self.request_id,
                "timestamp": self.timestamp
            }
        }
