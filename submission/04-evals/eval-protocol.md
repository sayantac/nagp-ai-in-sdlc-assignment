# Eval protocol

Follows `ops/evals/README.md`.

| Setting | Value |
|---|---|
| Harness | `scripts/run_evals.py` (headless `claude -p`, one fresh session per case) |
| Model (identical in all runs) | TODO exact id |
| Prompt | `prompts/review-v1.md`, verbatim from `ops/evals/README.md` |
| Tools | All disallowed (`--disallowedTools ...`); no MCP servers (`--strict-mcp-config`) |
| Context in the baseline | None: run from an empty temp directory; `~/.claude/CLAUDE.md` empty or moved aside |
| Changed variable | Context file: the same harness run from the repo root, so `CLAUDE.md` → `AGENTS.md` loads. Nothing else changes. |
| Runs | 3 per label, 12 cases each |
| Scoring | By hand (`scripts/score_evals.py`) against `answer-key.csv`, using the strict rule in the README |
| Answer key committed | TODO sha + time; must be earlier than the first raw result (checked by `scripts/precheck.py`) |

## Added cases
| Case | Defect or clean | Real-world origin (one line) |
|---|---|---|
| case-11 | defect | TODO |
| case-12 | clean | TODO |
