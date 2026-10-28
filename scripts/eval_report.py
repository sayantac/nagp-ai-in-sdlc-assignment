#!/usr/bin/env python3
"""Turn scored eval CSVs into the results table and the confidence statement.

  python3 scripts/eval_report.py baseline with-agents-md

The first label is the baseline and the second is the changed-variable run.
Writes submission/04-evals/results.md.

Definitions (ops/evals/README.md):
  caught rate      = caught / defect cases
  missed rate      = missed / defect cases
  false alarm rate = false alarms / clean cases
Comparison is per case. Each case gets its majority verdict over its runs, and
the cases whose majority changed are counted, with an exact two-sided sign test.
"""
import csv
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "submission" / "04-evals"
GOOD = {"caught", "clean_ok"}


def load(label):
    with (EVALS / "results" / f"results-{label}.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    unscored = [r for r in rows if not r["verdict"]]
    if unscored:
        sys.exit(f"{label}: {len(unscored)} rows unscored. Run score_evals.py {label} first.")
    return rows


def wilson(successes, total, z=1.96):
    if total == 0:
        return (float("nan"), float("nan"))
    p = successes / total
    centre = (p + z * z / (2 * total)) / (1 + z * z / total)
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return max(0.0, centre - half), min(1.0, centre + half)


def sign_test(improved, worsened):
    n = improved + worsened
    if n == 0:
        return 1.0
    k = min(improved, worsened)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def per_run(rows):
    table = defaultdict(Counter)
    for row in rows:
        table[int(row["run"])][row["verdict"]] += 1
    return dict(sorted(table.items()))


def majority(rows):
    votes = defaultdict(Counter)
    for row in rows:
        votes[row["case"]][row["verdict"] in GOOD] += 1
    return {case: counts[True] > counts[False] for case, counts in votes.items()}, votes


def pct(numerator, denominator):
    return f"{numerator}/{denominator} ({100 * numerator / denominator:.0f}%)" if denominator else "n/a"


def describe(label, rows):
    lines = [f"### {label}", "",
             f"model `{rows[0]['model']}`, prompt `{rows[0]['prompt_version']}`, context `{rows[0]['context']}`", "",
             "| Run | Caught | Missed | False alarm | Clean correctly passed |",
             "|---|---|---|---|---|"]
    caught_rates = []
    for run, counts in per_run(rows).items():
        defects = counts["caught"] + counts["missed"]
        cleans = counts["false_alarm"] + counts["clean_ok"]
        lines.append(f"| {run} | {pct(counts['caught'], defects)} | {pct(counts['missed'], defects)} | "
                     f"{pct(counts['false_alarm'], cleans)} | {pct(counts['clean_ok'], cleans)} |")
        if defects:
            caught_rates.append(counts["caught"] / defects)
    totals = Counter(row["verdict"] for row in rows)
    defects = totals["caught"] + totals["missed"]
    cleans = totals["false_alarm"] + totals["clean_ok"]
    low, high = wilson(totals["caught"], defects)
    lines.append(f"| **all** | {pct(totals['caught'], defects)} | {pct(totals['missed'], defects)} | "
                 f"{pct(totals['false_alarm'], cleans)} | {pct(totals['clean_ok'], cleans)} |")
    spread = (max(caught_rates) - min(caught_rates)) * 100 if caught_rates else 0
    lines += ["", f"- Run-to-run spread in caught rate: {spread:.0f} percentage points.",
              f"- 95% Wilson interval on the pooled caught rate: {100*low:.0f}%-{100*high:.0f}% "
              "(optimistic, because repeated runs of the same case are not independent).", ""]
    return lines


def main():
    labels = sys.argv[1:]
    if not labels:
        sys.exit("usage: eval_report.py <baseline-label> [changed-label]")
    data = {label: load(label) for label in labels}
    out = [f"# Review eval results", "",
           f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by scripts/eval_report.py "
           f"from submission/04-evals/results/*.csv. Scored by hand against answer-key.csv._", ""]
    for label, rows in data.items():
        out += describe(label, rows)

    out += ["## Per-case verdicts (good verdicts / runs)", "",
            "| Case | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
    majorities = {label: majority(rows) for label, rows in data.items()}
    for case in sorted({row["case"] for rows in data.values() for row in rows}):
        cells = []
        for label in labels:
            verdicts = [row["verdict"] for row in data[label] if row["case"] == case]
            cells.append(f"{sum(v in GOOD for v in verdicts)}/{len(verdicts)} " +
                         ",".join(sorted(set(verdicts))))
        out.append(f"| {case} | " + " | ".join(cells) + " |")
    out.append("")

    if len(labels) == 2:
        base, changed = (majorities[label][0] for label in labels)
        improved = [c for c in base if c in changed and not base[c] and changed[c]]
        worsened = [c for c in base if c in changed and base[c] and not changed[c]]
        p_value = sign_test(len(improved), len(worsened))
        out += ["## Did the change help?", "",
                f"- Cases whose majority verdict improved: {len(improved)} {improved}",
                f"- Cases whose majority verdict got worse: {len(worsened)} {worsened}",
                f"- Exact two-sided sign test on those {len(improved) + len(worsened)} discordant cases: "
                f"p = {p_value:.3f}",
                f"- With {len(base)} cases, even a perfectly one-sided result needs at least 6 discordant cases "
                "to reach p < 0.05. Treat anything less as directional.", "",
                "**Verdict (write this yourself):** improvement / no detectable change / regression, "
                "and how confident you are, in one or two sentences.", ""]
    (EVALS / "results.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
