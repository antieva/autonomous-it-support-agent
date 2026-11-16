"""Deterministic tools used by the incident responder.

The data is intentionally simulated, matching the scenarios in the assignment
notebook. The functions return JSON strings because that is the format expected
by the model tool-calling API.
"""

from __future__ import annotations

import json
from typing import Callable, Dict


SERVER_METRICS = {
    "payment-server-01": {"cpu": "98%", "memory": "40%", "status": "Warning"},
    "db-node-02": {"cpu": "12%", "memory": "60%", "status": "Healthy"},
    "auth-service-03": {"cpu": "45%", "memory": "95%", "status": "Critical"},
    "search-index-09": {"cpu": "10%", "memory": "15%", "status": "Error"},
    "frontend-node-04": {"cpu": "25%", "memory": "30%", "status": "Healthy"},
}

SERVER_LOGS = {
    "payment-server-01": [
        "[INFO] Request received /pay/v1",
        "[WARN] CPU threshold exceeded 90%",
        "[WARN] Thread pool exhaustion",
        "[CRITICAL] Process hung, not accepting new connections",
        "[ERROR] Timeout waiting for thread",
    ],
    "db-node-02": [
        "[INFO] Backup started",
        "[INFO] Backup completed successfully",
        "[INFO] User query executed in 12ms",
        "[INFO] Health check: OK",
        "[INFO] Replication sync active",
    ],
    "auth-service-03": [
        "[INFO] Token validated user_882",
        "[WARN] Garbage collection taking too long (>5s)",
        "[ERROR] java.lang.OutOfMemoryError: Java heap space",
        "[CRITICAL] Application crashing due to memory leak",
        "[INFO] Restarting context...",
    ],
    "search-index-09": [
        "[INFO] Indexing started",
        "[ERROR] Connection refused: elastic-cluster-main:9200",
        "[ERROR] Failed to write document ID 4432",
        "[CRITICAL] Dependency Unreachable: Search Engine is down",
        "[ERROR] Retrying in 30s...",
    ],
    "frontend-node-04": [
        "[INFO] GET /home 200 OK",
        "[INFO] GET /assets/logo.png 200 OK",
        "[INFO] GET /login 200 OK",
        "[INFO] GET /api/v1/status 200 OK",
        "[INFO] Health check passed",
    ],
}


def get_server_health(server_id: str) -> str:
    """Return CPU, memory, and status for a server."""
    print(f"-> TOOL: Checking health for {server_id}...")
    return json.dumps(SERVER_METRICS.get(server_id, {"error": "Server not found. Check the ID."}))


def fetch_recent_logs(server_id: str, lines: int = 5) -> str:
    """Return up to ``lines`` recent log entries for a server."""
    if lines < 1:
        raise ValueError("lines must be at least 1")
    print(f"-> TOOL: Fetching last {lines} log lines for {server_id}...")
    logs = SERVER_LOGS.get(server_id, ["[INFO] System stable", "[INFO] Heartbeat signal received"])
    return json.dumps({"logs": logs[:lines]})


def restart_service(server_id: str) -> str:
    """Simulate restarting a service and return a confirmation."""
    print(f"-> TOOL: Restarting service for {server_id}...")
    return json.dumps({"status": "success", "message": "Server restarted successfully", "server_id": server_id})


def escalate_to_engineer(summary: str) -> str:
    """Simulate creating a human-engineer incident ticket."""
    print("-> TOOL: Escalating to human...")
    return json.dumps({"status": "success", "message": "Ticket created", "summary": summary})


AVAILABLE_FUNCTIONS: Dict[str, Callable[..., str]] = {
    "get_server_health": get_server_health,
    "fetch_recent_logs": fetch_recent_logs,
    "restart_service": restart_service,
    "escalate_to_engineer": escalate_to_engineer,
}

