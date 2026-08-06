"""Optional Claude API helper for explaining a completed compression QA report."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def build_prompt(report: dict[str, object]) -> str:
    """Keep Claude in an advisory role, outside deterministic compression."""
    return f"""You are assisting an IoT QA engineer. Explain this completed compression-monitor report in plain language.

Report:
{json.dumps(report, indent=2)}

Return exactly three short sections:
1. What happened
2. What is safe to conclude
3. Recommended human follow-up

Rules: Do not invent measurements. Do not claim data loss if hash checks passed. Do not make changes to compression settings, agents, or deployment. This is an advisory summary only."""


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask Claude to explain a compression-monitor report.")
    parser.add_argument("report", type=Path, help="JSON report produced by a benchmark or trust monitor")
    parser.add_argument("--model", default=os.environ.get("CLAUDE_MODEL", "claude-opus-4-8"))
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before calling Claude.")

    try:
        from anthropic import Anthropic
    except ImportError as error:
        raise SystemExit("Install the optional dependency first: pip install anthropic") from error

    report = json.loads(args.report.read_text(encoding="utf-8"))
    client = Anthropic()
    response = client.messages.create(
        model=args.model,
        max_tokens=500,
        messages=[{"role": "user", "content": build_prompt(report)}],
    )
    print("".join(block.text for block in response.content if block.type == "text"))


if __name__ == "__main__":
    main()
