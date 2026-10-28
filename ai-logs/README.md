# AI Augmentation logs

The goal is traceability: what the AI did, which capabilities it used, and how a human checked and decided on the output. Logs are generated automatically wherever the tool supports it, and the human-oversight fields are added at the time of each step.

| File | Produced by | Contents |
|---|---|---|
| `raw.jsonl` | Claude Code hooks (`.claude/hooks/log_event.py`, configured in `.claude/settings.json`) and `scripts/run_evals.py` | Every session start and end, prompt, tool call (including MCP, subagent and skill calls), subagent stop, guard block and headless eval call, with UTC timestamp, git branch and HEAD. Secret-looking values are redacted. |
| `ai-log.auto.jsonl` | `scripts/normalize_logs.py` | One entry per user prompt, in the trainer's schema. Human fields are `null`. |
| `ai-log.jsonl` | The `/ai-log-entry` skill, confirmed by the human | Curated entries in the trainer's schema with `human_decision`, `action_verification`, `limitation` and `status`. `related_ids` link to the auto entries they cover. |
| `summary.md` | `scripts/normalize_logs.py` | Readable summary: counts, tools, MCP, subagents, skills, curated timeline, oversight coverage, unlinked prompts |
| `agent-wrong.md` | The `/agent-wrong` command | Moments where the agent was wrong, sycophantic or useless; feeds the ADR section |
| `transcripts/` | `/export` at the end of each session | Full session transcripts |

Commits carry an `AI-Log-Id:` trailer (via `.git/hooks/prepare-commit-msg`) plus Claude Code's `Co-Authored-By` trailer, linking commits to log entries.

## Field mapping for Claude Code

| Trainer field | Source |
|---|---|
| `ai_tool`, `model` | "Claude Code"; the model id read from the session transcript |
| `agent_type`, `agent_name` | `built-in` / `main` for the main session; `custom` subagents from `.claude/agents/` |
| `mode` | plan mode → `plan`; no edits and no subagents → `ask`; acceptEdits mode → `edit`; otherwise `agent` |
| `skills_used` | Custom slash commands (`.claude/commands/`) and skills (`.claude/skills/`) |
| `subagents_used` | Task/Agent tool calls with their `subagent_type` |
| `mcp_tools_used` | Tool names of the form `mcp__<server>__<tool>` |
| `execution_evidence` | Added field: Bash commands run, guard blocks, branch, git HEAD, session id |

## Before this repository work began

The assignment analysis and this scaffold were produced in a claude.ai conversation (Claude Opus 5.5) before any Claude Code session. They are recorded as the first two entries in `ai-log.jsonl`, with timestamps to day precision only, because exact times were not captured.
