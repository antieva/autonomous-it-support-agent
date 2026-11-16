"""OpenAI-compatible tool-calling agent."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .tools import AVAILABLE_FUNCTIONS


SYSTEM_PROMPT = (
    "You are a Level 1 IT Responder. Investigate server issues. "
    "If CPU or memory is above 90%, restart the service. "
    "If logs show a critical dependency error such as connection refused "
    "that a restart will not fix, escalate to an engineer."
)

TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_server_health",
            "description": "Checks the current CPU and memory usage of a specific server.",
            "parameters": {
                "type": "object",
                "properties": {"server_id": {"type": "string", "description": "The server ID."}},
                "required": ["server_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_recent_logs",
            "description": "Retrieves recent log entries from a server to diagnose errors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "The server ID."},
                    "lines": {"type": "integer", "description": "Number of log lines to fetch."},
                },
                "required": ["server_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "restart_service",
            "description": "Restarts a server service after critical CPU or memory usage is detected.",
            "parameters": {
                "type": "object",
                "properties": {"server_id": {"type": "string", "description": "The server ID."}},
                "required": ["server_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_engineer",
            "description": "Escalates an unresolved or dependency-related incident to a human engineer.",
            "parameters": {
                "type": "object",
                "properties": {"summary": {"type": "string", "description": "Incident summary."}},
                "required": ["summary"],
            },
        },
    },
]


class ITSupportAgent:
    """Run the incident workflow using an OpenAI-compatible client."""

    def __init__(self, client: Any, model: Optional[str] = None, max_turns: int = 12):
        self.client = client
        self.model = model or os.getenv("IT_SUPPORT_MODEL", "openai/gpt-5.4-nano")
        self.max_turns = max_turns

    def run(self, user_issue: str) -> str:
        """Investigate an issue and return the model's final response."""
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_issue},
        ]

        for _ in range(self.max_turns):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
            )
            response_message = response.choices[0].message
            messages.append(response_message)
            tool_calls = getattr(response_message, "tool_calls", None)

            if not tool_calls:
                return getattr(response_message, "content", "") or ""

            for tool_call in tool_calls:
                name = tool_call.function.name
                function = AVAILABLE_FUNCTIONS.get(name)
                if function is None:
                    raise ValueError(f"Model requested unknown tool: {name}")
                arguments = json.loads(tool_call.function.arguments or "{}")
                output = function(**arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": output,
                    }
                )

        raise RuntimeError(f"Agent exceeded the {self.max_turns}-turn limit")

