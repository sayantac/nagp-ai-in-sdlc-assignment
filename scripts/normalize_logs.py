#!/usr/bin/env python3
"""Turn the automatic hook log into the trainer's schema and build the readable summary.

Inputs:
  ai-logs/raw.jsonl     written automatically by .claude/hooks/log_event.py (and run_evals.py)
  ai-logs/ai-log.jsonl  curated entries with the human-oversight fields (via the /ai-log-entry skill)
  ai-logs/agent-wrong.md
Outputs (regenerated on every run, so the output is deterministic):
  ai-logs/ai-log.auto.jsonl  one entry per user prompt, in the trainer's schema, human fields null
  ai-logs/summary.md         the readable summary: coverage, tool usage, curated timeline, corrections

  python3 scripts/normalize_logs.py            # rebuild everything
  python3 scripts/normalize_logs.py --latest 5 # also print the 5 latest auto entries (for /ai-log-entry)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "ai-logs"
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
STAGES = [("task-1", "task-1-architecture"), ("task-2", "task-2-adr"), ("task-3", "task-3-autonomy"),
          ("task-4", "task-4-evals"), ("task-5", "task-5-risk-measurement"), ("video", "video"),
          ("package", "packaging")]


def read_jsonl(path):
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return items


def stage_for(branch):
    for prefix, stage in STAGES:
        if branch and branch.startswith(prefix):
            return stage
    return "setup"


_model_cache = {}


def model_from_transcript(path):
    if not path:
        return None
    if path not in _model_cache:
        model = None
        try:
            for line in Path(path).read_text(encoding="utf-8").splitlines():
                item = json.loads(line)
                message = item.get("message") if isinstance(item, dict) else None
                if isinstance(message, dict) and message.get("model"):
                    model = message["model"]
        except Exception:
            pass
        _model_cache[path] = model
    return _model_cache[path]


def relative(path_text):
    try:
        return str(Path(path_text).resolve().relative_to(ROOT.resolve()))
    except Exception:
        return path_text


def build_auto(raw):
    sessions = defaultdict(list)
    for event in raw:
        if event.get("session_id"):
            sessions[event["session_id"]].append(event)
    entries = []
    for session_id, events in sessions.items():
        events.sort(key=lambda e: e.get("ts", ""))
        current, index = None, 0
        for event in events:
            kind = event.get("event")
            if kind == "UserPromptSubmit":
                index += 1
                ts = event["ts"]
                prompt = event.get("prompt") or ""
                current = {
                    "id": f"{ts.replace('-', '').replace(':', '')}-{session_id[:8]}-p{index}",
                    "timestamp": ts, "stage": stage_for(event.get("branch")), "agent": "agent",
                    "agent_name": "main", "agent_type": "built-in", "ai_tool": "Claude Code",
                    "model": model_from_transcript(event.get("transcript_path")),
                    "mode": None, "permission_mode": event.get("permission_mode"),
                    "related_ids": [], "parent_task": None, "context": "AI in SDLC assignment",
                    "request": prompt, "skills_used": [], "subagents_used": [], "mcp_tools_used": [],
                    "tools_used": [], "suggestion": None, "human_decision": None,
                    "action_verification": None, "limitation": None, "status": "auto-captured",
                    "artifacts": [], "execution_evidence": {"commands": [], "guard_blocks": [],
                                                            "branch": event.get("branch"),
                                                            "git_head": event.get("git_head"),
                                                            "session_id": session_id}}
                if prompt.startswith("/"):
                    current["skills_used"].append({"name": prompt.split()[0], "type": "custom",
                                                   "purpose": "slash command", "invocation": "explicit"})
                entries.append(current)
                continue
            if current is None:
                continue
            if kind == "GuardBlock":
                current["execution_evidence"]["guard_blocks"].append(event.get("target"))
            if kind != "PostToolUse":
                continue
            tool = event.get("tool_name") or ""
            tool_input = event.get("tool_input") or {}
            if tool.startswith("mcp__"):
                parts = tool.split("__")
                current["mcp_tools_used"].append({"server": parts[1] if len(parts) > 1 else "?",
                                                  "tool": "__".join(parts[2:]) or "?", "purpose": None})
            elif tool in ("Task", "Agent"):
                current["subagents_used"].append({"name": tool_input.get("subagent_type") or "general-purpose",
                                                  "type": "custom" if tool_input.get("subagent_type") else "built-in",
                                                  "task": tool_input.get("description"), "status": "completed"})
            elif tool == "Skill":
                current["skills_used"].append({"name": tool_input.get("skill") or tool_input.get("command_name")
                                               or "?", "type": "custom", "purpose": None,
                                               "invocation": "automatic"})
            if tool and not tool.startswith("mcp__") and tool not in current["tools_used"]:
                current["tools_used"].append(tool)
            if tool in EDIT_TOOLS:
                target = tool_input.get("file_path") or tool_input.get("notebook_path")
                if target and relative(target) not in current["artifacts"]:
                    current["artifacts"].append(relative(target))
            if tool == "Bash" and tool_input.get("command"):
                current["execution_evidence"]["commands"].append(tool_input["command"][:300])
    for entry in entries:
        edited = bool(entry["artifacts"]) or "Bash" in entry["tools_used"]
        mode = entry.pop("permission_mode")
        if mode == "plan":
            entry["mode"] = "plan"
        elif not edited and not entry["subagents_used"]:
            entry["mode"] = "ask"
        elif mode == "acceptEdits":
            entry["mode"] = "edit"
        else:
            entry["mode"] = "agent"
    entries.sort(key=lambda e: e["timestamp"])
    return entries


def summary(auto, curated, raw, wrong_count):
    covered = {rid for entry in curated for rid in entry.get("related_ids", [])}
    uncovered = [entry for entry in auto if entry["id"] not in covered]
    tools, mcp, subagents, skills = Counter(), Counter(), Counter(), Counter()
    for entry in auto:
        tools.update(entry["tools_used"])
        mcp.update(f"{m['server']}::{m['tool']}" for m in entry["mcp_tools_used"])
        subagents.update(s["name"] for s in entry["subagents_used"])
        skills.update(s["name"] for s in entry["skills_used"])
    by_stage = Counter(entry["stage"] for entry in auto)
    evals = [e for e in raw if e.get("event") == "EvalRun"]
    blocks = [e for e in raw if e.get("event") == "GuardBlock"]
    models = Counter(entry["model"] for entry in auto if entry["model"])
    reviewed = sum(1 for e in curated if e.get("human_decision") and "TODO" not in str(e["human_decision"]))
    coverage = 100 * (len(auto) - len(uncovered)) / len(auto) if auto else 0

    def table(counter):
        return ["| Item | Count |", "|---|---|"] + [f"| `{k}` | {v} |" for k, v in counter.most_common()] or ["(none)"]

    out = ["# AI Augmentation log: summary", "",
           "_Generated by `scripts/normalize_logs.py`. Raw events come from Claude Code hooks "
           "(`ai-logs/raw.jsonl`), auto entries are in `ai-logs/ai-log.auto.jsonl`, and the human-curated "
           "entries are in `ai-logs/ai-log.jsonl`._", "",
           "## Overview", "",
           f"- Prompts captured automatically: **{len(auto)}**, across {len({e['execution_evidence']['session_id'] for e in auto})} sessions",
           f"- Curated entries with human decision and verification: **{reviewed}** of {len(curated)}",
           f"- Oversight coverage (auto prompts linked from a curated entry): **{coverage:.0f}%**",
           f"- Headless eval calls: **{len(evals)}**",
           f"- Guard blocks (attempted edits to evidence under ops/): **{len(blocks)}**",
           f"- Recorded agent errors (`agent-wrong.md`): **{wrong_count}**",
           f"- Models: {', '.join(f'`{m}` ({n})' for m, n in models.most_common()) or 'n/a'}", "",
           "## Prompts by stage", ""] + table(by_stage) + ["", "## Built-in tools", ""] + table(tools) + \
          ["", "## MCP tools", ""] + table(mcp) + ["", "## Subagents", ""] + table(subagents) + \
          ["", "## Skills and slash commands", ""] + table(skills) + \
          ["", "## Curated timeline", "", "| Time | Stage | Request | Human decision | Verification | Status |",
           "|---|---|---|---|---|---|"]
    for entry in sorted(curated, key=lambda e: e.get("timestamp", "")):
        def cell(value):
            return (str(value or "")[:140]).replace("|", "/").replace("\n", " ")
        out.append(f"| {cell(entry.get('timestamp'))} | {cell(entry.get('stage'))} | {cell(entry.get('request'))} | "
                   f"{cell(entry.get('human_decision'))} | {cell(entry.get('action_verification'))} | "
                   f"{cell(entry.get('status'))} |")
    out += ["", "## Prompts not yet linked to a curated entry", ""]
    out += [f"- `{e['id']}` ({e['stage']}): {e['request'][:100]!r}" for e in uncovered[-40:]] or ["(none)"]
    out += ["", "## Where the agent was wrong", "", "See `ai-logs/agent-wrong.md`.", ""]
    return "\n".join(out), uncovered


def main():
    raw = read_jsonl(LOGS / "raw.jsonl")
    curated = read_jsonl(LOGS / "ai-log.jsonl")
    auto = build_auto(raw)
    with (LOGS / "ai-log.auto.jsonl").open("w", encoding="utf-8") as handle:
        for entry in auto:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    wrong_file = LOGS / "agent-wrong.md"
    wrong_count = wrong_file.read_text(encoding="utf-8").count("\n## ") if wrong_file.exists() else 0
    text, uncovered = summary(auto, curated, raw, wrong_count)
    (LOGS / "summary.md").write_text(text, encoding="utf-8")
    print(f"auto entries: {len(auto)} | curated: {len(curated)} | not linked: {len(uncovered)} | "
          f"-> ai-logs/ai-log.auto.jsonl, ai-logs/summary.md")
    if "--latest" in sys.argv:
        count = int(sys.argv[sys.argv.index("--latest") + 1])
        for entry in auto[-count:]:
            print(json.dumps({key: entry[key] for key in ("id", "timestamp", "stage", "mode", "model", "request",
                                                          "tools_used", "mcp_tools_used", "subagents_used",
                                                          "skills_used", "artifacts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
