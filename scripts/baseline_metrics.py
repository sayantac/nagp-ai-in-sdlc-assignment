#!/usr/bin/env python3
"""Baseline numbers that can be captured today from the CI history.

Source: ops/pipeline/run-timings.csv. One row per step per run, with columns
run_number, started_at, branch, event, conclusion, step, duration_seconds.
The repository's own git history (6 bulk-import commits) and its PR history
(none) are NOT usable for lead time or review turnaround.

Computed:
  1. CI outcome rate: successful runs / all runs, split by PR and main push.
     This is NOT change failure rate, which needs production deploy and incident data.
  2. Pipeline duration: the sum of step durations per run (single sequential job), with
     median and p85 by the nearest-rank method. This is the CI portion of lead time.
  3. Lead-time proxy, PR to main: for each branch, from its first PR run start to
     the start of the first main push run after its last successful PR run. This
     ASSUMES the next push to main is that branch's merge, which is unverifiable here.
  4. Push-to-main frequency per week: a proxy for deployment frequency.

Writes submission/05-risk/evidence/baseline-numbers.md and .json.
"""
import csv
import json
import math
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "ops" / "pipeline" / "run-timings.csv"
OUT = ROOT / "submission" / "05-risk" / "evidence"


def parse_time(text):
    return datetime.strptime(text.strip(), "%Y-%m-%dT%H:%M:%SZ")


def nearest_rank(values, percentile):
    ordered = sorted(values)
    if not ordered:
        return None
    rank = max(1, math.ceil(percentile / 100 * len(ordered)))
    return ordered[rank - 1]


def load_runs():
    runs = OrderedDict()
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            row = {key.strip(): (value or "").strip() for key, value in row.items()}
            number = int(row["run_number"])
            run = runs.setdefault(number, {
                "run": number, "started_at": parse_time(row["started_at"]), "branch": row["branch"],
                "event": row["event"], "conclusion": row["conclusion"], "steps": []})
            run["steps"].append((row["step"], int(row["duration_seconds"])))
    for run in runs.values():
        run["duration_s"] = sum(seconds for _, seconds in run["steps"])
        run["last_step"] = run["steps"][-1][0]
    return list(runs.values())


def outcome_rates(runs):
    result = {}
    for name, subset in (("all", runs), ("pull_request", [r for r in runs if r["event"] == "pull_request"]),
                         ("push_to_main", [r for r in runs if r["event"] == "push"])):
        success = sum(r["conclusion"] == "success" for r in subset)
        result[name] = {"success": success, "total": len(subset),
                        "failure_rate_pct": round(100 * (len(subset) - success) / len(subset), 1) if subset else None}
    return result


def durations(runs):
    minutes = [r["duration_s"] / 60 for r in runs if r["conclusion"] == "success"]
    return {"n_successful_runs": len(minutes), "median_min": round(nearest_rank(minutes, 50), 1),
            "p85_min": round(nearest_rank(minutes, 85), 1), "min_min": round(min(minutes), 1),
            "max_min": round(max(minutes), 1)}


def lead_time_proxy(runs):
    by_branch = defaultdict(list)
    for run in runs:
        if run["event"] == "pull_request":
            by_branch[run["branch"]].append(run)
    pushes = sorted((r for r in runs if r["event"] == "push"), key=lambda r: r["started_at"])
    pairs = []
    for branch, branch_runs in by_branch.items():
        branch_runs.sort(key=lambda r: r["started_at"])
        green = [r for r in branch_runs if r["conclusion"] == "success"]
        if not green:
            continue
        after = [p for p in pushes if p["started_at"] > green[-1]["started_at"]]
        if not after:
            pairs.append({"branch": branch, "first_pr_run": branch_runs[0]["run"], "merge_push_run": None})
            continue
        merge = after[0]
        hours = (merge["started_at"] + timedelta(seconds=merge["duration_s"]) -
                 branch_runs[0]["started_at"]).total_seconds() / 3600
        pairs.append({"branch": branch, "first_pr_run": branch_runs[0]["run"],
                      "merge_push_run": merge["run"], "hours": round(hours, 1)})
    hours = [p["hours"] for p in pairs if p.get("hours") is not None]
    return {"pairs": pairs, "n": len(hours),
            "median_h": round(nearest_rank(hours, 50), 1) if hours else None,
            "p85_h": round(nearest_rank(hours, 85), 1) if hours else None}


def main():
    runs = load_runs()
    window = (min(r["started_at"] for r in runs), max(r["started_at"] for r in runs))
    weeks = max(1.0, (window[1] - window[0]).total_seconds() / (7 * 86400))
    pushes = sum(r["event"] == "push" for r in runs)
    data = {"source": str(SOURCE.relative_to(ROOT)), "runs": len(runs),
            "window": [window[0].isoformat() + "Z", window[1].isoformat() + "Z"],
            "ci_outcomes": outcome_rates(runs), "pipeline_duration": durations(runs),
            "lead_time_proxy_pr_to_main": lead_time_proxy(runs),
            "push_to_main_per_week": round(pushes / weeks, 1),
            "failed_runs": [{"run": r["run"], "branch": r["branch"], "event": r["event"],
                             "last_step_recorded": r["last_step"]} for r in runs if r["conclusion"] != "success"]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "baseline-numbers.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    o, d, lt = data["ci_outcomes"], data["pipeline_duration"], data["lead_time_proxy_pr_to_main"]
    md = ["# Baseline numbers captured from CI history", "",
          f"Source: `{data['source']}`, {data['runs']} runs, {data['window'][0]} to {data['window'][1]}. "
          "Generated by `python3 scripts/baseline_metrics.py`. Percentiles use the nearest-rank method.", "",
          "| Metric | Value | Status |", "|---|---|---|",
          f"| CI pipeline duration (successful runs) | median {d['median_min']} min, p85 {d['p85_min']} min "
          f"(n={d['n_successful_runs']}, range {d['min_min']}-{d['max_min']}) | Measured. This is the CI component of lead time |",
          f"| CI failure rate, all runs | {o['all']['failure_rate_pct']}% ({o['all']['total'] - o['all']['success']}/{o['all']['total']}) | Measured. NOT change failure rate |",
          f"| CI failure rate, PR / push to main | {o['pull_request']['failure_rate_pct']}% / {o['push_to_main']['failure_rate_pct']}% | Measured |",
          f"| Lead time, first PR run to merge push finished | median {lt['median_h']} h, p85 {lt['p85_h']} h (n={lt['n']}) | PROXY: assumes the next main push is the merge |",
          f"| Push-to-main frequency | {data['push_to_main_per_week']} per week | PROXY for deployment frequency |",
          "", "## Failed runs", "", "| Run | Branch | Event | Last step recorded (not necessarily the failing step) |", "|---|---|---|---|"]
    md += [f"| {f['run']} | {f['branch']} | {f['event']} | {f['last_step_recorded']} |" for f in data["failed_runs"]]
    md += ["", "## Lead-time proxy pairs", "", "| Branch | First PR run | Merge push run | Hours |", "|---|---|---|---|"]
    md += [f"| {p['branch']} | {p['first_pr_run']} | {p['merge_push_run']} | {p.get('hours', 'n/a')} |" for p in lt["pairs"]]
    merge_runs = [p["merge_push_run"] for p in lt["pairs"] if p.get("merge_push_run")]
    shared = sorted({run for run in merge_runs if merge_runs.count(run) > 1})
    if shared:
        md += ["", f"**Proxy warning:** more than one branch maps to main push run(s) {shared}, so for "
               "those branches the merge time is ambiguous. Report the lead-time proxy as indicative only."]
    (OUT / "baseline-numbers.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
