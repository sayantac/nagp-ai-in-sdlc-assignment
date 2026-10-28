# Demo video (8–10 min) — shot list

| Time | Show | Say (one line) |
|---|---|---|
| 0:00–0:30 | `submission/README.md` | What is in the submission and how it is traceable |
| 0:30–1:30 | `.claude/` (agents, hooks, deny rules) | The setup is the control: scoped agents, read-only evidence, no web |
| 1:30–2:45 | As-built vs unscoped diagram; `inferred.md` | One concrete inference the agent made from ops/ that was wrong |
| 2:45–3:30 | `python3 scripts/demo_arch_test.py` output, CI link | The rule, the test going red, then green |
| 3:30–5:15 | ADR: the decision, the 3 a.m. section, "Where the agent was wrong" | The unknown-outcome problem, and whether the agent caved under pressure |
| 5:15–6:15 | Autonomy policy, first-response scores | The day-one level and the measured reason for it |
| 6:15–7:30 | `results.md` | The rates, the spread, the per-case flips, the confidence |
| 7:30–8:30 | Trifecta audit, blocked WebFetch, baseline numbers | Which leg was removed; the two numbers and which is a proxy |
| 8:30–9:30 | `ai-logs/summary.md`, one entry traced to its commit | Prompt → subagent → human decision → commit (`AI-Log-Id`) → CI |
