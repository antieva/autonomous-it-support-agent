# Autonomous IT Support Agent

An LLM-powered Level 1 IT support agent that diagnoses server incidents with
tool calls, restarts services when resources are critical, and escalates
everything else to a human engineer.

You describe a problem in plain language, for example "Search isn't working.
Check search-index-09.", and the agent investigates on its own. It checks server
health, reads recent logs, and decides what to do:

- **CPU or memory critical:** it restarts the service.
- **Dependency failure or unresolved issue:** it escalates to a human engineer
  with a summary.

It works with any OpenAI-compatible model through OpenRouter and runs from a
simple command line (`it-support-agent "<incident>"`). The server tools are
simulated, so it is safe to experiment with. The tests cover the business logic
and the tool-calling loop.

## Setup

```bash
cd assignement/autonomous-it-support-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

The test suite is deterministic and does not call an LLM:

```bash
pytest
```

## Run with OpenRouter

Set `OPENROUTER_APIKEY` and optionally select another OpenRouter model:

```bash
export OPENROUTER_APIKEY='your-key'
python -m it_support_agent.cli "Search isn't working. Check search-index-09."
```

The default model is `openai/gpt-5.4-nano`; override it with
`IT_SUPPORT_MODEL` when needed.

## Project layout

- `src/it_support_agent/tools.py` — simulated server health, log, restart, and escalation tools.
- `src/it_support_agent/agent.py` — tool schema and OpenAI-compatible execution loop.
- `src/it_support_agent/cli.py` — command-line entry point.
- `tests/` — business-logic and tool-loop tests.

