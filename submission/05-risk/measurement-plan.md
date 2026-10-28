# Baseline measurement plan

Capture before the on-call rotation starts. Report the median and p85, the time window and n. Never report a mean alone.

| Metric | Definition | Captured today | Value | Source and query today | Production source once live | Owner |
|---|---|---|---|---|---|---|
| Lead time for changes | First commit → running in production | Proxy | TODO | `python3 scripts/baseline_metrics.py` over `ops/pipeline/run-timings.csv` (PR first run → merge-push run finished) | `gh pr list --state merged --json number,mergedAt,commits` joined by SHA to `gh api repos/{owner}/{repo}/deployments?environment=production` and their statuses | TODO |
| CI pipeline duration | Successful pipeline wall time | Yes | TODO | Same script; the sum of step durations per run | GitHub Actions run timings: `gh run list --workflow ci.yml --json databaseId,createdAt,updatedAt,conclusion` | TODO |
| Change failure rate | Production deploys causing an incident, rollback or hotfix ÷ production deploys | No | n/a | Not derivable: no deploy or incident data. CI failure rate (TODO%) is reported separately and is NOT this metric. | Production deployments (above) joined to incidents tagged `caused-by-change`, plus revert commits on main | TODO |
| Review turnaround | PR opened → first review submitted | No | n/a | Not derivable: no PR review data (ASSUMPTIONS.md, A6) | `gh pr list --state merged --limit 500 --json number,createdAt,reviews`, first `reviews[].submittedAt` − `createdAt` | TODO |

Evidence: `evidence/baseline-numbers.md` and `.json`, plus the independent cross-check of two numbers (log id TODO).
