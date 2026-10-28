---
name: ai-log-entry
description: Write one curated AI Augmentation log entry in the trainer's JSON schema, recording the human decision, the verification performed and any limitation. Use after every meaningful AI-assisted step in this assignment, whenever the user says "log this", "/ai-log-entry", "record that", or finishes a task step, and before committing work produced with the agent.
---

# AI log entry

Appends one line to `ai-logs/ai-log.jsonl`. These curated entries are the human-oversight record. The automatic hook log (`ai-logs/raw.jsonl`) records what happened; this entry records what the human decided about it.

## Steps

1. Run `python3 scripts/normalize_logs.py --latest 8` to refresh the auto log and list the latest auto-captured prompt ids, with their tools, MCP calls, subagents and files.
2. Draft every factual field from that output and this conversation: tools, MCP calls, subagents, skills, files, model, mode and stage.
3. **Ask the human for the three oversight fields, in their own words.** Ask them in one message:
   - `human_decision`: what they accepted, changed or rejected, and why.
   - `action_verification`: how they checked it, for example a command run, a file opened, a comparison with their own notes, or a CI link.
   - `limitation`: anything still wrong, unverified or out of scope. `null` if none.

   Never invent, paraphrase into something stronger, or pre-fill these three fields. If the human says "skip", write `null` and set `status` to `"unreviewed"`.
4. Ask for `status`, one of: `applied`, `partially-applied`, `rejected`, `rework-required`, `unreviewed`.
5. Show the complete JSON entry and append it only after the human confirms.

## Schema (one JSON object per line)

```json
{
  "id": "<YYYYMMDDTHHMMSSZ>-<stage>-<short-slug>",
  "timestamp": "<UTC ISO-8601>",
  "stage": "<setup | task-1-architecture | task-2-adr | task-3-autonomy | task-4-evals | task-5-risk-measurement | video | packaging>",
  "agent": "agent",
  "agent_name": "<main | codebase-cartographer | evidence-analyst | devils-advocate | incident-first-responder>",
  "agent_type": "<built-in | custom | sub-agent>",
  "ai_tool": "Claude Code",
  "model": "<exact model id from the auto log>",
  "mode": "<ask | plan | agent | edit>",
  "related_ids": ["<auto ids from step 1 that this entry covers>"],
  "parent_task": "<assignment task, e.g. 'Task 2 - exactly-once ADR'>",
  "context": "AI in SDLC assignment - Invoice Approval service",
  "request": "<the prompt or slash command, verbatim if short>",
  "skills_used": [{"name": "", "type": "custom", "purpose": "", "invocation": "explicit"}],
  "subagents_used": [{"name": "", "type": "custom", "task": "", "status": "completed"}],
  "mcp_tools_used": [{"server": "", "tool": "", "purpose": ""}],
  "tools_used": ["Read", "Grep"],
  "suggestion": "<one-line summary of what the agent proposed or produced>",
  "human_decision": "<HUMAN, own words>",
  "action_verification": "<HUMAN, own words>",
  "limitation": "<HUMAN, own words, or null>",
  "status": "<applied | partially-applied | rejected | rework-required | unreviewed>",
  "artifacts": ["<repo-relative paths created or changed>"],
  "execution_evidence": {"commands": [], "test_results": null, "commit": null}
}
```

Mode mapping for Claude Code (also documented in `ai-logs/README.md`): plan mode → `plan`; a question answered with no file edits and no subagents → `ask`; acceptEdits mode → `edit`; default mode with edits or subagents → `agent`.

Slash commands from `.claude/commands/` go in `skills_used` with `type: custom` and `invocation: explicit`.

If the agent was wrong, sycophantic or useless in this step, also remind the human to run `/agent-wrong`.
