# Autonomy policy: first-response incident summaries

_One page. Owner: TODO. Effective: start of the on-call rotation. Review: TODO._

## Levels

| Level | Name | What the agent may do |
|---|---|---|
| L0 | Off | Nothing |
| L1 | Suggest | Produces output for a human to read; nothing is shared or acted on |
| L2 | Draft for approval | Produces output that a human must verify and approve before anyone else sees it or acts on it |
| L3 | Act, then review | Output is shared automatically; a human reviews it within a fixed time |
| L4 | Autonomous | Acts with periodic sampling only |

## Tasks and levels

| Task in the workflow | Level | Controls that make this level safe | Evidence needed to move up a level | Who approves the move |
|---|---|---|---|---|

## Controls in place today (configured, not described)
<!-- Point to the real configuration: .claude/agents/incident-first-responder.md (read-only tools), .claude/settings.json deny rules, the citation requirement, guard_evidence.py. -->

## Measured on this repository
<!-- From first-response-scores.md: on INC-2041 and INC-2047, how many statements were correct, wrong, or unsupported; what was missed. -->

## Day-one level for this team
<!-- State the level, then justify it with: two of six engineers are new to the codebase, plus the measured error rate above. -->
