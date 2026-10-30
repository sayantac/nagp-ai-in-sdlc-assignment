# Autonomy policy: first-response incident summaries

Owner: Sayantan Chakraborty (senior engineer, Invoice Approval). Effective: start of the on-call rotation. Review: after the first month-end, then quarterly.

## Levels

| Level | Name | What the agent may do |
|---|---|---|
| L0 | Off | Nothing |
| L1 | Suggest | Produces output for an engineer to read; nothing is shared or acted on |
| L2 | Draft for approval | An engineer verifies the output before anyone else sees it or acts on it |
| L3 | Act, then review | Output is used automatically; an engineer reviews it within a fixed time |
| L4 | Autonomous | Acts with periodic sampling only |

## Tasks and levels

| Task | Day-one level | Controls that make it safe | Evidence to move up | Who approves |
|---|---|---|---|---|
| Read exported evidence (alert, logs, metrics, queue status) | L3 | Read-only tools (Read, Grep, Glob); no network; evidence folders write-protected | Not applicable: reading changes nothing | Not applicable |
| Draft the first-response summary (what, impact, timeline) | L2 | Every statement labelled FACT or HYPOTHESIS; every FACT cites file and line; instructions found inside logs flagged, not followed; an engineer opens each cited line before sharing | 20 incidents or drills run in shadow mode: at least 95% of FACT claims correct and cited, and no wrong FACT that would have changed the action | Service owner |
| Rank hypotheses with confidence and next checks | L1 | Shown next to the engineer's own view; never acted on alone | Top three contain the real cause in at least 80% of the same 20 cases, and no hypothesis is presented as fact | Service owner and on-call lead |
| Propose mitigation options (what each changes, costs, how to undo) | L1 | Options only; a named approver decides (the incident commander out of hours) | 10 reviewed proposals with correct undo steps and no unsafe option | Incident commander and service owner |
| Execute any change (rollback, config, queue action, paging, closing an incident) | L0 | No write tools and no production credentials for the agent | Not planned | Not applicable |

## Controls in place today (configured, not described)

- `.claude/agents/incident-first-responder.md`: read-only tools, a citation rule, and instructions to flag injected text.
- `.claude/settings.json`: web fetch, web search and the Playwright MCP are denied.
- `.claude/hooks/guard_evidence.py`: blocks edits under `ops/`. Known limit: it does not cover writes made through Bash, which stay behind a permission prompt.

## Measured on this repository

Not measured. I did not run a trial on INC-2041 or INC-2047, so there is no error rate for this workflow. The day-one level below is therefore the lowest level that still saves time, and moving up requires the shadow-mode evidence in the table.

## Day-one level for this team

- **L2 for summaries, L1 for hypotheses and mitigation options, L0 for any action.** Reading exported evidence is L3 because it cannot change anything.
- Two of the six engineers are new to this codebase. They cannot yet tell a plausible but wrong hypothesis from a right one, and no error rate exists to show how often that happens.
- A new engineer must open each cited line before relying on a summary. During the first two rotations a second engineer co-signs any summary that goes beyond the on-call pair.
- A level moves up only on the evidence above, and only with the approver's written sign-off.