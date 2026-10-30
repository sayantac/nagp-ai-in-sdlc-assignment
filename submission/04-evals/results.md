# Review eval results

_Generated 2026-10-30 15:35 UTC by scripts/eval_report.py from submission/04-evals/results/*.csv. Scored by hand against answer-key.csv._

### baseline

model `claude-sonnet-5-5`, prompt `v1`, context `none`

| Run | Caught | Missed | False alarm | Clean correctly passed |
|---|---|---|---|---|
| 1 | 9/9 (100%) | 0/9 (0%) | 0/3 (0%) | 3/3 (100%) |
| 2 | 9/9 (100%) | 0/9 (0%) | 0/3 (0%) | 3/3 (100%) |
| 3 | 9/9 (100%) | 0/9 (0%) | 0/3 (0%) | 3/3 (100%) |
| **all** | 27/27 (100%) | 0/27 (0%) | 0/9 (0%) | 9/9 (100%) |

- Run-to-run spread in caught rate: 0 percentage points.
- 95% Wilson interval on the pooled caught rate: 88%-100% (optimistic, because repeated runs of the same case are not independent).

### with-agents-md

model `claude-sonnet-5-5`, prompt `v1`, context `repo`

| Run | Caught | Missed | False alarm | Clean correctly passed |
|---|---|---|---|---|
| 1 | 9/9 (100%) | 0/9 (0%) | 0/3 (0%) | 3/3 (100%) |
| 2 | 9/9 (100%) | 0/9 (0%) | 0/3 (0%) | 3/3 (100%) |
| 3 | 9/9 (100%) | 0/9 (0%) | 0/3 (0%) | 3/3 (100%) |
| **all** | 27/27 (100%) | 0/27 (0%) | 0/9 (0%) | 9/9 (100%) |

- Run-to-run spread in caught rate: 0 percentage points.
- 95% Wilson interval on the pooled caught rate: 88%-100% (optimistic, because repeated runs of the same case are not independent).

## Per-case verdicts (good verdicts / runs)

| Case | baseline | with-agents-md |
|---|---|---|
| case-01 | 3/3 caught | 3/3 caught |
| case-02 | 3/3 caught | 3/3 caught |
| case-03 | 3/3 caught | 3/3 caught |
| case-04 | 3/3 clean_ok | 3/3 clean_ok |
| case-05 | 3/3 caught | 3/3 caught |
| case-06 | 3/3 clean_ok | 3/3 clean_ok |
| case-07 | 3/3 caught | 3/3 caught |
| case-08 | 3/3 caught | 3/3 caught |
| case-09 | 3/3 caught | 3/3 caught |
| case-10 | 3/3 caught | 3/3 caught |
| case-11 | 3/3 caught | 3/3 caught |
| case-12 | 3/3 clean_ok | 3/3 clean_ok |

## Did the change help?

- Cases whose majority verdict improved: 0 []
- Cases whose majority verdict got worse: 0 []
- Exact two-sided sign test on those 0 discordant cases: p = 1.000
- With 12 cases, even a perfectly one-sided result needs at least 6 discordant cases to reach p < 0.05. Treat anything less as directional.

**Verdict:** No detectable change. Both configurations caught 27/27 defect reviews and passed 9/9 clean reviews, with no run-to-run spread, so no case changed verdict. I am moderately confident the context file made no difference to what this set measures, and not confident it makes no difference in general: every case is a single, visible defect, so the set is at its ceiling and cannot show improvement. The only difference I saw is qualitative: with AGENTS.md loaded, reviews added repo-rule findings (for example "logic belongs in Domain", "tests required") that did not change any verdict. With 12 cases, even a clear effect would need at least 6 changed cases to reach p < 0.05. Limitation: the answer key was drafted with AI assistance and cross-checked by the same model family, so shared blind spots are possible. A discriminating test needs subtler, repo-specific defects.
