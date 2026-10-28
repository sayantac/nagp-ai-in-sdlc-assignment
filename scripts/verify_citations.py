#!/usr/bin/env python3
"""Check that every element in the as-built diagrams has a citation that resolves.

Element IDs: C# (container/component), A# (actor/external), E# (edge),
S# (sequence step). Rules:
  1. Every ID used in submission/01-architecture/as-built-*.mmd has a row in citations.md.
  2. Every cited path exists in the repository.
  3. Every part of the cited symbol (e.g. ApprovalService.Approve) appears as a whole word in that file.
  4. Every row in the as-built section is used by a diagram (no orphan citations).
With --target, target-*.mmd files are checked against all sections too.

Writes the report to submission/01-architecture/evidence/citation-check.txt and
exits 1 on any failure.
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCH = ROOT / "submission" / "01-architecture"
ID_PATTERN = re.compile(r"\b([CAES]\d{1,3})\b")


def parse_citations(path):
    rows, section, header = [], "as-built", None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            section = "target" if "target" in line.lower() else "as-built"
            header = None
            continue
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= set("-: ") for cell in cells):
            continue
        if header is None:
            header = [cell.lower() for cell in cells]
            continue
        row = dict(zip(header, cells))
        if row.get("id") and ID_PATTERN.fullmatch(row["id"]):
            row["section"] = section
            rows.append(row)
    return rows


def ids_in(mmd_path):
    found = set()
    for line in mmd_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(("%%", "classDef", "class ", "style ", "linkStyle")):
            continue
        found.update(ID_PATTERN.findall(stripped))
    return found


def main():
    include_target = "--target" in sys.argv
    citations_file = ARCH / "citations.md"
    rows = parse_citations(citations_file)
    by_id = {row["id"]: row for row in rows}
    patterns = ["as-built-*.mmd"] + (["target-*.mmd"] if include_target else [])
    diagrams = [path for pattern in patterns for path in sorted(ARCH.glob(pattern))]
    failures, lines = [], []

    if not diagrams:
        failures.append("No diagrams found in submission/01-architecture/")
    used = set()
    for diagram in diagrams:
        diagram_ids = ids_in(diagram)
        used |= diagram_ids
        for element_id in sorted(diagram_ids, key=lambda value: (value[0], int(value[1:]))):
            if element_id not in by_id:
                failures.append(f"{diagram.name}: {element_id} has no row in citations.md")

    for row in rows:
        if row["section"] == "target" and not include_target:
            continue
        path_text = row.get("path", "").strip("` ")
        symbol = row.get("symbol", "").strip("` ")
        target = ROOT / path_text
        if not path_text or not target.exists():
            failures.append(f"{row['id']}: path '{path_text}' does not exist")
            continue
        if symbol and symbol not in ("-", "—", "n/a"):
            text = target.read_text(encoding="utf-8", errors="replace") if target.is_file() else ""
            for part in re.split(r"[^\w]+", symbol):
                if part and not re.search(rf"\b{re.escape(part)}\b", text):
                    failures.append(f"{row['id']}: symbol part '{part}' not found in {path_text}")
        if row["section"] == "as-built" and row["id"] not in used:
            failures.append(f"{row['id']}: cited but not used in any as-built diagram")
        lines.append(f"ok-checked {row['id']:5} {path_text} :: {symbol}")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = [f"# citation check {stamp}", f"# diagrams: {', '.join(d.name for d in diagrams)}",
              f"# rows: {len(rows)}  ids used: {len(used)}  failures: {len(failures)}", ""]
    report += [f"FAIL {failure}" for failure in failures] + lines
    (ARCH / "evidence").mkdir(parents=True, exist_ok=True)
    (ARCH / "evidence" / "citation-check.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[:3] + [f"FAIL {failure}" for failure in failures]))
    print("RESULT:", "PASS" if not failures else "FAIL")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
