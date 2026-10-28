#!/usr/bin/env python3
"""Claude Code hook: append every hook event to ai-logs/raw.jsonl.

Wired to SessionStart, UserPromptSubmit, PostToolUse, SubagentStop, Stop and
SessionEnd in .claude/settings.json. Never blocks Claude Code: any error is
swallowed and the hook exits 0.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

MAX_TEXT = 2000
SECRET_PATTERN = re.compile(
    r"(?i)(password|passwd|secret|token|api[_-]?key)(\s*[:=]\s*)([^\s'\"]+)"
)


def redact(text):
    return SECRET_PATTERN.sub(lambda m: m.group(1) + m.group(2) + "[REDACTED]", text)


def trim(value, limit=MAX_TEXT):
    if value is None:
        return None
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = redact(text)
    return text if len(text) <= limit else text[:limit] + f"...[truncated {len(text) - limit} chars]"


def git(project_dir, *args):
    try:
        out = subprocess.run(["git", *args], cwd=project_dir, capture_output=True,
                             text=True, timeout=3)
        return out.stdout.strip() or None
    except Exception:
        return None


def main():
    payload = json.load(sys.stdin)
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    event = payload.get("hook_event_name")
    record = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": event,
        "session_id": payload.get("session_id"),
        "transcript_path": payload.get("transcript_path"),
        "permission_mode": payload.get("permission_mode"),
        "branch": git(project_dir, "rev-parse", "--abbrev-ref", "HEAD"),
        "git_head": git(project_dir, "rev-parse", "--short", "HEAD"),
    }
    if event == "UserPromptSubmit":
        record["prompt"] = trim(payload.get("prompt"), 4000)
    if event == "PostToolUse":
        tool_input = payload.get("tool_input") or {}
        record["tool_name"] = payload.get("tool_name")
        record["tool_input"] = {
            key: trim(value, 600) for key, value in tool_input.items()
            if key in ("file_path", "notebook_path", "command", "description", "pattern",
                       "path", "subagent_type", "prompt", "skill", "command_name", "url",
                       "diagram", "preview_id")
        } or {"keys": sorted(tool_input.keys())}
        record["tool_response"] = trim(payload.get("tool_response"), 800)
    if event in ("SubagentStop", "Stop"):
        record["stop_hook_active"] = payload.get("stop_hook_active")
    if event in ("SessionStart", "SessionEnd"):
        record["source_or_reason"] = payload.get("source") or payload.get("reason")

    log_dir = os.path.join(project_dir, "ai-logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "raw.jsonl"), "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
