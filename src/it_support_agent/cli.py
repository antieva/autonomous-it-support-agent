"""Command-line entry point."""

from __future__ import annotations

import os
import sys

from openai import OpenAI

from .agent import ITSupportAgent


def main() -> int:
    if not os.getenv("OPENROUTER_APIKEY"):
        print("Set OPENROUTER_APIKEY before running the live agent.", file=sys.stderr)
        return 2
    issue = " ".join(sys.argv[1:]).strip()
    if not issue:
        print('Usage: it-support-agent "Describe the incident"', file=sys.stderr)
        return 2
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_APIKEY"],
    )
    print(ITSupportAgent(client).run(issue))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

