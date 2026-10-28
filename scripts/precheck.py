#!/usr/bin/env python3
"""Pre-submission check. Run from the repo root:  python3 scripts/precheck.py

Each check prints PASS, WARN or FAIL. Exits 1 if anything FAILs.
"""
import csv
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUB = ROOT / "submission"
results = []


def record(level, name, detail=""):
    results.append((level, name, detail))


def when(text):
    """Parse an ISO-8601 time with Z or an offset (git uses the committer's local offset)."""
    return datetime.fromisoformat(text.strip().replace("Z", "+00:00"))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def first_commit_time_where(path, predicate):
    """Commit time of the oldest commit in which the file at `path` satisfies predicate(text)."""
    for sha in reversed(git("log", "--format=%H", "--", str(path)).splitlines()):
        text = git("show", f"{sha}:{path}")
        if predicate(text):
            return git("show", "-s", "--format=%cI", sha), sha[:7]
    return None, None


def check_files():
    required = ["01-architecture/as-built-container.mmd", "01-architecture/as-built-sequence.mmd",
                "01-architecture/target-container.mmd", "01-architecture/target-sequence.mmd",
                "01-architecture/citations.md", "01-architecture/inferred.md", "01-architecture/RUN.md",
                "01-architecture/evidence/arch-test-2-red-violation.txt",
                "01-architecture/evidence/arch-test-3-green-after.txt",
                "02-adr/ADR-001-exactly-once-payex.md", "03-autonomy/autonomy-policy.md",
                "03-autonomy/first-response-scores.md", "04-evals/results.md", "04-evals/answer-key.csv",
                "05-risk/trifecta-audit.md", "05-risk/measurement-plan.md",
                "05-risk/evidence/baseline-numbers.md"]
    missing = [p for p in required if not (SUB / p).exists()]
    for case in ("case-11", "case-12"):
        if not (ROOT / "ops" / "evals" / "cases" / f"{case}.diff").exists():
            missing.append(f"ops/evals/cases/{case}.diff")
    record("FAIL" if missing else "PASS", "required hand-in files", ", ".join(missing))


def check_todos():
    hits = []
    for path in list(SUB.rglob("*.md")) + list(SUB.rglob("*.csv")) + [ROOT / "ai-logs" / "ai-log.jsonl"]:
        if path.exists() and "work" not in path.parts:
            count = len(re.findall(r"\bTODO\b", path.read_text(encoding="utf-8", errors="replace")))
            if count:
                hits.append(f"{path.relative_to(ROOT)}({count})")
    record("WARN" if hits else "PASS", "no TODO markers left", " ".join(hits))


def check_citations():
    out = subprocess.run(["python3", "scripts/verify_citations.py", "--target"], cwd=ROOT,
                         capture_output=True, text=True)
    record("PASS" if out.returncode == 0 else "FAIL", "citations resolve (as-built + target)",
           out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr[-200:])


def check_answer_key_first():
    key_path = "submission/04-evals/answer-key.csv"

    def complete(text):
        rows = list(csv.DictReader(text.splitlines()))
        return bool(rows) and all(row.get("expected") in ("defect", "clean") for row in rows)

    key_time, sha = first_commit_time_where(key_path, complete)
    starts = []
    for raw in (SUB / "04-evals" / "results").glob("*/raw/*.json"):
        try:
            starts.append(json.loads(raw.read_text(encoding="utf-8"))["started"])
        except Exception:
            pass
    if not key_time:
        record("FAIL", "answer key complete and committed", "no commit with every 'expected' filled")
    elif not starts:
        record("WARN", "answer key committed before eval runs", f"key {sha} at {key_time}; no runs yet")
    else:
        first_run = min(starts)
        ok = when(key_time) < when(first_run)
        record("PASS" if ok else "FAIL", "answer key committed before first eval run",
               f"key {sha} {key_time} vs first run {first_run}")


def check_eval_scored():
    csvs = list((SUB / "04-evals" / "results").glob("results-*.csv"))
    unscored = 0
    for path in csvs:
        with path.open(newline="", encoding="utf-8") as handle:
            unscored += sum(1 for row in csv.DictReader(handle) if not row["verdict"])
    level = "FAIL" if len(csvs) < 2 or unscored else "PASS"
    record(level, "two eval labels, fully scored", f"{len(csvs)} labels, {unscored} unscored rows")


def check_human_first():
    problems = []
    for incident in ("INC-2041", "INC-2047"):
        notes = f"submission/03-autonomy/work/{incident}-human-notes.md"
        summary = f"submission/03-autonomy/work/{incident}-ai-summary.md"
        notes_time = git("log", "--diff-filter=A", "--format=%cI", "--", notes)
        summary_time = git("log", "--diff-filter=A", "--format=%cI", "--", summary)
        if not notes_time or not summary_time:
            problems.append(f"{incident}: missing")
        elif when(notes_time.splitlines()[-1]) >= when(summary_time.splitlines()[-1]):
            problems.append(f"{incident}: AI summary committed before human notes")
    record("FAIL" if problems else "PASS", "human incident notes committed before AI summaries", "; ".join(problems))


def check_adr():
    text = (SUB / "02-adr" / "ADR-001-exactly-once-payex.md").read_text(encoding="utf-8")
    section = text.split("## Where the agent was wrong or useless")[-1]
    rows = [l for l in section.splitlines() if l.startswith("|") and not l.startswith("|---") and "What the agent said" not in l]
    record("PASS" if len(rows) >= 2 else "WARN", "ADR 'Where the agent was wrong' has specifics", f"{len(rows)} rows")


def check_logs():
    logs = ROOT / "ai-logs"
    subprocess.run(["python3", "scripts/normalize_logs.py"], cwd=ROOT, capture_output=True)
    raw = (logs / "raw.jsonl").read_text(encoding="utf-8").splitlines() if (logs / "raw.jsonl").exists() else []
    curated = [json.loads(l) for l in (logs / "ai-log.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    reviewed = [e for e in curated if e.get("human_decision") and "TODO" not in str(e.get("human_decision"))]
    transcripts = list((logs / "transcripts").glob("*"))
    record("PASS" if len(raw) > 50 else "FAIL", "automatic hook log populated", f"{len(raw)} raw events")
    record("PASS" if len(reviewed) >= 10 else "WARN", "curated entries with human decisions", f"{len(reviewed)}/{len(curated)}")
    record("PASS" if transcripts else "WARN", "session transcripts exported", f"{len(transcripts)} files")
    trailers = git("log", "--format=%B").count("AI-Log-Id:")
    record("PASS" if trailers else "WARN", "commits carry AI-Log-Id trailers", f"{trailers} commits")


def check_video():
    text = (SUB / "README.md").read_text(encoding="utf-8")
    line = next((l for l in text.splitlines() if l.startswith("**Author:**")), "")
    record("PASS" if "http" in line else "FAIL", "video link in submission/README.md")


for check in (check_files, check_todos, check_citations, check_answer_key_first, check_eval_scored,
              check_human_first, check_adr, check_logs, check_video):
    try:
        check()
    except Exception as error:
        record("FAIL", check.__name__, repr(error))

for level, name, detail in results:
    print(f"[{level:4}] {name}" + (f"  -- {detail}" if detail else ""))
raise SystemExit(1 if any(level == "FAIL" for level, _, _ in results) else 0)
