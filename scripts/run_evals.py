#!/usr/bin/env python3
"""Run the review eval headlessly with Claude Code, one fresh session per case.

Follows ops/evals/README.md: each call gets only the review prompt and the case
diff. No tools, no MCP servers, and (in --context none) no project context file.

  python3 scripts/run_evals.py --label baseline       --context none --model <model-id>
  python3 scripts/run_evals.py --label with-agents-md --context repo --model <same model-id>

--context none : runs from an empty temp directory, so no CLAUDE.md/AGENTS.md is loaded
--context repo : runs from the repo root, so CLAUDE.md -> AGENTS.md is loaded
                 (this is the single changed variable)

Outputs:
  submission/04-evals/results/<label>/raw/run<r>-<case>.json   (full Claude Code JSON output)
  submission/04-evals/results/results-<label>.csv              (rows to score with score_evals.py)
Already-completed calls are skipped, so you can safely re-run after an interruption.
"""
import argparse
import csv
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "ops" / "evals" / "cases"
EVALS = ROOT / "submission" / "04-evals"
NO_TOOLS = ["Bash", "Edit", "Write", "MultiEdit", "Read", "Glob", "Grep", "LS", "WebFetch",
            "WebSearch", "Task", "NotebookEdit", "NotebookRead", "TodoWrite"]
FIELDS = ["run", "case", "model", "prompt_version", "context", "verdict", "finding_summary",
          "confidence_reported", "notes", "raw_file"]


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--context", choices=["none", "repo"], required=True)
    parser.add_argument("--model", required=True, help="exact model id, keep identical across labels")
    parser.add_argument("--prompt-version", default="v1")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--allow-user-claude-md", action="store_true")
    args = parser.parse_args()

    user_memory = Path.home() / ".claude" / "CLAUDE.md"
    if user_memory.exists() and user_memory.read_text(encoding="utf-8").strip() and not args.allow_user_claude_md:
        sys.exit(f"{user_memory} exists and is not empty. It would be loaded into every eval call and "
                 "contaminate the baseline. Move it aside for the eval, or pass --allow-user-claude-md "
                 "and record that in eval-protocol.md.")

    prompt = (EVALS / "prompts" / f"review-{args.prompt_version}.md").read_text(encoding="utf-8").strip()
    cases = sorted(CASES.glob("case-*.diff"))
    raw_dir = EVALS / "results" / args.label / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_path = EVALS / "results" / f"results-{args.label}.csv"
    existing = {}
    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8") as handle:
            existing = {(row["run"], row["case"]): row for row in csv.DictReader(handle)}

    empty_dir = tempfile.mkdtemp(prefix="eval-")
    cwd = ROOT if args.context == "repo" else Path(empty_dir)
    log_path = ROOT / "ai-logs" / "raw.jsonl"
    print(f"{len(cases)} cases x {args.runs} runs, context={args.context}, model={args.model}, cwd={cwd}")

    for run_number in range(1, args.runs + 1):
        for case_path in cases:
            case = case_path.stem
            raw_file = raw_dir / f"run{run_number}-{case}.json"
            if not raw_file.exists():
                started = utc()
                t0 = time.time()
                command = ["claude", "-p", prompt, "--disallowedTools", *NO_TOOLS,
                           "--strict-mcp-config", "--output-format", "json", "--model", args.model]
                result = subprocess.run(command, cwd=cwd, input=case_path.read_text(encoding="utf-8"),
                                        capture_output=True, text=True)
                try:
                    output = json.loads(result.stdout)
                except json.JSONDecodeError:
                    output = {"parse_error": True, "stdout": result.stdout, "stderr": result.stderr}
                record = {"label": args.label, "run": run_number, "case": case, "context": args.context,
                          "model_requested": args.model, "prompt_version": args.prompt_version,
                          "started": started, "wall_seconds": round(time.time() - t0, 1),
                          "exit_code": result.returncode, "cwd_mode": args.context, "output": output}
                raw_file.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
                log_path.parent.mkdir(exist_ok=True)
                with log_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"ts": started, "event": "EvalRun", "label": args.label,
                                             "run": run_number, "case": case, "context": args.context,
                                             "model": args.model, "exit_code": result.returncode,
                                             "session_id": output.get("session_id"),
                                             "raw_file": str(raw_file.relative_to(ROOT))}) + "\n")
                status = "ok" if result.returncode == 0 and not output.get("parse_error") else "ERROR"
                print(f"run {run_number} {case}: {status} ({record['wall_seconds']}s)")
            key = (str(run_number), case)
            if key not in existing:
                existing[key] = {"run": run_number, "case": case, "model": args.model,
                                 "prompt_version": args.prompt_version, "context": args.context,
                                 "verdict": "", "finding_summary": "", "confidence_reported": "",
                                 "notes": "", "raw_file": str(raw_file.relative_to(ROOT))}
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                for row_key in sorted(existing, key=lambda k: (int(k[0]), k[1])):
                    writer.writerow({field: existing[row_key].get(field, "") for field in FIELDS})
    print(f"Done. Score with: python3 scripts/score_evals.py {args.label}")


if __name__ == "__main__":
    main()
