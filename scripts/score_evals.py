#!/usr/bin/env python3
"""Interactive, strict scoring of eval results against YOUR answer key.

  python3 scripts/score_evals.py baseline

For each unscored row: shows the answer key for the case, then the review the
agent produced, then asks for a verdict. Saves after every row, so you can quit
and resume. Scoring rule (ops/evals/README.md): "caught" only if the review
names the actual defect for the right reason. Style notes on a clean case are
not false alarms.
"""
import csv
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "submission" / "04-evals"
DEFECT_CHOICES = {"c": "caught", "m": "missed", "w": "missed"}
CLEAN_CHOICES = {"k": "clean_ok", "f": "false_alarm"}


def load_key():
    with (EVALS / "answer-key.csv").open(newline="", encoding="utf-8") as handle:
        key = {row["case"]: row for row in csv.DictReader(handle)}
    blank = [case for case, row in key.items() if row["expected"] not in ("defect", "clean")]
    if blank:
        sys.exit(f"answer-key.csv has no expected value (defect|clean) for: {', '.join(blank)}")
    return key


def review_text(raw_file):
    record = json.loads((ROOT / raw_file).read_text(encoding="utf-8"))
    output = record.get("output", {})
    return output.get("result") or output.get("stdout") or json.dumps(output)[:3000]


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: score_evals.py <label>")
    csv_path = EVALS / "results" / f"results-{sys.argv[1]}.csv"
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    key = load_key()
    todo = [row for row in rows if not row["verdict"]]
    print(f"{len(todo)} of {len(rows)} rows to score in {csv_path.name}\n")
    for row in todo:
        case_key = key[row["case"]]
        expected = case_key["expected"]
        print("=" * 100)
        print(f"RUN {row['run']}  {row['case']}   expected: {expected.upper()}")
        if expected == "defect":
            print("defect: " + case_key.get("defect_description", ""))
        print("-" * 100)
        print(textwrap.indent(review_text(row["raw_file"]), "  "))
        print("-" * 100)
        choices = DEFECT_CHOICES if expected == "defect" else CLEAN_CHOICES
        prompt = ("[c]aught  [m]issed  [w]right area but wrong reason (=missed)" if expected == "defect"
                  else "[k] clean, no defect asserted   [f]alse alarm (asserted a defect that is not there)")
        answer = ""
        while answer not in choices and answer != "q":
            answer = input(f"{prompt}  [q]uit > ").strip().lower()
        if answer == "q":
            break
        row["verdict"] = choices[answer]
        row["finding_summary"] = input("finding summary (one line, enter to skip) > ").strip()
        row["confidence_reported"] = input("confidence the review reported [h/m/l/none] > ").strip()
        note = input("notes (enter to skip) > ").strip()
        row["notes"] = ("wrong reason; " if answer == "w" else "") + note
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    remaining = sum(1 for row in rows if not row["verdict"])
    print(f"\nSaved. {remaining} rows still unscored.")


if __name__ == "__main__":
    main()
