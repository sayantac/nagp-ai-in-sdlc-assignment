#!/usr/bin/env python3
"""Prove the architecture test bites: green -> inject violation -> red -> revert -> green.

Writes three output files and the violation diff to
submission/01-architecture/evidence/. Always reverts the violation, even on
error. Run from the repository root:  python3 scripts/demo_arch_test.py
"""
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "submission" / "01-architecture" / "evidence"
DOMAIN_DIR = ROOT / "backend" / "src" / "InvoiceApp.Domain"
CSPROJ = DOMAIN_DIR / "InvoiceApp.Domain.csproj"
VIOLATION_FILE = DOMAIN_DIR / "ArchViolationDemo.cs"
TEST_CMD = ["dotnet", "test", "backend/InvoiceApp.sln", "--filter", "Category=Architecture",
            "--logger", "console;verbosity=normal"]

VIOLATION_SOURCE = """using Microsoft.AspNetCore.Http;

namespace InvoiceApp.Domain;

// DELIBERATE VIOLATION for the architecture-test demo. Removed automatically.
public static class ArchViolationDemo
{
    public static IResult Approved() => Results.Ok();
}
"""
FRAMEWORK_REFERENCE = """  <ItemGroup>
    <FrameworkReference Include="Microsoft.AspNetCore.App" />
  </ItemGroup>
</Project>"""


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def run_tests(label):
    head = run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = run(TEST_CMD)
    path = EVIDENCE / f"arch-test-{label}.txt"
    path.write_text(
        f"# {label}\n# started: {started}\n# git HEAD: {head}\n# command: {' '.join(TEST_CMD)}\n"
        f"# exit code: {result.returncode}\n\n{result.stdout}\n{result.stderr}",
        encoding="utf-8")
    return result.returncode, path


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if run(["git", "status", "--porcelain", "--", str(DOMAIN_DIR)]).stdout.strip():
        sys.exit("Domain project has uncommitted changes. Commit or stash them first.")

    original_csproj = CSPROJ.read_text(encoding="utf-8")
    outcomes = []
    code, path = run_tests("1-green-before")
    outcomes.append(("before violation", code, 0, path))
    try:
        CSPROJ.write_text(original_csproj.replace("</Project>", FRAMEWORK_REFERENCE), encoding="utf-8")
        VIOLATION_FILE.write_text(VIOLATION_SOURCE, encoding="utf-8")
        run(["git", "add", "-N", str(VIOLATION_FILE)])
        diff = run(["git", "diff", "--", str(DOMAIN_DIR)]).stdout
        (EVIDENCE / "arch-violation.diff").write_text(diff, encoding="utf-8")
        code, path = run_tests("2-red-violation")
        outcomes.append(("with violation", code, "non-zero", path))
    finally:
        run(["git", "reset", "-q", "--", str(VIOLATION_FILE)])
        VIOLATION_FILE.unlink(missing_ok=True)
        CSPROJ.write_text(original_csproj, encoding="utf-8")
    code, path = run_tests("3-green-after")
    outcomes.append(("after revert", code, 0, path))

    ok = outcomes[0][1] == 0 and outcomes[1][1] != 0 and outcomes[2][1] == 0
    for name, got, expected, file_path in outcomes:
        print(f"{name:18} exit={got:<3} expected={expected:<9} -> {file_path.relative_to(ROOT)}")
    red_text = outcomes[1][3].read_text(encoding="utf-8")
    if outcomes[1][1] != 0 and "Microsoft.AspNetCore" not in red_text:
        print("WARNING: the red run failed, but not visibly because of the rule. "
              "Open the file and check it is the architecture test failing, not the build.")
    print("RESULT:", "PASS - the test bites" if ok else "UNEXPECTED - inspect the evidence files")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
