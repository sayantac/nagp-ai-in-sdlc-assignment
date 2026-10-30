# Gaps in the brief, and the assumptions made

Each gap is recorded with the assumption made and where it affects the submission. Rows A1–A9 were identified on 2026-10-28 by reading the brief and repository commit `0616158`. Rows marked TODO need your input.

| # | Gap | Assumption / handling | Affects |
|---|---|---|---|
| A1 | The brief says the agent setup to audit is "described at the end of ops/README.md". That file has no such section; it ends at "No answers here". | Asked the trainer on TODO(date). Until answered, the audit covers the actual agent setup used for this submission (Claude Code with the configuration in `.claude/` and `.mcp.json`). | Task 5a |
| A2 | The scenario facts table (PayEx timeout, volumes, SOC 2) appears only in the PDF, not in `ops/README.md`. | Transcribed into `submission/SCENARIO.md` and used as the single source. | Tasks 2, 3 |
| A3 | `ops/evals` gives no answer key ("which is which is not recorded here"). | Own answer key in `04-evals/answer-key.csv`, committed before the first eval run (commit TODO). `scripts/precheck.py` verifies the ordering. | Task 4 |
| A4 | The brief says four of the ten eval cases were shown in the session, which could inflate scores. | The assignment was issued after the workshop ended and this repository was not used in it, so none of the ten cases was shown to me. All ten are marked `no` in `shown_in_session`. The two added cases are still written, as the brief requires. | Task 4 |
| A5 | The repository's git history is 6 bulk-import commits (5 and 12 Oct 2026), with no PRs or reviews. | Lead time and review turnaround cannot come from git or GitHub. The CI history used is `ops/pipeline/run-timings.csv` (20 runs). | Task 5b |
| A6 | There is no review data anywhere in the repository. | Review turnaround is not capturable today. The plan names its future source. | Task 5b |
| A7 | "The Mermaid MCP" is not specified. | Used the Mermaid Chart MCP connector (claude_ai_Mermaid_Chart, remote). Diagram content is sent to an external service to validate and render; the diagrams contain only code structure, no data or secrets. Recorded as an external-communication path in the trifecta audit. | Task 1, Task 5a |
| A8 | The repository's `.github/workflows/ci.yml` is a cut-down pipeline; `ops/pipeline/ci-pipeline.yml` is "the real one". | The architecture test runs in the repository's CI, since that is what exists. It slots into the real pipeline's Unit tests step without change, because that step runs `dotnet test` on the solution. | Task 1 |
| A9 | The repository's `AGENTS.md` contains demo credentials (labelled not real). | Treated as non-secret. Still counted as "private data" in the trifecta audit, because an agent cannot tell the difference. | Task 5a |
