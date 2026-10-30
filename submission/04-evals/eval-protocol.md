# Eval protocol

Follows `ops/evals/README.md`.

| Setting | Value |
|---|---|
| Harness | `scripts/run_evals.py` (headless `claude -p`, one fresh session per case) |
| Model (identical in all runs) | `claude-sonnet-5-5` |
| Prompt | `prompts/review-v1.md`, verbatim from `ops/evals/README.md` |
| Tools | All disallowed (`--disallowedTools ...`); no MCP servers (`--strict-mcp-config`) |
| Context in the baseline | None: run from an empty temp directory; `~/.claude/CLAUDE.md` empty or moved aside |
| Changed variable | Context file: the same harness run from the repo root, so `CLAUDE.md` → `AGENTS.md` loads. Nothing else changes. |
| Runs | 3 per label, 12 cases each |
| Scoring | By hand (`scripts/score_evals.py`) against `answer-key.csv`, using the strict rule in the README |
| Answer key committed | TODO sha + time; must be earlier than the first raw result (checked by `scripts/precheck.py`) |

## Added cases
| Case | Defect or clean | Origin (one line) |
|---|---|---|
| case-11 | defect | Non-idempotent retry of a payment submission after a timeout (duplicate-payment risk). Written against this codebase from a common payment-integration defect pattern. |
| case-12 | clean | Extract-method refactor of Approve/Reject into a shared Decide helper, behaviour unchanged. Typical false-alarm bait. |
