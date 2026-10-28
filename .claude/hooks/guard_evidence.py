#!/usr/bin/env python3
"""Claude Code PreToolUse hook: the evidence under ops/ is read-only.

Blocks Edit / Write / MultiEdit / NotebookEdit on anything under ops/, except
new eval cases (ops/evals/cases/case-11.diff and above). Exit code 2 blocks
the tool call and shows the reason to the agent. Every block is logged to
ai-logs/raw.jsonl as a 'GuardBlock' event, which is evidence of the control
working.

Known limitation (record it in the autonomy policy / trifecta audit): this
does not stop writes made through Bash (e.g. `sed -i`). Bash is gated by the
normal permission prompt instead.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

ALLOWED_UNDER_OPS = re.compile(r"^ops/evals/cases/case-(1[1-9]|[2-9][0-9])\.diff$")


def main():
    payload = json.load(sys.stdin)
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        return 0
    relative = os.path.relpath(os.path.abspath(target), os.path.abspath(project_dir)).replace(os.sep, "/")
    if not relative.startswith("ops/") or ALLOWED_UNDER_OPS.match(relative):
        return 0

    reason = (f"Blocked by guard_evidence.py: '{relative}' is evidence under ops/ and is read-only. "
              "Write your output under submission/ instead. New eval cases go in "
              "ops/evals/cases/case-11.diff or higher.")
    try:
        with open(os.path.join(project_dir, "ai-logs", "raw.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "event": "GuardBlock",
                "session_id": payload.get("session_id"),
                "tool_name": payload.get("tool_name"),
                "target": relative,
            }) + "\n")
    except Exception:
        pass
    print(reason, file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
