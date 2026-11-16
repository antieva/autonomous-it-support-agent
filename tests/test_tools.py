import json

import pytest

from it_support_agent.tools import (
    fetch_recent_logs,
    get_server_health,
    restart_service,
    escalate_to_engineer,
)


def test_health_returns_assignment_metric():
    result = json.loads(get_server_health("payment-server-01"))
    assert result == {"cpu": "98%", "memory": "40%", "status": "Warning"}


def test_logs_respect_requested_limit():
    result = json.loads(fetch_recent_logs("search-index-09", lines=2))
    assert len(result["logs"]) == 2
    assert "Connection refused" in result["logs"][1]


def test_restart_and_escalation_return_success():
    assert json.loads(restart_service("auth-service-03"))["status"] == "success"
    assert json.loads(escalate_to_engineer("dependency unavailable"))["status"] == "success"


def test_invalid_log_limit_is_rejected():
    with pytest.raises(ValueError):
        fetch_recent_logs("db-node-02", lines=0)

