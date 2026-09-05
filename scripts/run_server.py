#!/usr/bin/env python3
"""
SATYA REST API Application Server Script (Phase 11)
Launches zero-dependency Python standard library HTTP server wrapping SATYAApplicationAPI.
"""

import sys
import os
import json
import argparse
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.persistence.database_engine import DatabaseEngine
from backend.api.app import SATYAApplicationAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
logger = logging.getLogger("SATYA.Server")

# Global API Router instance
db_file = os.path.join(BASE_DIR, "satya_dev.db")
db_engine = DatabaseEngine(db_file)
api_router = SATYAApplicationAPI(db_engine)

def _auto_seed_database(api: SATYAApplicationAPI):
    try:
        proj_id = "PRJ-NBG-2026"
        schedule_path = os.path.join(BASE_DIR, "data", "synthetic", "schedules", "baseline_schedule.json")
        if os.path.exists(schedule_path):
            fps = api.db.get_fingerprints_by_project(proj_id)
            if not fps:
                logger.info(f"Seeding baseline schedule for project {proj_id}...")
                api.fingerprint_service.process_schedule_file(schedule_path)

            vocab = api.fingerprint_service.get_valid_activity_vocabulary()
            api.pipeline_service.set_schedule_vocabulary(vocab)
            api.validation_service.set_valid_vocabulary(vocab)

            events = api.db.get_all_execution_events()
            if not events:
                logger.info(f"Seeding hero demo DPR observation payload for project {proj_id}...")
                demo_text = (
                    "Daily Progress Report - Duliajan Field Office - Date: 2026-09-04\n"
                    "Contractor: North Basin Constructors Pvt Ltd | Sector: PL-SEC1\n"
                    "ACT-1010: Mainline ROW Clearing & Grading Sec 1 1800m completed.\n"
                    "ACT-1011: Mainline Trench Excavation Sec 1 1500m completed.\n"
                    "ACT-1020: Mainline HDD River Crossing Section 3 420m drilling completed. QA/NDT clearance pending."
                )
                # Route through the upload handler so matching, trust evaluation
                # and projection run exactly as they do for live uploads.
                api.ingestion_handler.handle_upload({
                    "project_id": proj_id,
                    "source_type": "DPR_EXCEL",
                    "file_name": "demo_dpr_001.txt",
                    "content": demo_text,
                    "observed_timestamp": "2026-09-04T08:00:00Z",
                })

            proj = api.db.get_latest_schedule_projection(proj_id)
            if not proj:
                logger.info(f"Generating initial schedule projection for project {proj_id}...")
                api.projection_service.generate_projection_for_project(proj_id)
                api.monitoring_service.run_monitoring_evaluation(proj_id)
    except Exception as e:
        logger.warning(f"Auto-seeding check encountered notice: {e}")

_auto_seed_database(api_router)

class SATYAHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    Standard library HTTP request handler wrapping SATYAApplicationAPI router.
    """

    def log_message(self, format, *args):
        # Override default stderr logging with structured logger
        logger.info(f"{self.address_string()} - {format % args}")

    def _process_request(self, method: str):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
        origin = self.headers.get("Origin")

        # Static Asset Serving for Frontend App
        if not path.startswith("/api/v1"):
            if method != "GET":
                self.send_error(405, "Method Not Allowed")
                return

            rel_path = path.lstrip("/")
            if not rel_path or rel_path == "":
                rel_path = "index.html"

            static_dir = os.path.join(BASE_DIR, "frontend")
            file_path = os.path.abspath(os.path.join(static_dir, rel_path))

            # Security check: prevent directory traversal
            if not file_path.startswith(static_dir) or not os.path.exists(file_path) or os.path.isdir(file_path):
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"404 Not Found")
                return

            # Determine mime type
            mime_type = "text/html"
            if file_path.endswith(".js"):
                mime_type = "application/javascript"
            elif file_path.endswith(".css"):
                mime_type = "text/css"
            elif file_path.endswith(".json"):
                mime_type = "application/json"
            elif file_path.endswith(".svg"):
                mime_type = "image/svg+xml"

            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
            return

        # Read JSON body if present
        body_json = None
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            try:
                raw_body = self.rfile.read(content_length).decode("utf-8")
                body_json = json.loads(raw_body)
            except Exception as e:
                logger.warning(f"Failed to parse request JSON body: {e}")

        status_code, headers, response_data = api_router.dispatch(
            method=method,
            path=path,
            body=body_json,
            params=query_params,
            request_origin=origin
        )

        self.send_response(status_code)
        for h_name, h_val in headers.items():
            self.send_header(h_name, h_val)
        self.end_headers()

        response_bytes = json.dumps(response_data, indent=2).encode("utf-8")
        self.wfile.write(response_bytes)

    def do_GET(self):
        self._process_request("GET")

    def do_POST(self):
        self._process_request("POST")

    def do_OPTIONS(self):
        self._process_request("OPTIONS")

def main():
    parser = argparse.ArgumentParser(description="SATYA Application API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    args = parser.parse_args()

    server_address = (args.host, args.port)
    httpd = HTTPServer(server_address, SATYAHTTPRequestHandler)
    logger.info(f"🚀 SATYA REST API Server running at http://{args.host}:{args.port}")
    logger.info(f"📋 OpenAPI specification available at http://{args.host}:{args.port}/api/v1/openapi.json")
    logger.info("Press Ctrl+C to stop.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down SATYA API Server.")
        httpd.server_close()

if __name__ == "__main__":
    main()
