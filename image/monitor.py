#!/usr/bin/env python3
"""image/monitor.py
Optional monitoring endpoint — enabled via MONITORING=1 (or "true").
Serves container uptime, per-process status and host-log stats as JSON.

Note: runs on MONITOR_PORT (default 8081), NOT 8080 — that port is already
used by Logdy's own web UI inside this container.
"""

import json
import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

START_TIME = time.time()
HOST_NAME = os.uname().nodename
MONITOR_PORT = int(os.environ.get("MONITOR_PORT", "8081"))
LOG_DIR = "/var/log/hosts"

# Processes this image starts; checked by name via pgrep.
WATCHED_SERVICES = ["syslog-ng", "cron", "logdy"]


def is_running(process_name):
    result = subprocess.run(
        ["pgrep", "-x", process_name],
        capture_output=True,
        timeout=5,
    )
    return result.returncode == 0


def host_log_stats():
    """Minimal stats across the per-host log files syslog-ng writes."""
    try:
        entries = [
            e for e in os.scandir(LOG_DIR)
            if e.is_file() and e.name.endswith(".log") and not e.name.startswith(".")
        ]
    except FileNotFoundError:
        return {"host_count": 0, "total_bytes": 0, "newest_message_age_seconds": None}

    if not entries:
        return {"host_count": 0, "total_bytes": 0, "newest_message_age_seconds": None}

    total_bytes = sum(e.stat().st_size for e in entries)
    newest_mtime = max(e.stat().st_mtime for e in entries)

    return {
        "host_count": len(entries),
        "total_bytes": total_bytes,
        "newest_message_age_seconds": round(time.time() - newest_mtime),
    }


class MonitorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path not in ("/", "/index.json"):
            self.send_response(404)
            self.end_headers()
            return

        try:
            data = {
                "hostname": HOST_NAME,
                "uptime_seconds": round(time.time() - START_TIME),
                "retention_hours": int(os.environ.get("RETENTION_HOURS", "24")),
                "services": {
                    name: is_running(name) for name in WATCHED_SERVICES
                },
                "hosts": host_log_stats(),
            }
            status = 200
        except Exception as e:
            data = {"error": str(e)}
            status = 500

        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", MONITOR_PORT), MonitorHandler)
    print(f"Monitoring endpoint on :{MONITOR_PORT} (hostname={HOST_NAME})")
    server.serve_forever()
