# Baseline measurement plan

Capture before the on-call rotation starts. Report the median and p85, the time window and n. Never report a mean alone.

  **Two numbers captured today:** lead time (proxy) median 67.5 h, p85 291.9 h, n=5; CI pipeline duration median 31.4 min, p85 34.5 min, n=18. Source: ops/pipeline/run-timings.csv (20 runs, 19 Jan–2 Feb 2026).

| Metric | Definition | Captured today | Value | Source and query today | Production source once live | Owner |
|---|---|---|---|---|---|---|
| Lead time for changes | First commit → running in production | Proxy | PROXY: median 67.5 h, p85 291.9 h (n=5 branches, 2026-01-19 to 2026-02-02). Assumes the next main push is the merge; branches `fix/notification-filter` and `fix/approval-audit` both map to push run 19, so indicative only. Not first commit → production. | `python3 scripts/baseline_metrics.py` over `ops/pipeline/run-timings.csv` (PR first run → merge-push run finished) | `gh pr list --state merged --json number,mergedAt,commits` joined by SHA to `gh api repos/{owner}/{repo}/deployments?environment=production` and their statuses | Sayantan Chakraborty (senior engineer, Invoice Approval) |
| CI pipeline duration | Successful pipeline wall time | Yes | Measured: median 31.4 min, p85 34.5 min (n=18 successful runs of 20, 2026-01-19 to 2026-02-02) | Same script; the sum of step durations per run | GitHub Actions run timings: `gh run list --workflow ci.yml --json databaseId,createdAt,updatedAt,conclusion` | Sayantan Chakraborty (senior engineer, Invoice Approval) |
| Change failure rate | Production deploys causing an incident, rollback or hotfix ÷ production deploys | No | n/a | Not derivable: no deploy or incident data. CI failure rate (10.0%, 2/20 runs; PR 16.7%, push to main 0.0%; measured, same window) is reported separately and is NOT this metric. | Production deployments (above) joined to incidents tagged `caused-by-change`, plus revert commits on main | Sayantan Chakraborty (senior engineer, Invoice Approval) |
| Review turnaround | PR opened → first review submitted | No | n/a | Not derivable: no PR review data (ASSUMPTIONS.md, A6) | `gh pr list --state merged --limit 500 --json number,createdAt,reviews`, first `reviews[].submittedAt` − `createdAt` | Sayantan Chakraborty (senior engineer, Invoice Approval) |

Evidence: `evidence/baseline-numbers.md` and `.json`, plus the independent cross-check of two numbers (log id `20261028T152600Z-task-5-risk-measurement-baseline-numbers`).
